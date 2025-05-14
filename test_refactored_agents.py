#!/usr/bin/env python3
"""
Test script to verify that all agents still work after refactoring.

This script runs the Schema Parser Agent, Reference Data Agent, and Data Synthesis Agent
in sequence to ensure they're functioning correctly with the new externalized prompts
and standardized directory structure.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.schema_parse_agent import SchemaParseAgent
from agents.ref_data_agent import RefDataAgent
from agents.data_synth_agent import DataSynthAgent
from models.ir import Schema

# Test configuration
RUN_ID = "test_refactored_agents"
SQL_FILE = "samples/sql/sample.sql"
REF_DATA_FILE = "tests/fixtures/sample_ref_data.csv"
ARTIFACTS_DIR = "runs"
ROW_COUNT = 3  # Small number for quick testing

def main():
    """Run the test for all agents."""
    print("Testing refactored agents...")
    print(f"Using run_id: {RUN_ID}")
    print(f"Using SQL file: {SQL_FILE}")
    print(f"Using reference data: {REF_DATA_FILE}")
    
    # Step 1: Test Schema Parser Agent
    print("\n=== Testing Schema Parser Agent ===")
    schema_parser = SchemaParseAgent(
        run_id=RUN_ID,
        artifacts_dir=ARTIFACTS_DIR,
        seed=42
    )
    
    schema = schema_parser.run(SQL_FILE, schema_name="SampleOrdersDB")
    print(f"Schema parsed successfully with {len(schema.tables)} tables")
    
    # Step 2: Test Reference Data Agent
    print("\n=== Testing Reference Data Agent ===")
    ref_data_agent = RefDataAgent(
        run_id=RUN_ID,
        artifacts_dir=ARTIFACTS_DIR,
        seed=42
    )
    
    enriched_schema = ref_data_agent.run(
        schema=schema,
        ref_data_path=REF_DATA_FILE,
        intelligent_mapping=True
    )
    
    ref_tables = [table for table in enriched_schema.tables if table.reference_data]
    print(f"Reference data loaded successfully for {len(ref_tables)} tables")
    
    # Step 3: Test Data Synthesis Agent
    print("\n=== Testing Data Synthesis Agent ===")
    data_synth_agent = DataSynthAgent(
        run_id=RUN_ID,
        artifacts_dir=ARTIFACTS_DIR,
        seed=42
    )
    
    # Override row counts for faster testing
    row_counts = {table.name: ROW_COUNT for table in enriched_schema.tables}
    
    output_dir = os.path.join(ARTIFACTS_DIR, RUN_ID, "outputs", "tables")
    output_files = data_synth_agent.run(
        schema=enriched_schema,
        output_dir=output_dir,
        row_counts=row_counts
    )
    
    print(f"Data generated successfully for {len(output_files)} tables")
    print(f"Output files saved to: {output_dir}")
    
    # Check if all agents succeeded
    if (len(schema.tables) > 0 and 
        len(output_files) > 0):
        print("\n✅ All agents are working correctly after refactoring!")
    else:
        print("\n❌ Some agents may not be working correctly. Check the logs for details.")
    
    # Print locations where artifacts can be found
    print("\nArtifacts can be found in the following locations:")
    print(f"- Prompts: {os.path.join(ARTIFACTS_DIR, RUN_ID, 'traces')}")
    print(f"- Schema IR: {os.path.join(ARTIFACTS_DIR, RUN_ID, 'ir')}")
    print(f"- Generated Data: {os.path.join(ARTIFACTS_DIR, RUN_ID, 'outputs', 'tables')}")

if __name__ == "__main__":
    main() 