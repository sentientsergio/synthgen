#!/usr/bin/env python3
"""
Data Synthesis Agent

This agent is responsible for generating synthetic data based on the schema constraints
and reference data. It leverages the distribution weights in the reference data
to create realistic data distributions.

The agent uses LLM to:
1. Analyze schema constraints and relationships
2. Generate data values that respect constraints and data types
3. Create realistic relationships between tables
4. Apply distribution weights from reference data
"""

import os
import json
import csv
import random
import re  # Import re at the top of the file
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from agents.base import Agent
from models.ir import Schema, Table, Column, ColumnType, ReferenceData
from utils.file_io import write_json, write_file
from utils.llm import get_provider


class DataSynthAgent(Agent):
    """
    Agent for generating synthetic data based on the schema IR with reference data.
    
    This agent creates realistic data that respects all schema constraints including
    data types, primary keys, foreign keys, and check constraints. It leverages
    reference data with distribution weights to create realistic data distributions.
    """
    
    def __init__(self, run_id: str, artifacts_dir: str, **kwargs):
        """Initialize the DataSynthAgent.
        
        Args:
            run_id: Unique identifier for this run
            artifacts_dir: Directory for storing artifacts
            **kwargs: Additional parameters
        """
        super().__init__(
            name="DataSynthAgent",
            run_id=run_id,
            artifacts_dir=artifacts_dir,
            seed=kwargs.get("seed")
        )
        self.llm_provider = kwargs.get("llm_provider", "openai")
        self.llm_model = kwargs.get("llm_model", "gpt-4o")
        self.provider = get_provider(self.llm_provider)
        
        # Set random seed for reproducible data generation
        if self.seed is not None:
            random.seed(self.seed)
        
        # Store the last LLM call for retry logic
        self._last_prompt = None
        self._last_params = None
    
    def llm_call(self, prompt: str, **kwargs) -> str:
        """Make an LLM API call.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the LLM API call
            
        Returns:
            Response from the LLM
        """
        self._last_prompt = prompt
        self._last_params = kwargs
        
        return self.provider.generate(
            prompt=prompt,
            temperature=kwargs.get("temperature", 0.2),  # Some creativity is good for data variety
            max_tokens=kwargs.get("max_tokens", 4000),
            seed=self.seed,
            model=self.llm_model
        )
    
    def retry_llm_call(self) -> str:
        """Retry the last LLM API call.
        
        Returns:
            Response from the LLM
        
        Raises:
            RuntimeError: If there's no previous LLM call to retry
        """
        if self._last_prompt is None:
            raise RuntimeError("No previous LLM call to retry")
        
        return self.llm_call(self._last_prompt, **self._last_params)
    
    def run(self, 
            schema: Schema, 
            output_dir: Union[str, Path],
            row_counts: Optional[Dict[str, int]] = None,
            custom_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
        """Generate synthetic data based on the schema.
        
        Args:
            schema: Schema IR with reference data
            output_dir: Directory to save the generated data
            row_counts: Dictionary mapping table names to row counts
            custom_rules: Optional custom generation rules
            
        Returns:
            Dictionary mapping table names to output file paths
        """
        self.logger.info(f"Generating synthetic data for schema '{schema.name}'")
        
        # Save input schema for reference
        self.save_artifact("input_schema", schema.to_json(indent=2), is_json=True)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Set default row counts if not provided
        if row_counts is None:
            row_counts = self._default_row_counts(schema)
        
        # Log the tables and row counts we'll generate
        tables_info = "\n".join([f"  - {table}: {row_counts.get(table, 'default')} rows" 
                             for table in [t.name for t in schema.tables]])
        self.logger.info(f"Will generate data for tables:\n{tables_info}")
        
        # Generate data for each table in the correct order (respecting foreign key constraints)
        output_files = {}
        generation_order = self._determine_generation_order(schema)
        
        for table_name in generation_order:
            table = schema.get_table(table_name)
            if table:
                output_file = self._generate_table_data(
                    schema, table, row_counts.get(table_name, 10), output_path, custom_rules
                )
                output_files[table_name] = output_file
        
        return output_files
    
    def _default_row_counts(self, schema: Schema) -> Dict[str, int]:
        """Determine default row counts for each table.
        
        Sets reasonable defaults based on table type:
        - Reference tables: Use actual reference data if available, otherwise 5-10 rows
        - Data tables: 50-100 rows for normal tables, less for junction tables
        
        Args:
            schema: Schema with tables
            
        Returns:
            Dictionary mapping table names to row counts
        """
        row_counts = {}
        
        for table in schema.tables:
            if table.is_reference_table:
                # For reference tables with reference data, use that count
                if table.reference_data and table.reference_data.rows:
                    row_counts[table.name] = len(table.reference_data.rows)
                else:
                    # Otherwise generate a small number of reference rows
                    row_counts[table.name] = 5
            else:
                # For regular data tables, generate more rows
                # Use fewer rows for junction tables (tables that mainly contain foreign keys)
                fk_columns = sum(1 for fk in table.foreign_keys for _ in fk.columns)
                if fk_columns > 0 and fk_columns >= len(table.columns) / 2:
                    # Likely a junction table
                    row_counts[table.name] = 25
                else:
                    # Regular data table
                    row_counts[table.name] = 50
        
        return row_counts
    
    def _determine_generation_order(self, schema: Schema) -> List[str]:
        """Determine the order in which tables should be generated.
        
        Tables with foreign key dependencies must be generated after the tables they
        reference. Reference tables are generated first, followed by data tables in
        dependency order.
        
        Args:
            schema: Schema with tables and relationships
            
        Returns:
            List of table names in generation order
        """
        # Start with reference tables
        ref_tables = [table.name for table in schema.get_reference_tables()]
        
        # Then add other tables in dependency order
        data_tables = [table.name for table in schema.get_data_tables()]
        
        # Build dependency graph
        dependencies = {table.name: set() for table in schema.tables}
        for table in schema.tables:
            for fk in table.foreign_keys:
                dependencies[table.name].add(fk.ref_table)
        
        # Topological sort
        visited = set(ref_tables)  # Mark reference tables as already visited
        generation_order = ref_tables.copy()
        
        def visit(table_name):
            if table_name in visited:
                return
            if table_name in temp_visited:
                # Circular dependency, break it (could be more sophisticated)
                return
            
            temp_visited.add(table_name)
            
            # Visit dependencies first
            for dep in dependencies.get(table_name, set()):
                visit(dep)
            
            temp_visited.remove(table_name)
            visited.add(table_name)
            generation_order.append(table_name)
        
        # Process all data tables
        temp_visited = set()
        for table_name in data_tables:
            if table_name not in visited:
                visit(table_name)
        
        self.logger.info(f"Generation order: {', '.join(generation_order)}")
        return generation_order
    
    def _generate_table_data(self, 
                           schema: Schema, 
                           table: Table, 
                           row_count: int, 
                           output_dir: Path,
                           custom_rules: Optional[Dict[str, Any]] = None) -> Path:
        """Generate synthetic data for a single table.
        
        Args:
            schema: Complete schema
            table: Table to generate data for
            row_count: Number of rows to generate
            output_dir: Directory to save the generated data
            custom_rules: Optional custom generation rules
            
        Returns:
            Path to the generated CSV file
        """
        self.logger.info(f"Generating {row_count} rows for table '{table.name}'")
        
        # For reference tables with reference data, use that directly
        if table.is_reference_table and table.reference_data and table.reference_data.rows:
            data = self._use_reference_data(table, row_count)
        else:
            # For regular tables, generate synthetic data
            data = self._generate_synthetic_data(schema, table, row_count, custom_rules)
        
        # Save to CSV
        output_file = output_dir / f"{table.name}.csv"
        self._write_csv(data, output_file)
        
        # Save a copy to artifacts
        self.save_artifact(f"data_{table.name}", "\n".join([",".join(map(str, row.values())) for row in data]))
        
        return output_file
    
    def _use_reference_data(self, table: Table, row_count: int) -> List[Dict[str, Any]]:
        """Use existing reference data for the table.
        
        For reference tables with reference data, we use the actual reference data
        rather than generating new values. If distribution weights are provided,
        we sample according to those weights.
        
        Args:
            table: Table with reference data
            row_count: Number of rows to generate (likely ignored for reference data)
            
        Returns:
            List of dictionaries representing the rows
        """
        if not table.reference_data or not table.reference_data.rows:
            return []
        
        # Return the reference data rows directly
        # Note: We don't typically expand reference tables beyond their defined values
        return table.reference_data.rows.copy()
    
    def _generate_synthetic_data(self, 
                               schema: Schema, 
                               table: Table, 
                               row_count: int,
                               custom_rules: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate synthetic data for a table.
        
        For regular tables, we generate synthetic data based on:
        1. Column data types and constraints
        2. Primary key uniqueness
        3. Foreign key references to other tables
        4. Check constraints
        5. Distribution rules in reference data
        
        Args:
            schema: Complete schema
            table: Table to generate data for
            row_count: Number of rows to generate
            custom_rules: Optional custom generation rules
            
        Returns:
            List of dictionaries representing the rows
        """
        # For small tables, use the LLM to generate data
        if row_count <= 50:
            return self._llm_generate_data(schema, table, row_count, custom_rules)
        
        # For larger tables, use a hybrid approach (LLM + algorithmic)
        # First, generate a smaller set with LLM to learn patterns
        sample_rows = self._llm_generate_data(schema, table, min(20, row_count), custom_rules)
        
        # Then, generate the rest algorithmically based on the sample
        if len(sample_rows) < row_count:
            additional_rows = self._algorithmic_generate_data(schema, table, row_count - len(sample_rows), sample_rows)
            sample_rows.extend(additional_rows)
        
        return sample_rows
    
    def _llm_generate_data(self, 
                         schema: Schema, 
                         table: Table, 
                         row_count: int,
                         custom_rules: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Use LLM to generate realistic data for a table.
        
        Args:
            schema: Complete schema
            table: Table to generate data for
            row_count: Number of rows to generate
            custom_rules: Optional custom generation rules
            
        Returns:
            List of dictionaries representing the rows
        """
        # Create prompt for the LLM
        prompt = self._create_generation_prompt(schema, table, row_count, custom_rules)
        
        # Save the prompt for reference
        self.save_prompt(prompt)
        
        # Call LLM to generate data
        try:
            response = self.llm_call(prompt, temperature=0.3)  # More variety for synthetic data
            self.save_artifact(f"llm_response_{table.name}", response)
            
            # Parse the LLM response to get the data
            rows = self._parse_generated_data(response, table)
            return rows
        except Exception as e:
            self.logger.error(f"Error generating data for table '{table.name}': {str(e)}")
            # Return an empty list if generation fails
            return []
    
    def _create_generation_prompt(self, 
                                schema: Schema, 
                                table: Table, 
                                row_count: int,
                                custom_rules: Optional[Dict[str, Any]] = None) -> str:
        """Create a prompt for the LLM to generate data.
        
        This builds a comprehensive prompt with:
        1. Table structure and constraints
        2. Foreign key relationships
        3. Reference data with distribution weights
        4. Custom generation rules (if provided)
        
        Args:
            schema: Complete schema
            table: Table to generate data for
            row_count: Number of rows to generate
            custom_rules: Optional custom generation rules
            
        Returns:
            Prompt string for the LLM
        """
        # Build information about the table
        table_info = json.dumps(table.to_dict(), indent=2)
        
        # Get information about foreign key references
        fk_references = []
        for fk in table.foreign_keys:
            ref_table = schema.get_table(fk.ref_table)
            if ref_table and ref_table.reference_data and ref_table.reference_data.rows:
                # Include a sample of reference data (up to 10 rows)
                sample_rows = ref_table.reference_data.rows[:10]
                # Include distribution weights if available
                has_weights = any("weight" in row for row in sample_rows)
                
                fk_references.append(
                    f"Foreign key {fk.name} references table {fk.ref_table}:\n"
                    f"Columns: {', '.join(fk.columns)} -> {', '.join(fk.ref_columns)}\n"
                    f"Reference data sample ({len(ref_table.reference_data.rows)} total rows)"
                    f"{' with distribution weights' if has_weights else ''}:\n"
                    f"{json.dumps(sample_rows, indent=2)}"
                )
        
        fk_section = "\n\n".join(fk_references) if fk_references else "No foreign key references with reference data."
        
        # Build prompt
        prompt = f"""# Synthetic Data Generation Task

## Objective
Generate {row_count} rows of synthetic data for the SQL Server table '{table.name}'.

## Table Structure
```json
{table_info}
```

## Foreign Key Reference Data
{fk_section}

## Instructions
1. Generate {row_count} rows of realistic data for this table
2. Follow all constraints:
   - Respect data types and length limits for each column
   - Ensure primary key values are unique
   - Reference valid foreign key values from related tables
   - Follow check constraints
   - Respect NOT NULL constraints
3. When using reference data with weights, distribute foreign key references proportionally
4. Create realistic and varied values, avoid repetitive patterns
5. For columns that are part of both a primary key and foreign key, ensure values don't conflict

## Output Format
Return ONLY a JSON array of objects, with each object representing a row.
Each object should have column names as keys and values should be appropriate for the column data type.

Example:
```json
[
  {{
    "column1": "value1",
    "column2": 42,
    ...
  }},
  ...
]
```
"""
        
        # Add custom rules if provided
        if custom_rules and table.name in custom_rules:
            rules_str = json.dumps(custom_rules[table.name], indent=2)
            prompt += f"\n## Custom Generation Rules\n```json\n{rules_str}\n```\n"
        
        return prompt
    
    def _parse_generated_data(self, response: str, table: Table) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract the generated data.
        
        Args:
            response: LLM response text
            table: Table structure for type conversion
            
        Returns:
            List of dictionaries representing the rows
        """
        try:
            # Extract JSON array from the response
            # First, look for JSON code blocks
            json_match = re.search(r'```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no code blocks, try to find array directly
                json_str = response.strip()
                if not json_str.startswith('['):
                    # Find the first '[' and the last ']'
                    start = json_str.find('[')
                    end = json_str.rfind(']') + 1
                    if start >= 0 and end > start:
                        json_str = json_str[start:end]
                    else:
                        raise ValueError("No JSON array found in response")
            
            # Parse the JSON
            data = json.loads(json_str)
            
            # Convert data types based on column definitions
            return self._convert_data_types(data, table)
            
        except Exception as e:
            self.logger.error(f"Error parsing generated data: {str(e)}")
            # Try a simpler, more lenient parsing approach
            try:
                # Look for anything that might be a JSON array
                array_pattern = r'\[(.*)\]'
                match = re.search(array_pattern, response, re.DOTALL)
                if match:
                    # Fix common JSON issues
                    array_str = match.group(0)
                    # Replace single quotes with double quotes
                    array_str = array_str.replace("'", '"')
                    # Fix unquoted keys
                    array_str = re.sub(r'(\w+):', r'"\1":', array_str)
                    
                    data = json.loads(array_str)
                    return self._convert_data_types(data, table)
                else:
                    return []
            except:
                # If all else fails, return empty list
                return []
    
    def _convert_data_types(self, data: List[Dict[str, Any]], table: Table) -> List[Dict[str, Any]]:
        """Convert data types based on column definitions.
        
        Args:
            data: List of row dictionaries
            table: Table with column definitions
            
        Returns:
            Data with correctly typed values
        """
        converted_data = []
        
        for row in data:
            converted_row = {}
            for col_name, value in row.items():
                column = table.get_column(col_name)
                if column:
                    # Convert based on column type
                    if value is None:
                        converted_row[col_name] = None
                    elif column.is_numeric:
                        try:
                            if column.data_type in (ColumnType.INTEGER, ColumnType.BIGINT, 
                                                  ColumnType.SMALLINT, ColumnType.TINYINT):
                                converted_row[col_name] = int(value)
                            else:
                                converted_row[col_name] = float(value)
                        except:
                            # Fallback to original value if conversion fails
                            converted_row[col_name] = value
                    elif column.is_boolean:
                        if isinstance(value, bool):
                            converted_row[col_name] = value
                        elif str(value).lower() in ('true', 't', 'yes', 'y', '1'):
                            converted_row[col_name] = True
                        elif str(value).lower() in ('false', 'f', 'no', 'n', '0'):
                            converted_row[col_name] = False
                        else:
                            converted_row[col_name] = value
                    else:
                        # String, date, etc. - keep as string
                        converted_row[col_name] = str(value)
                else:
                    # Column not found, keep original value
                    converted_row[col_name] = value
            
            converted_data.append(converted_row)
        
        return converted_data
    
    def _algorithmic_generate_data(self, 
                                 schema: Schema, 
                                 table: Table, 
                                 row_count: int,
                                 sample_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate synthetic data algorithmically based on sample rows.
        
        This method is used for larger tables where LLM-based generation would be
        too expensive. It uses the sample rows generated by the LLM to learn patterns
        and then generates similar data algorithmically.
        
        Args:
            schema: Complete schema
            table: Table to generate data for
            row_count: Number of additional rows to generate
            sample_rows: Sample rows to learn from
            
        Returns:
            List of dictionaries representing the additional rows
        """
        if not sample_rows:
            return []
        
        # This is a simplified implementation
        # A more sophisticated version would analyze value patterns and distributions
        additional_rows = []
        
        # Get primary key columns
        pk_columns = table.primary_key.columns if table.primary_key else []
        
        # Get all generated primary key values to avoid duplicates
        existing_pk_values = set()
        if pk_columns:
            for row in sample_rows:
                pk_value = tuple(row.get(col) for col in pk_columns)
                existing_pk_values.add(pk_value)
        
        # Get foreign key mappings and valid values
        fk_mappings = {}
        for fk in table.foreign_keys:
            ref_table = schema.get_table(fk.ref_table)
            if ref_table and ref_table.reference_data and ref_table.reference_data.rows:
                # Extract valid values for this foreign key
                valid_values = []
                for ref_row in ref_table.reference_data.rows:
                    # Each reference row should have values for all the reference columns
                    if all(col in ref_row for col in fk.ref_columns):
                        values = [ref_row[col] for col in fk.ref_columns]
                        valid_values.append(values)
                
                # Get distribution weights if available
                weights = None
                if ref_table.reference_data.distribution_strategy == "weighted_random":
                    weights = ref_table.reference_data.get_weighted_distribution()
                
                fk_mappings[tuple(fk.columns)] = (valid_values, weights)
        
        # Generate additional rows
        for _ in range(row_count):
            new_row = {}
            
            # Randomly select and modify a sample row as a starting point
            template_row = random.choice(sample_rows)
            
            # Start by copying values from the template
            for col_name, value in template_row.items():
                column = table.get_column(col_name)
                if not column:
                    continue
                
                # Generate a new value based on column type and constraints
                if column.is_numeric:
                    # For numeric columns, vary the value slightly
                    if isinstance(value, (int, float)):
                        variation = random.uniform(0.8, 1.2)
                        new_value = value * variation
                        if column.data_type in (ColumnType.INTEGER, ColumnType.BIGINT, 
                                              ColumnType.SMALLINT, ColumnType.TINYINT):
                            new_value = int(new_value)
                        new_row[col_name] = new_value
                    else:
                        new_row[col_name] = value
                elif column.is_string:
                    # For string columns, try to maintain the pattern
                    if isinstance(value, str):
                        # Simple variation - append/prepend some random characters
                        suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2))
                        new_row[col_name] = f"{value[:5]}{suffix}"[-column.length:] if column.length else f"{value[:5]}{suffix}"
                    else:
                        new_row[col_name] = str(value)
                else:
                    # For other types, just copy the value
                    new_row[col_name] = value
            
            # Handle foreign keys using reference data and weights
            for fk_columns, (valid_values, weights) in fk_mappings.items():
                if valid_values:
                    # Select a valid value set based on weights
                    if weights:
                        indices = list(range(len(valid_values)))
                        weight_values = list(weights.values())
                        selected_idx = random.choices(indices, weights=weight_values, k=1)[0]
                        selected_values = valid_values[selected_idx]
                    else:
                        selected_values = random.choice(valid_values)
                    
                    # Assign to row
                    for i, col in enumerate(fk_columns):
                        if i < len(selected_values):
                            new_row[col] = selected_values[i]
            
            # Ensure primary key is unique
            if pk_columns:
                # Create a unique suffix for primary key if needed
                pk_value = tuple(new_row.get(col) for col in pk_columns)
                suffix = 1
                while pk_value in existing_pk_values:
                    # Modify the primary key value
                    for col in pk_columns:
                        column = table.get_column(col)
                        if column and column.is_numeric:
                            new_row[col] = int(new_row.get(col, 0)) + suffix
                        elif column and column.is_string:
                            base_value = str(new_row.get(col, ''))
                            new_row[col] = f"{base_value}_{suffix}"
                    
                    pk_value = tuple(new_row.get(col) for col in pk_columns)
                    suffix += 1
                
                existing_pk_values.add(pk_value)
            
            additional_rows.append(new_row)
        
        return additional_rows
    
    def _write_csv(self, data: List[Dict[str, Any]], output_file: Path) -> None:
        """Write data to a CSV file.
        
        Args:
            data: List of row dictionaries
            output_file: Path to output file
        """
        if not data:
            # Create an empty file
            with open(output_file, 'w', newline='') as f:
                f.write("")
            return
        
        # Get column names from the first row
        columns = list(data[0].keys())
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
        
        self.logger.info(f"Wrote {len(data)} rows to {output_file}") 