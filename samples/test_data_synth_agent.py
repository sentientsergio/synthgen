#!/usr/bin/env python3
"""
Simple test script for the Data Synthesis Agent.

This script demonstrates how to use the Data Synthesis Agent to generate
realistic synthetic data based on schema constraints and reference data.
It shows how distribution weights in reference data influence the generated data.
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
from agents.ref_data_agent import RefDataAgent
from agents.data_synth_agent import DataSynthAgent
from utils.file_io import ensure_directory, read_file
from constants import DEFAULT_LLM_MODEL
from models.ir import Schema
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a demonstration of the Data Synthesis Agent."""
    # Get the default model from environment or constants
    default_model = os.environ.get('DEFAULT_LLM_MODEL', DEFAULT_LLM_MODEL)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Data Synthesis Agent")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output including prompts and LLM responses")
    parser.add_argument("--model", "-m", default=default_model, help=f"Specify the OpenAI model to use (default: {default_model})")
    parser.add_argument("--sql-file", "-f", default=None, help="Specify a custom SQL file to parse (default: samples/sql/sample.sql)")
    parser.add_argument("--ref-data", "-r", default=None, help="Specify a custom reference data file or directory (default: tests/fixtures/sample_ref_data.csv)")
    parser.add_argument("--schema-name", "-n", default="SampleOrdersDB", help="Specify the schema name (default: SampleOrdersDB)")
    parser.add_argument("--row-count", "-c", type=int, default=None, help="Override the default row count for all tables")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for reproducible data generation (default: 42)")
    parser.add_argument("--rules", default=None, help="Path to custom generation rules JSON file")
    args = parser.parse_args()
    
    verbose = args.verbose
    model = args.model
    schema_name = args.schema_name
    custom_row_count = args.row_count
    seed = args.seed
    rules_file = args.rules
    
    print("Testing Data Synthesis Agent...")
    print(f"Using model: {model}")
    print(f"Using seed: {seed}")
    if custom_row_count:
        print(f"Overriding row count to {custom_row_count} for all tables")
    if rules_file:
        print(f"Using custom generation rules from: {rules_file}")
    
    # Create a unique run ID for this test
    run_id = "test_data_synth_agent"
    
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
    
    # Load custom rules if specified
    custom_rules = None
    if rules_file:
        try:
            with open(rules_file, 'r') as f:
                rules_data = json.load(f)
                # Convert to the format expected by the DataSynthAgent
                custom_rules = {}
                for rule in rules_data.get("rules", []):
                    target = rule.get("target", "")
                    # If target is a table.column format, extract the table
                    table_name = target.split(".")[0] if "." in target else target
                    if table_name:
                        if table_name not in custom_rules:
                            custom_rules[table_name] = []
                        custom_rules[table_name].append(rule)
            print(f"Loaded {sum(len(rules) for rules in custom_rules.values())} rules for {len(custom_rules)} tables")
        except Exception as e:
            print(f"Error loading rules file: {str(e)}")
            custom_rules = None

    # Step 1: Parse the SQL file to get the schema
    print(f"\n=== Step 1: Parsing SQL schema from {sql_file} ===")
    schema_parser = SchemaParseAgent(
        run_id=run_id,
        artifacts_dir=test_artifacts_dir,
        seed=seed,
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
        llm_model=model,
        seed=seed
    )
    
    # Load the reference data
    enriched_schema = ref_data_agent.run(
        schema=schema,
        ref_data_path=ref_data_file,
        intelligent_mapping=True
    )
    
    # Save the enriched schema
    enriched_schema_file = os.path.join(test_artifacts_dir, "enriched_schema.json")
    enriched_schema.save_to_file(enriched_schema_file)
    print(f"Saved enriched schema to {enriched_schema_file}")
    
    # Step 3: Generate synthetic data
    print("\n=== Step 3: Generating synthetic data ===")
    data_synth_agent = DataSynthAgent(
        run_id=run_id,
        artifacts_dir=test_artifacts_dir,
        llm_provider="openai",
        llm_model=model,
        seed=seed
    )
    
    # Set custom row counts if specified
    row_counts = None
    if custom_row_count:
        row_counts = {table.name: custom_row_count for table in enriched_schema.tables}
    
    # Generate data for each table
    output_dir = os.path.join(test_artifacts_dir, "generated_data")
    ensure_directory(output_dir)
    output_files = data_synth_agent.run(
        schema=enriched_schema,
        output_dir=output_dir,
        row_counts=row_counts,
        custom_rules=custom_rules
    )
    
    # Step 4: Summarize the generated data
    print("\n=== Step 4: Summary of generated data ===")
    total_rows = 0
    for table_name, file_path in output_files.items():
        # Count lines in the CSV (header + data rows)
        with open(file_path, 'r') as f:
            line_count = sum(1 for line in f)
        
        # Subtract 1 for the header row
        row_count = max(0, line_count - 1)
        total_rows += row_count
        
        print(f"Table {table_name}: {row_count} rows generated -> {file_path}")
    
    print(f"\nTotal: {total_rows} rows of synthetic data generated across {len(output_files)} tables")
    print(f"Data files saved to: {output_dir}")
    
    # Step 5: Show sample of generated data for one table
    if output_files:
        print("\n=== Step 5: Sample of generated data ===")
        # Choose a table to show (preferably a data table with actual rows)
        tables_with_rows = {name: path for name, path in output_files.items() 
                         if os.path.getsize(path) > 5}  # Filter tables with content
        
        if tables_with_rows:
            # Try to find a data table (non-reference table) with rows
            data_tables = [name for name in tables_with_rows.keys() 
                         if not any(name == ref_table.name for ref_table in enriched_schema.get_reference_tables())]
            
            sample_table = data_tables[0] if data_tables else list(tables_with_rows.keys())[0]
            sample_file = output_files[sample_table]
            
            print(f"Sample data from table: {sample_table}")
            try:
                with open(sample_file, 'r') as f:
                    # Read header and up to 5 data rows, safely handling StopIteration
                    lines = []
                    for _ in range(6):
                        try:
                            lines.append(next(f))
                        except StopIteration:
                            break
                    
                    if lines:
                        # Print header
                        print(f"  Header: {lines[0].strip()}")
                        
                        # Print data rows
                        if len(lines) > 1:
                            print("  Data rows:")
                            for i, line in enumerate(lines[1:], 1):
                                print(f"  {i}. {line.strip()}")
                        else:
                            print("  No data rows found in the file.")
            except Exception as e:
                print(f"  Error reading sample data: {str(e)}")
        else:
            print("No tables with data rows were generated. Check the agent logs for details.")

    print("\nData Synthesis Agent demonstration complete!")


if __name__ == "__main__":
    main() 