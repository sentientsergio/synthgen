#!/usr/bin/env python3
"""
Test script for the Schema Parser Agent.

This script demonstrates how to use the SchemaParseAgent to parse
a SQL CREATE script and build an Intermediate Representation (IR).
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.schema_parse_agent import SchemaParseAgent
from utils.file_io import ensure_directory


def main():
    """Run a test of the Schema Parser Agent."""
    print("Testing Schema Parser Agent...")
    
    # Create a unique run ID
    run_id = "test_run"
    
    # Create artifacts directory
    artifacts_dir = "artifacts"
    ensure_directory(artifacts_dir)
    
    # Initialize the agent
    agent = SchemaParseAgent(
        run_id=run_id,
        artifacts_dir=artifacts_dir,
        llm_provider="openai",
        llm_model="gpt-4o"
    )
    
    # Get the path to the sample SQL script
    sql_script_path = Path("samples/sql/sample.sql")
    if not sql_script_path.exists():
        print(f"Error: SQL script not found: {sql_script_path}")
        return 1
    
    # Parse the schema
    print(f"Parsing SQL script: {sql_script_path}")
    schema = agent.run(sql_script_path, schema_name="SampleDB")
    
    # Output some basic info about the parsed schema
    print(f"\nParsed Schema: {schema.name}")
    print(f"Number of tables: {len(schema.tables)}")
    
    # List tables
    print("\nTables:")
    for table in schema.tables:
        print(f"  - {table.name} ({len(table.columns)} columns)")
        
        # List columns
        for col in table.columns:
            nullable = "NULL" if col.nullable else "NOT NULL"
            print(f"    - {col.name}: {col.data_type.name} {nullable}")
        
        # Show primary key
        if table.primary_key:
            print(f"    PK: {table.primary_key.name} on {', '.join(table.primary_key.columns)}")
        
        # Show foreign keys
        for fk in table.foreign_keys:
            print(f"    FK: {fk.name} to {fk.ref_table} ({', '.join(fk.columns)} -> {', '.join(fk.ref_columns)})")
    
    # Show reference tables
    ref_tables = schema.get_reference_tables()
    print(f"\nReference tables: {[t.name for t in ref_tables]}")
    
    # Show data tables
    data_tables = schema.get_data_tables()
    print(f"Data tables: {[t.name for t in data_tables]}")
    
    # Show artifacts location
    print(f"\nArtifacts saved to: {os.path.join(artifacts_dir, run_id, 'SchemaParser')}")
    print("  - prompt.md: The prompt sent to the LLM")
    print("  - schema.json: The parsed schema in JSON format")
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    main() 