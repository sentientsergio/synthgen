#!/usr/bin/env python3
"""
Simple test script for the Reference Data Agent.

This script demonstrates how to use the Reference Data Agent to load
reference data into a schema and incorporate distribution weights.
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

from agents.ref_data_agent import RefDataAgent
from agents.schema_parse_agent import SchemaParseAgent
from utils.file_io import ensure_directory, read_file
from constants import DEFAULT_LLM_MODEL
from models.ir import Schema
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a demonstration of the Reference Data Agent."""
    # Get the default model from environment or constants
    default_model = os.environ.get('DEFAULT_LLM_MODEL', DEFAULT_LLM_MODEL)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Reference Data Agent")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output including prompts and LLM responses")
    parser.add_argument("--model", "-m", default=default_model, help=f"Specify the OpenAI model to use (default: {default_model})")
    parser.add_argument("--sql-file", "-f", default=None, help="Specify a custom SQL file to parse (default: samples/sql/sample.sql)")
    parser.add_argument("--ref-data", "-r", default=None, help="Specify a custom reference data file or directory (default: tests/fixtures/sample_ref_data.csv)")
    parser.add_argument("--schema-name", "-n", default="SampleOrdersDB", help="Specify the schema name (default: SampleOrdersDB)")
    parser.add_argument("--no-intelligent", action="store_true", help="Disable intelligent mapping (use simple name-based mapping)")
    args = parser.parse_args()
    
    verbose = args.verbose
    model = args.model
    schema_name = args.schema_name
    intelligent_mapping = not args.no_intelligent
    
    print("Testing Reference Data Agent...")
    print(f"Using model: {model}")
    print(f"Using intelligent mapping: {intelligent_mapping}")
    
    # Create a unique run ID for this test
    run_id = "test_ref_data_agent"
    
    # Ensure artifacts directory exists
    artifacts_dir = os.path.join(project_root, "artifacts")
    test_artifacts_dir = os.path.join(artifacts_dir, run_id)
    ensure_directory(test_artifacts_dir)
    
    # Path to SQL file
    if args.sql_file:
        sql_file = args.sql_file
    else:
        sql_file = os.path.join(project_root, "samples", "sql", "sample.sql")
    
    # Path to reference data
    if args.ref_data:
        ref_data_file = args.ref_data
    else:
        ref_data_file = os.path.join(project_root, "tests", "fixtures", "sample_ref_data.csv")
    
    # Step 1: Parse the SQL file to get the schema
    print(f"\n=== Step 1: Parsing SQL schema from {sql_file} ===")
    schema_parser = SchemaParseAgent(
        run_id=run_id,
        artifacts_dir=test_artifacts_dir,
        seed=42,  # Use fixed seed for reproducibility
        llm_provider="openai",
        llm_model=model
    )
    
    schema = schema_parser.run(sql_file, schema_name=schema_name)
    print(f"Parsed schema with {len(schema.tables)} tables")
    
    # Print tables in the schema
    print("\nTables in the schema:")
    for i, table in enumerate(schema.tables):
        print(f"  {i+1}. {table.name} ({len(table.columns)} columns)")
    
    # Save the parsed schema
    schema_file = os.path.join(test_artifacts_dir, "schema.json")
    schema.save_to_file(schema_file)
    print(f"Saved parsed schema to {schema_file}")
    
    # Step 2: Load reference data into the schema
    print(f"\n=== Step 2: Loading reference data from {ref_data_file} ===")
    ref_data_agent = RefDataAgent(
        run_id=run_id,
        artifacts_dir=test_artifacts_dir,
        llm_provider="openai",
        llm_model=model
    )
    
    # Load the reference data
    enriched_schema = ref_data_agent.run(
        schema=schema,
        ref_data_path=ref_data_file,
        intelligent_mapping=intelligent_mapping
    )
    
    # Save the enriched schema
    enriched_schema_file = os.path.join(test_artifacts_dir, "enriched_schema.json")
    enriched_schema.save_to_file(enriched_schema_file)
    print(f"Saved enriched schema to {enriched_schema_file}")
    
    # Step 3: Show tables with reference data
    print("\n=== Step 3: Tables with reference data ===")
    ref_tables = []
    for table in enriched_schema.tables:
        if table.reference_data:
            ref_tables.append(table)
            print(f"\nTable: {table.name}")
            print(f"  Number of reference rows: {len(table.reference_data.rows)}")
            print(f"  Distribution strategy: {table.reference_data.distribution_strategy or 'None'}")
            
            # Show distribution weights if available
            if table.reference_data.distribution_strategy == "weighted_random":
                print("  Distribution weights:")
                for i, row in enumerate(table.reference_data.rows):
                    if "weight" in row:
                        weight_info = f" (weight: {row['weight']})"
                    else:
                        weight_info = ""
                    
                    # Print first two columns as key/value for demonstration
                    if len(row) > 1:
                        cols = list(row.keys())
                        print(f"    {row[cols[0]]}: {row[cols[1]]}{weight_info}")
    
    # If no tables have reference data, note that
    if not ref_tables:
        print("No tables have reference data. The agent wasn't able to map any reference data to the schema tables.")
        print("This could be because:")
        print("  1. The table names in the reference data don't match the schema")
        print("  2. The schema doesn't have any tables that would typically contain reference data")
        print("  3. Intelligent mapping isn't finding good matches")
        
        # Suggest solutions
        print("\nSuggestions:")
        print("  1. Try modifying the reference data file to match the schema table names")
        print("  2. Use verbose mode to see the LLM reasoning")
        print("  3. Create more descriptive table/column names in both the schema and reference data")
    else:
        print(f"\nSuccessfully added reference data to {len(ref_tables)} tables!")
        
    print("\nReference Data Agent demonstration complete!")


if __name__ == "__main__":
    main() 