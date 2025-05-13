#!/usr/bin/env python3
"""
Simple test script for the Schema Parser Agent.

This script demonstrates how to use the Schema Parser Agent to parse SQL scripts
into Intermediate Representation objects.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.schema_parse_agent import SchemaParseAgent
from utils.file_io import ensure_directory, read_file
from constants import DEFAULT_LLM_MODEL  # Import default model from constants
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a basic test of the Schema Parser Agent."""
    # Get the default model from environment or constants
    default_model = os.environ.get('DEFAULT_LLM_MODEL', DEFAULT_LLM_MODEL)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Schema Parser Agent")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output including prompts and LLM responses")
    parser.add_argument("--model", "-m", default=default_model, help=f"Specify the OpenAI model to use (default: {default_model})")
    parser.add_argument("--sql-file", "-f", default=None, help="Specify a custom SQL file to parse (default: samples/sql/sample.sql)")
    parser.add_argument("--schema-name", "-n", default="SampleOrdersDB", help="Specify the schema name (default: SampleOrdersDB)")
    args = parser.parse_args()
    
    verbose = args.verbose
    model = args.model
    schema_name = args.schema_name
    
    print("Testing Schema Parser Agent...")
    print(f"Default model from environment/constants: {default_model}")
    
    # Create a unique run ID for this test
    run_id = "test_run"
    
    # Ensure artifacts directory exists
    artifacts_dir = os.path.join(project_root, "artifacts")
    ensure_directory(artifacts_dir)
    
    # Initialize the Schema Parser Agent
    agent = SchemaParseAgent(
        run_id=run_id,
        artifacts_dir=artifacts_dir,
        seed=42,  # Use fixed seed for reproducibility
        llm_provider="openai",
        llm_model=model
    )
    
    # Path to our sample SQL file
    if args.sql_file:
        sql_file = args.sql_file
    else:
        sql_file = os.path.join(project_root, "samples", "sql", "sample.sql")
    
    # Parse the SQL file into a Schema object
    print(f"Parsing SQL file: {sql_file}")
    print(f"Using model: {model}")
    
    # Print file content if verbose
    if verbose:
        print("\n=== SQL File Content ===")
        print(read_file(sql_file))
        print("========================\n")
    
    # Save the original save_artifact method
    original_save_artifact = agent.save_artifact
    
    # Override save_artifact to print artifacts in verbose mode
    def verbose_save_artifact(name, content, is_json=False):
        result = original_save_artifact(name, content, is_json)
        if verbose:
            if name == "prompt":
                print("\n=== LLM Prompt ===")
                print(content)
                print("=================\n")
            elif name == "llm_response" and is_json:
                print("\n=== LLM Response ===")
                if isinstance(content, str):
                    parsed = json.loads(content)
                    print(json.dumps(parsed, indent=2))
                else:
                    print(content)
                print("====================\n")
        return result
    
    # Replace the save_artifact method temporarily
    agent.save_artifact = verbose_save_artifact
    
    try:
        # Parse the schema
        schema = agent.run(sql_file, schema_name=schema_name)
        
        # Print some basic information about the parsed schema
        print("\nParsed Schema:")
        print(f"Name: {schema.name}")
        print(f"Number of tables: {len(schema.tables)}")
        print(f"Tables: {[t.name for t in schema.tables]}")
        
        print("\nTables with foreign keys:")
        for table in schema.tables:
            if table.foreign_keys:
                print(f"  {table.name}: {len(table.foreign_keys)} foreign keys")
                for fk in table.foreign_keys:
                    print(f"    {fk.name}: {table.name}.{fk.columns} -> {fk.ref_table}.{fk.ref_columns}")
        
        print("\nReference tables (tables with only a primary key, no foreign keys):")
        ref_tables = [t for t in schema.tables if not t.foreign_keys]
        print(f"  {[t.name for t in ref_tables]}")
        
        print("\nSuccessfully parsed schema!")
        schema_path = os.path.join(artifacts_dir, run_id, 'SchemaParser', 'schema.json')
        print(f"Schema JSON saved to: {schema_path}")
        
        # Print schema JSON if verbose
        if verbose:
            print("\n=== Generated Schema JSON ===")
            print(schema.to_json(indent=2))
            print("============================\n")
    
    finally:
        # Restore the original save_artifact method
        agent.save_artifact = original_save_artifact


if __name__ == "__main__":
    main() 