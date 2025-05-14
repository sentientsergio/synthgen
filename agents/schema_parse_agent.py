"""
Schema Parser Agent for transforming SQL CREATE scripts to Intermediate Representation.

This agent uses LLM to parse SQL Server CREATE scripts and extract the schema information
into a structured IR model that can be used by downstream agents in the pipeline.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from agents.base import Agent
from models.ir import Schema, Table, Column, ColumnType, PrimaryKey, ForeignKey, CheckConstraint
from utils.file_io import read_file, write_json, write_file
from utils.llm import get_provider


class SchemaParseAgent(Agent):
    """Agent for parsing SQL CREATE scripts into Intermediate Representation (IR).
    
    This agent uses LLM capabilities to analyze SQL Server DDL scripts and transform them
    into a structured Schema object that captures all relevant information for downstream
    processing.
    """
    
    def __init__(
        self, 
        run_id: Optional[str] = None,
        artifacts_dir: str = "artifacts",
        seed: Optional[int] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
    ):
        """Initialize Schema Parser Agent.
        
        Args:
            run_id: Unique identifier for this run
            artifacts_dir: Directory for storing artifacts
            seed: Random seed for reproducibility
            llm_provider: Name of the LLM provider to use
            llm_model: Name of the LLM model to use
        """
        super().__init__("SchemaParser", run_id, artifacts_dir, seed)
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.provider = get_provider(llm_provider)
        
        # Store the last LLM calls for retry logic
        self._last_prompt = None
        self._last_schema_template = None

    def run(
        self, 
        sql_script_path: Union[str, Path],
        schema_name: Optional[str] = None,
        chunk_size: int = 10000,
        max_tokens: int = 4000, 
    ) -> Schema:
        """Parse the SQL script and generate the IR schema.
        
        Args:
            sql_script_path: Path to the SQL CREATE script
            schema_name: Name to use for the schema (if not specified, will be extracted from the script)
            chunk_size: Maximum characters to process in a single LLM call
            max_tokens: Maximum tokens to generate in the LLM response
            
        Returns:
            A Schema object representing the Intermediate Representation
        """
        self.logger.info(f"Parsing SQL script: {sql_script_path}")
        
        # Read the SQL script
        sql_script = read_file(sql_script_path)
        
        # If no schema name provided, use the filename
        if schema_name is None:
            schema_name = Path(sql_script_path).stem
        
        # Parse the SQL script into IR schema
        schema = self._parse_sql_to_schema(sql_script, schema_name, chunk_size, max_tokens)
        
        # If schema is None (parsing failed), create a minimal schema
        if schema is None:
            self.logger.error("Failed to parse schema, creating minimal schema object")
            schema = Schema(name=schema_name, tables=[], description="Failed to parse schema")
            self.save_error("Failed to parse schema", {"sql_script_path": str(sql_script_path)})
        else:
            # Save the schema to artifacts
            schema_json = schema.to_json(indent=2)
            self.save_artifact("schema", schema_json, is_json=True)
            
            self.logger.info(f"Successfully parsed schema '{schema.name}' with {len(schema.tables)} tables")
        
        return schema
    
    def _parse_sql_to_schema(
        self, 
        sql_script: str, 
        schema_name: str, 
        chunk_size: int = 10000, 
        max_tokens: int = 4000,
    ) -> Optional[Schema]:
        """Parse the SQL script into an IR Schema using LLM.
        
        Args:
            sql_script: SQL CREATE script content
            schema_name: Name to use for the schema
            chunk_size: Maximum characters to process in a single LLM call
            max_tokens: Maximum tokens to generate in the LLM response
            
        Returns:
            A Schema object representing the Intermediate Representation
        """
        self.logger.info(f"Processing SQL script ({len(sql_script)} characters)")
        
        # If the script is too large, we'll need to chunk it
        if len(sql_script) > chunk_size:
            return self._process_large_script(sql_script, schema_name, chunk_size, max_tokens)
        
        # Generate JSON schema template for the IR
        schema_template = self._get_schema_template(schema_name)
        
        # Create prompt for the LLM using externalized prompt template
        prompt_template = self.load_prompt("parse_schema")
        prompt = prompt_template.format(
            sql_script=sql_script,
            schema_name=schema_name
        )
        
        # Store for retry logic
        self._last_prompt = prompt
        self._last_schema_template = schema_template
        
        # Save the prompt as an artifact
        self.save_prompt(prompt)
        
        # Call LLM to parse the SQL script
        try:
            schema_json = self.provider.generate_json(
                prompt,
                schema_template,
                temperature=0.0,
                seed=self.seed,
                max_tokens=max_tokens,
                model=self.llm_model
            )
            
            # Save the response
            self.save_llm_response(json.dumps(schema_json, indent=2), "schema")
            
            # Convert the JSON response to a Schema object
            schema = self._create_schema_from_llm_response(schema_json)
            return schema
            
        except Exception as e:
            # Handle errors and retry if needed
            self.logger.error(f"Error parsing schema: {str(e)}")
            return self.handle_llm_error(e)
    
    def _create_schema_from_llm_response(self, response: Dict[str, Any]) -> Schema:
        """Create a Schema object from the LLM response.
        
        This handles conversion of data types and ensures the response is properly formatted.
        
        Args:
            response: JSON response from the LLM
            
        Returns:
            Schema object
        """
        # Create schema with basic information
        schema = Schema(
            name=response.get("name", "Unknown"),
            tables=[],
            description=response.get("description", ""),
            generation_rules=[]
        )
        
        # Process tables
        for table_data in response.get("tables", []):
            # Process columns with proper data type handling
            columns = []
            for col_data in table_data.get("columns", []):
                # Handle different data type formats
                if isinstance(col_data.get("data_type"), dict):
                    # New format with name, length, etc.
                    data_type_name = col_data["data_type"].get("name", "UNKNOWN")
                    length = col_data["data_type"].get("length")
                    precision = col_data["data_type"].get("precision")
                    scale = col_data["data_type"].get("scale")
                else:
                    # Old format with just the type name
                    data_type_name = col_data.get("data_type", "UNKNOWN")
                    length = col_data.get("length")
                    precision = col_data.get("precision")
                    scale = col_data.get("scale")
                
                # Convert string data type to enum
                try:
                    data_type = ColumnType.from_sql_type(data_type_name)
                except:
                    data_type = ColumnType.UNKNOWN
                
                column = Column(
                    name=col_data.get("name", "Unknown"),
                    data_type=data_type,
                    nullable=col_data.get("nullable", True),
                    length=length,
                    precision=precision,
                    scale=scale,
                    default_value=col_data.get("default_value"),
                    is_identity=col_data.get("is_identity", False),
                    description=col_data.get("description")
                )
                columns.append(column)
            
            # Create primary key if present
            primary_key = None
            if table_data.get("primary_key"):
                pk_data = table_data["primary_key"]
                primary_key = PrimaryKey(
                    name=pk_data.get("name", f"PK_{table_data.get('name')}"),
                    columns=pk_data.get("columns", [])
                )
            
            # Create foreign keys
            foreign_keys = []
            for fk_data in table_data.get("foreign_keys", []):
                fk = ForeignKey(
                    name=fk_data.get("name", "Unknown"),
                    columns=fk_data.get("columns", []),
                    ref_table=fk_data.get("ref_table", "Unknown"),
                    ref_columns=fk_data.get("ref_columns", []),
                    on_delete=fk_data.get("on_delete"),
                    on_update=fk_data.get("on_update")
                )
                foreign_keys.append(fk)
            
            # Create check constraints
            check_constraints = []
            for ck_data in table_data.get("check_constraints", []):
                ck = CheckConstraint(
                    name=ck_data.get("name", "Unknown"),
                    definition=ck_data.get("definition", "")
                )
                check_constraints.append(ck)
            
            # Create the table
            table = Table(
                name=table_data.get("name", "Unknown"),
                columns=columns,
                primary_key=primary_key,
                foreign_keys=foreign_keys,
                check_constraints=check_constraints,
                description=table_data.get("description")
            )
            
            schema.tables.append(table)
        
        return schema
    
    def _process_large_script(
        self, 
        sql_script: str, 
        schema_name: str, 
        chunk_size: int, 
        max_tokens: int,
    ) -> Optional[Schema]:
        """Process a large SQL script by chunking it.
        
        For large scripts, we process them in chunks and then combine the results.
        
        Args:
            sql_script: SQL CREATE script content
            schema_name: Name to use for the schema
            chunk_size: Maximum characters to process in a single LLM call
            max_tokens: Maximum tokens to generate in the LLM response
            
        Returns:
            A Schema object representing the combined Intermediate Representation
        """
        self.logger.info(f"Script is large ({len(sql_script)} chars), processing in chunks")
        
        # First, try to extract all CREATE TABLE statements
        tables_sql = self._extract_create_tables(sql_script)
        
        # Create an empty schema
        schema = Schema(name=schema_name, tables=[], description=f"SQL Server schema {schema_name}")
        
        # Process each table
        for i, table_sql in enumerate(tables_sql):
            self.logger.info(f"Processing table {i+1}/{len(tables_sql)}")
            
            # Create a mini-schema with just this table
            table_schema = self._parse_sql_to_schema(table_sql, schema_name, chunk_size, max_tokens)
            
            # If successful, add the table to our schema
            if table_schema and table_schema.tables:
                schema.tables.extend(table_schema.tables)
        
        # Process constraints that might be defined separately
        constraints_sql = self._extract_constraints(sql_script)
        if constraints_sql:
            self.logger.info("Processing separate constraints")
            constraints_schema = self._parse_sql_to_schema(constraints_sql, schema_name, chunk_size, max_tokens)
            
            # Merge constraints into the existing tables
            if constraints_schema:
                self._merge_constraints(schema, constraints_schema)
        
        return schema
    
    def _extract_create_tables(self, sql_script: str) -> List[str]:
        """Extract CREATE TABLE statements from a SQL script.
        
        Args:
            sql_script: SQL CREATE script content
            
        Returns:
            List of CREATE TABLE statements
        """
        # This is a simplified approach; in a real implementation we would use a more robust parser
        # or leverage the LLM to identify and extract CREATE TABLE blocks
        
        # Split the script by common statement terminators
        statements = []
        current_statement = []
        
        in_multiline_comment = False
        in_string = False
        
        for line in sql_script.splitlines():
            # Skip empty lines
            stripped_line = line.strip()
            if not stripped_line:
                continue
                
            # Handle comments and strings (simplified)
            if "/*" in stripped_line and not in_string:
                in_multiline_comment = True
            if "*/" in stripped_line and not in_string:
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue
            if stripped_line.startswith("--"):
                continue
                
            # Add the line to the current statement
            current_statement.append(line)
            
            # Check if the statement is complete
            if ";" in line:
                statement = "\n".join(current_statement)
                if "CREATE TABLE" in statement.upper():
                    statements.append(statement)
                current_statement = []
                
        # Check if there's an unfinished statement
        if current_statement:
            statement = "\n".join(current_statement)
            if "CREATE TABLE" in statement.upper():
                statements.append(statement)
                
        return statements
    
    def _extract_constraints(self, sql_script: str) -> str:
        """Extract ALTER TABLE statements with constraints from a SQL script.
        
        Args:
            sql_script: SQL CREATE script content
            
        Returns:
            SQL script with just the constraint definitions
        """
        # Simplified extraction of ALTER TABLE statements that add constraints
        constraints = []
        
        for line in sql_script.splitlines():
            if "ALTER TABLE" in line.upper() and ("ADD CONSTRAINT" in line.upper() or "ADD FOREIGN KEY" in line.upper()):
                constraints.append(line)
                
        return "\n".join(constraints)
    
    def _merge_constraints(self, schema: Schema, constraints_schema: Schema) -> None:
        """Merge constraints from constraints_schema into the main schema.
        
        Args:
            schema: The main schema to update
            constraints_schema: Schema containing constraints to merge
        """
        # This is a simplified approach
        # In a real implementation, we would carefully merge constraints by table
        
        if not constraints_schema or not constraints_schema.tables:
            return
            
        for constraints_table in constraints_schema.tables:
            # Find the matching table in the main schema
            main_table = next((t for t in schema.tables if t.name == constraints_table.name), None)
            if main_table:
                # Add foreign keys
                for fk in constraints_table.foreign_keys:
                    if not any(existing.name == fk.name for existing in main_table.foreign_keys):
                        main_table.foreign_keys.append(fk)
                
                # Add check constraints
                for ck in constraints_table.check_constraints:
                    if not any(existing.name == ck.name for existing in main_table.check_constraints):
                        main_table.check_constraints.append(ck)
    
    def _create_parse_prompt(self, sql_script: str, schema_name: str) -> str:
        """Create a prompt for parsing SQL to Schema.
        
        This method is kept for backward compatibility but now uses the externalized prompt template.
        
        Args:
            sql_script: SQL CREATE script content
            schema_name: Name to use for the schema
            
        Returns:
            Prompt for the LLM
        """
        prompt_template = self.load_prompt("parse_schema")
        return prompt_template.format(
            sql_script=sql_script,
            schema_name=schema_name
        )
    
    def _get_schema_template(self, schema_name: str) -> Dict[str, Any]:
        """Get the JSON schema template for the IR.
        
        Args:
            schema_name: Name to use for the schema
            
        Returns:
            JSON schema template
        """
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the schema"},
                "description": {"type": "string", "description": "Description of the schema"},
                "tables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the table"},
                            "description": {"type": "string", "description": "Description of the table"},
                            "columns": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "Name of the column"},
                                        "data_type": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string", "description": "SQL Server data type name"},
                                                "length": {"type": ["integer", "null"], "description": "Length for string types"},
                                                "precision": {"type": ["integer", "null"], "description": "Precision for numeric types"},
                                                "scale": {"type": ["integer", "null"], "description": "Scale for numeric types"},
                                            },
                                            "required": ["name"]
                                        },
                                        "nullable": {"type": "boolean", "description": "Whether the column can be NULL"},
                                        "default_value": {"type": ["string", "null"], "description": "Default value for the column, if any"},
                                        "is_identity": {"type": "boolean", "description": "Whether the column is an identity column"},
                                        "description": {"type": "string", "description": "Description of the column"}
                                    },
                                    "required": ["name", "data_type", "nullable"]
                                }
                            },
                            "primary_key": {
                                "type": ["object", "null"],
                                "properties": {
                                    "name": {"type": "string", "description": "Name of the primary key constraint"},
                                    "columns": {"type": "array", "items": {"type": "string"}, "description": "Columns in the primary key"},
                                },
                                "required": ["name", "columns"]
                            },
                            "foreign_keys": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "Name of the foreign key constraint"},
                                        "columns": {"type": "array", "items": {"type": "string"}, "description": "Columns in the foreign key"},
                                        "ref_table": {"type": "string", "description": "Referenced table"},
                                        "ref_columns": {"type": "array", "items": {"type": "string"}, "description": "Referenced columns"},
                                        "on_delete": {"type": "string", "description": "ON DELETE action"},
                                        "on_update": {"type": "string", "description": "ON UPDATE action"},
                                    },
                                    "required": ["name", "columns", "ref_table", "ref_columns"]
                                }
                            },
                            "check_constraints": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "Name of the check constraint"},
                                        "definition": {"type": "string", "description": "SQL definition of the constraint"},
                                    },
                                    "required": ["name", "definition"]
                                }
                            },
                            "is_reference_table": {"type": "boolean", "description": "Whether this is a reference/lookup table"}
                        },
                        "required": ["name", "columns"]
                    }
                }
            },
            "required": ["name", "tables"]
        }
    
    def retry_llm_call(self) -> Optional[Schema]:
        """Retry the last LLM call.
        
        Returns:
            A Schema object representing the Intermediate Representation
        """
        if not self._last_prompt or not self._last_schema_template:
            self.logger.error("No previous LLM call to retry")
            return None
            
        try:
            schema_json = self.provider.generate_json(
                self._last_prompt,
                self._last_schema_template,
                temperature=0.0,
                seed=self.seed,
                model=self.llm_model
            )
            
            # Convert the JSON response to a Schema object
            schema = self._create_schema_from_llm_response(schema_json)
            return schema
            
        except Exception as e:
            self.logger.error(f"Retry failed: {str(e)}")
            return None 