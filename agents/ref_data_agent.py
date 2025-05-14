#!/usr/bin/env python3
"""
Reference Data Agent

This agent is responsible for loading reference data from files and updating
the Intermediate Representation (IR) with that data. It handles:

1. Loading reference data from CSV files
2. Mapping reference data to schema tables
3. Handling distribution weights for data generation
4. Updating the IR with the enriched reference data
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from agents.base import Agent
from models.ir import Schema, Table, ReferenceData
from utils.ref_data_parser import (
    parse_multi_table_csv,
    csv_to_ir,
    update_schema_with_reference_data,
    directory_to_ir
)
from utils.llm import get_provider


class RefDataAgent(Agent):
    """
    Agent responsible for loading and mapping reference data to schema tables.
    
    This agent handles loading reference data from CSV files and updating the
    Intermediate Representation (IR) with that data. It can handle both single-file
    multi-table CSV files and directories of CSV files (one per table).
    
    The agent also supports distribution weights for reference data, which can
    influence how frequently each reference value appears in generated data.
    """
    
    def __init__(self, run_id: str, artifacts_dir: str, **kwargs):
        """Initialize the RefDataAgent."""
        super().__init__(
            name="RefDataAgent",
            run_id=run_id,
            artifacts_dir=artifacts_dir,
            seed=kwargs.get("seed")
        )
        self.llm_provider = kwargs.get("llm_provider", "openai")
        self.llm_model = kwargs.get("llm_model", "gpt-4o")
        self.provider = get_provider(self.llm_provider)
        
        # Store the last LLM call info for retry logic
        self._last_prompt = None
    
    def llm_call(self, prompt: str) -> str:
        """
        Make an LLM API call.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The response from the LLM
        """
        self._last_prompt = prompt
        return self.provider.generate(
            prompt=prompt,
            temperature=0.0,  # Use deterministic output
            max_tokens=4000,
            seed=self.seed,
            model=self.llm_model
        )
    
    def retry_llm_call(self) -> Any:
        """
        Retry the last LLM API call.
        
        This method is required by the Agent base class and is called by
        handle_llm_error when there's an API error.
        
        Returns:
            Result from the LLM API call
        
        Raises:
            RuntimeError: If there's no previous LLM call to retry
        """
        if self._last_prompt is None:
            raise RuntimeError("No previous LLM call to retry")
        
        return self.llm_call(self._last_prompt)
    
    def run(self, 
            schema: Schema, 
            ref_data_path: Union[str, Path],
            intelligent_mapping: bool = True) -> Schema:
        """
        Load reference data and update the schema IR.
        
        Args:
            schema: The Schema IR to update with reference data
            ref_data_path: Path to reference data file or directory
            intelligent_mapping: Whether to use LLM for intelligent mapping
            
        Returns:
            Updated Schema IR with reference data
        """
        self.logger.info(f"Processing reference data from: {ref_data_path}")
        
        # Save the input schema for reference
        self.save_artifact("input_schema", schema.to_json(indent=2), is_json=True)
        
        # Process based on whether ref_data_path is a file or directory
        path = Path(ref_data_path)
        if path.is_file():
            # Single multi-table CSV file
            self.logger.info("Processing single multi-table CSV file")
            updated_schema = self._process_single_file(schema, path, intelligent_mapping)
        elif path.is_dir():
            # Directory of CSV files
            self.logger.info("Processing directory of CSV files")
            updated_schema = self._process_directory(schema, path, intelligent_mapping)
        else:
            self.logger.error(f"Reference data path does not exist: {ref_data_path}")
            raise FileNotFoundError(f"Reference data path does not exist: {ref_data_path}")
        
        # Save the updated schema
        self.save_artifact("output_schema", updated_schema.to_json(indent=2), is_json=True)
        
        # Return the updated schema
        return updated_schema
    
    def _process_single_file(self, 
                           schema: Schema, 
                           file_path: Path,
                           intelligent_mapping: bool) -> Schema:
        """
        Process a single multi-table CSV file.
        
        Args:
            schema: The Schema IR to update
            file_path: Path to the multi-table CSV file
            intelligent_mapping: Whether to use LLM for intelligent mapping
            
        Returns:
            Updated Schema IR
        """
        if intelligent_mapping:
            # Use LLM to intelligently map reference data to schema tables
            return self._intelligent_mapping(schema, file_path)
        else:
            # Use simple mapping based on table names
            return update_schema_with_reference_data(schema, file_path)
    
    def _process_directory(self, 
                         schema: Schema, 
                         dir_path: Path,
                         intelligent_mapping: bool) -> Schema:
        """
        Process a directory of CSV files.
        
        Args:
            schema: The Schema IR to update
            dir_path: Path to the directory containing CSV files
            intelligent_mapping: Whether to use LLM for intelligent mapping
            
        Returns:
            Updated Schema IR
        """
        updated_schema = schema
        
        # Process each CSV file in the directory
        csv_files = list(dir_path.glob("*.csv"))
        self.logger.info(f"Found {len(csv_files)} CSV files in directory")
        
        for csv_file in csv_files:
            # Update schema with each file
            updated_schema = self._process_single_file(
                updated_schema, csv_file, intelligent_mapping
            )
        
        return updated_schema
    
    def _intelligent_mapping(self, 
                           schema: Schema, 
                           file_path: Path) -> Schema:
        """
        Use LLM to intelligently map reference data to schema tables.
        
        This method uses the LLM to:
        1. Understand the schema structure
        2. Parse the reference data
        3. Map reference data to the most appropriate tables
        4. Handle cases where table names don't match exactly
        
        Args:
            schema: The Schema IR to update
            file_path: Path to the reference data file
            
        Returns:
            Updated Schema IR
        """
        # First, try simple name-based mapping
        try:
            schemas_data = parse_multi_table_csv(file_path)
            simple_mapping = self._create_mapping_suggestion(schema, schemas_data)
            
            # If we have a clean mapping (every ref table maps to a schema table),
            # we can use simple mapping
            if self._is_clean_mapping(simple_mapping):
                self.logger.info("Using simple name-based mapping")
                return update_schema_with_reference_data(schema, file_path)
        except Exception as e:
            self.logger.warning(f"Error in simple mapping: {str(e)}")
        
        # If simple mapping fails or is incomplete, use LLM
        self.logger.info("Using LLM for intelligent mapping")
        
        # Read the reference data file content
        with open(file_path, 'r', encoding='utf-8') as f:
            ref_data_content = f.read()
        
        # Prepare the prompt for the LLM using externalized prompt template
        prompt_template = self.load_prompt("mapping")
        prompt = prompt_template.format(
            schema_json=schema.to_json(indent=2),
            ref_data_content=ref_data_content
        )
        
        self.save_prompt(prompt)
        
        # Call the LLM
        try:
            response = self.llm_call(prompt)
            self.save_llm_response(response, "mapping")
            
            # Parse the LLM response to get the mapping
            mapping = self._parse_mapping_response(response)
            
            # Apply the mapping to update the schema
            return self._apply_mapping(schema, file_path, mapping)
        except Exception as e:
            self.logger.error(f"Error in LLM-based mapping: {str(e)}")
            # Fall back to simple mapping
            self.logger.info("Falling back to simple mapping")
            return update_schema_with_reference_data(schema, file_path)
    
    def _create_mapping_suggestion(self, 
                                 schema: Schema, 
                                 schemas_data: Dict[str, Dict[str, List[Dict[str, str]]]]) -> Dict[str, str]:
        """
        Create a simple name-based mapping from reference data tables to schema tables.
        
        Args:
            schema: The Schema IR
            schemas_data: Parsed reference data
            
        Returns:
            Dictionary mapping reference table names to schema table names
        """
        mapping = {}
        
        # Get all schema table names
        schema_tables = {table.name.lower(): table.name for table in schema.tables}
        
        # Check each reference data table
        for schema_name, tables in schemas_data.items():
            for ref_table_name in tables.keys():
                # Try exact match
                if ref_table_name.lower() in schema_tables:
                    mapping[f"{schema_name}.{ref_table_name}"] = schema_tables[ref_table_name.lower()]
                # Try without schema qualification
                elif ref_table_name.lower() in schema_tables:
                    mapping[f"{schema_name}.{ref_table_name}"] = schema_tables[ref_table_name.lower()]
        
        return mapping
    
    def _is_clean_mapping(self, mapping: Dict[str, str]) -> bool:
        """
        Check if the mapping is clean (all reference tables map to schema tables).
        
        Args:
            mapping: Mapping from reference tables to schema tables
            
        Returns:
            True if all reference tables map to schema tables
        """
        return len(mapping) > 0 and all(v for v in mapping.values())
    
    def _prepare_mapping_prompt(self, schema: Schema, ref_data_content: str) -> str:
        """
        Prepare a prompt for the LLM to map reference data to schema tables.
        
        This method is kept for backward compatibility but now uses the externalized prompt template.
        
        Args:
            schema: The Schema IR
            ref_data_content: Content of the reference data file
            
        Returns:
            Prompt string for the LLM
        """
        prompt_template = self.load_prompt("mapping")
        return prompt_template.format(
            schema_json=schema.to_json(indent=2),
            ref_data_content=ref_data_content
        )
    
    def _parse_mapping_response(self, response: str) -> Dict[str, str]:
        """
        Parse the LLM response to extract the mapping.
        
        Args:
            response: LLM response text
            
        Returns:
            Dictionary mapping reference table names to schema table names
        """
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Extract the mapping
            if "mapping" in data:
                return data["mapping"]
            else:
                return data  # Assume the whole JSON is the mapping
        except Exception as e:
            self.logger.error(f"Error parsing mapping response: {str(e)}")
            return {}
    
    def _apply_mapping(self, 
                     schema: Schema, 
                     file_path: Path, 
                     mapping: Dict[str, str]) -> Schema:
        """
        Apply the mapping to update the schema with reference data.
        
        Args:
            schema: The Schema IR to update
            file_path: Path to the reference data file
            mapping: Mapping from reference table names to schema table names
            
        Returns:
            Updated Schema IR
        """
        if not mapping:
            # If mapping is empty, fall back to simple mapping
            return update_schema_with_reference_data(schema, file_path)
        
        # Parse the reference data file
        schemas_data = parse_multi_table_csv(file_path)
        
        # Apply the mapping
        for ref_table, schema_table in mapping.items():
            # Split ref_table into schema and table names
            parts = ref_table.split('.')
            if len(parts) == 2:
                ref_schema, ref_table_name = parts
            else:
                ref_schema = "dbo"  # Default schema
                ref_table_name = ref_table
            
            # Check if we have this table in the reference data
            if ref_schema in schemas_data and ref_table_name in schemas_data[ref_schema]:
                # Get the schema table
                table = schema.get_table(schema_table)
                
                if table:
                    # Get the reference data rows
                    rows = schemas_data[ref_schema][ref_table_name]
                    
                    # Determine if we have distribution weights
                    has_weights = any("weight" in row for row in rows)
                    
                    # If we don't have weights but it's a reference table with boolean YES/NO values,
                    # we can suggest proper weights (e.g., more "YES" than "NO")
                    if not has_weights and self._is_boolean_ref_table(rows):
                        rows = self._add_boolean_weights(rows)
                    
                    # Update the table with reference data
                    distribution_strategy = "weighted_random" if has_weights else None
                    
                    # Add reference data to the table
                    table.reference_data = ReferenceData(
                        rows=rows,
                        distribution_strategy=distribution_strategy,
                        description=f"Reference data for {schema_table}"
                    )
                    
                    self.logger.info(f"Applied reference data to table {schema_table}")
                else:
                    self.logger.warning(f"Schema table {schema_table} not found")
            else:
                self.logger.warning(f"Reference table {ref_table} not found in data")
        
        return schema
    
    def _is_boolean_ref_table(self, rows: List[Dict[str, str]]) -> bool:
        """
        Check if this looks like a boolean reference table (YES/NO, Y/N, etc.).
        
        Args:
            rows: List of data rows
            
        Returns:
            True if this looks like a boolean reference table
        """
        if not rows:
            return False
        
        # Check if there are exactly two rows
        if len(rows) != 2:
            return False
        
        # Check column names and values
        # Usually these tables have a code column and a description column
        if len(rows[0]) != 2:
            return False
        
        # Get column names
        columns = list(rows[0].keys())
        
        # Get values from both columns in both rows
        values = []
        for col in columns:
            values.extend([rows[0][col], rows[1][col]])
        
        # Check for common boolean indicators
        boolean_indicators = [
            'yes', 'no', 'y', 'n', 'true', 'false', 't', 'f',
            '1', '0', 'active', 'inactive', 'enabled', 'disabled'
        ]
        
        # Convert values to lowercase for comparison
        lower_values = [str(v).lower() for v in values]
        
        # Count how many boolean indicators we have
        count = sum(1 for v in lower_values if v in boolean_indicators)
        
        # If at least half of the values are boolean indicators, consider it a boolean table
        return count >= len(values) // 2
    
    def _add_boolean_weights(self, rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Add weights to a boolean reference table.
        
        For boolean tables, we typically want more "YES" than "NO", so we'll add
        weights of 0.7 for the "positive" value and 0.3 for the "negative" value.
        
        Args:
            rows: List of data rows
            
        Returns:
            List of data rows with weights added
        """
        if len(rows) != 2:
            return rows
        
        # Deep copy the rows
        new_rows = [dict(row) for row in rows]
        
        # Determine which row is the "positive" one
        positive_indicators = ['yes', 'y', 'true', 't', '1', 'active', 'enabled']
        
        positive_index = -1
        for i, row in enumerate(new_rows):
            # Check all values in this row
            for val in row.values():
                if str(val).lower() in positive_indicators:
                    positive_index = i
                    break
            if positive_index >= 0:
                break
        
        # If we found a positive value, assign weights
        if positive_index >= 0:
            new_rows[positive_index]['weight'] = 0.7
            new_rows[1 - positive_index]['weight'] = 0.3
        
        return new_rows 