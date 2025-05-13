#!/usr/bin/env python3
"""
Simple test script for the Reference Data Parser utility.

This script demonstrates how to use the Reference Data Parser utility
to load reference data from multi-table CSV files into IR Schema objects.
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

from utils.ref_data_parser import parse_multi_table_csv, csv_to_ir, update_schema_with_reference_data
from utils.file_io import ensure_directory
from models.ir import Schema


def main():
    """Run a demonstration of the Reference Data Parser utility."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Reference Data Parser utility")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--csv-file", "-f", default=None, help="Specify a custom CSV file to parse")
    args = parser.parse_args()
    
    verbose = args.verbose
    
    print("Testing Reference Data Parser...")
    
    # Path to sample CSV file
    if args.csv_file:
        csv_file = args.csv_file
    else:
        csv_file = os.path.join(project_root, "tests", "fixtures", "sample_ref_data.csv")
    
    # Ensure artifacts directory exists
    artifacts_dir = os.path.join(project_root, "artifacts", "ref_data_test")
    ensure_directory(artifacts_dir)
    
    print(f"Parsing multi-table CSV file: {csv_file}")
    
    # Step 1: Simply parse the multi-table CSV file to see the table data
    schemas = parse_multi_table_csv(csv_file)
    
    print("\nParsed Schemas and Tables:")
    for schema_name, tables in schemas.items():
        print(f"Schema: {schema_name}")
        for table_name, rows in tables.items():
            print(f"  - Table: {table_name} ({len(rows)} rows)")
            
            if verbose:
                print(f"\n    {schema_name}.{table_name} Contents:")
                for i, row in enumerate(rows):
                    if i < 3:  # Only show first 3 rows if there are many
                        print(f"      {row}")
                    elif i == 3:
                        print(f"      ... ({len(rows) - 3} more rows)")
    
    # Step 2: Convert the CSV file to IR Schema objects
    ir_schemas = csv_to_ir(csv_file)
    
    print("\nCreated IR Schemas:")
    for schema_name, schema in ir_schemas.items():
        print(f"Schema: {schema_name}")
        print(f"  - Tables: {len(schema.tables)}")
        
        for table in schema.tables:
            print(f"\n  Table: {table.name}")
            print(f"    Columns: {[col.name for col in table.columns]}")
            print(f"    Column Types: {[col.data_type.name for col in table.columns]}")
            print(f"    Reference Data Rows: {len(table.reference_data.rows)}")
        
        # Save each schema to a JSON file
        schema_file = os.path.join(artifacts_dir, f"{schema_name}_schema.json")
        schema.save_to_file(schema_file)
        print(f"\nSaved IR Schema to: {schema_file}")
    
    # Step 3: Demonstrate updating an existing schema with reference data
    print("\nDemonstrating updating an existing schema with reference data...")
    
    # Get the first schema as an example
    first_schema_name = next(iter(ir_schemas.keys()))
    example_schema = ir_schemas[first_schema_name]
    
    # Create a simple schema with just the structure (no data)
    simple_schema = Schema(name=first_schema_name, tables=[])
    for table in example_schema.tables:
        # Create copies of the tables but without reference data
        simple_table = table.to_dict()
        simple_table["reference_data"] = None
        simple_schema.tables.append(Schema.from_dict({"name": first_schema_name, "tables": [simple_table]}).tables[0])
    
    # Save the simple schema without reference data
    simple_schema_file = os.path.join(artifacts_dir, "simple_schema.json")
    simple_schema.save_to_file(simple_schema_file)
    print(f"  - Created simple schema without reference data: {simple_schema_file}")
    
    # Update the simple schema with reference data
    updated_schema = update_schema_with_reference_data(simple_schema, csv_file)
    
    # Save the updated schema
    updated_schema_file = os.path.join(artifacts_dir, "updated_schema.json")
    updated_schema.save_to_file(updated_schema_file)
    print(f"  - Updated schema with reference data: {updated_schema_file}")
    
    # Step 4: Create a simple example reference data file for demonstration
    demo_file_path = os.path.join(artifacts_dir, "demo_ref_data.csv")
    with open(demo_file_path, 'w') as f:
        f.write("# [Sales.Regions]\n")
        f.write("RegionID, RegionName, CountryCode\n")
        f.write("1, North America, US\n")
        f.write("2, Europe, UK\n")
        f.write("3, Asia-Pacific, JP\n\n")
        
        f.write("# [Sales.SalesPersons]\n")
        f.write("SalesPersonID, FirstName, LastName, RegionID\n")
        f.write("1, John, Smith, 1\n")
        f.write("2, Emma, Johnson, 2\n")
        f.write("3, Robert, Williams, 3\n")
    
    print(f"\nCreated a demo reference data file: {demo_file_path}")
    print("The file contains two tables in the Sales schema:")
    print("  - Regions: Contains region information")
    print("  - SalesPersons: Contains sales person information with references to regions")
    
    # Parse and convert the demo file
    demo_schemas = csv_to_ir(demo_file_path)
    
    # Save the demo schema
    if "Sales" in demo_schemas:
        demo_schema = demo_schemas["Sales"]
        demo_schema_file = os.path.join(artifacts_dir, "sales_schema.json")
        demo_schema.save_to_file(demo_schema_file)
        print(f"\nSaved demo Sales schema to: {demo_schema_file}")
    
    print("\nReference Data Parser demonstration complete!")
    print("\nUsage tips:")
    print("1. Create your reference data in the schema-qualified format shown in the demo file")
    print("2. Use parse_multi_table_csv() to parse the file and examine the data")
    print("3. Use csv_to_ir() to convert the data to IR Schema objects")
    print("4. Use update_schema_with_reference_data() to add reference data to existing schemas")


if __name__ == "__main__":
    main() 