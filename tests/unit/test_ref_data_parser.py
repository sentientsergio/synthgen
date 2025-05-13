#!/usr/bin/env python3
"""
Unit tests for Reference Data Parser utilities.

This module tests the functionality of the reference data parser,
including the multi-table CSV format parsing and conversion to IR.
"""

import sys
import os
from pathlib import Path
import json

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import unittest
from utils.ref_data_parser import (
    parse_multi_table_csv,
    csv_to_ir,
    update_schema_with_reference_data
)
from models.ir import Schema, Table, Column, ColumnType, ReferenceData


class TestRefDataParser(unittest.TestCase):
    """Tests for the reference data parser utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.fixtures_dir = os.path.join(project_root, "tests", "fixtures")
        self.sample_data_file = os.path.join(self.fixtures_dir, "sample_ref_data.csv")
        
        # Define expected schema and table names for test data
        self.expected_schema_name = "Reference"
        self.expected_tables = ["Countries", "Languages", "Currencies"]
        
        # Define expected data structure (partial) for verification
        self.expected_data = {
            "Reference": {
                "Countries": {
                    "count": 8,
                    "columns": ["CountryCode", "CountryName", "Continent"],
                    "sample_row": {
                        "index": 0,
                        "CountryCode": "US"
                    }
                },
                "Languages": {
                    "count": 7,
                    "columns": ["LanguageCode", "LanguageName", "NativeName"],
                    "sample_row": {
                        "index": 2,
                        "LanguageCode": "DE"
                    }
                },
                "Currencies": {
                    "count": 7,
                    "columns": ["CurrencyCode", "CurrencyName", "Symbol"],
                    "sample_row": {
                        "index": 1,
                        "CurrencyCode": "EUR"
                    }
                }
            }
        }

    def test_parse_multi_table_csv(self):
        """Test parsing a multi-table CSV file."""
        schemas = parse_multi_table_csv(self.sample_data_file)
        
        # Check that we got the expected schema
        self.assertIn(self.expected_schema_name, schemas)
        schema_data = schemas[self.expected_schema_name]
        
        # Check that we got all the expected tables
        for table_name in self.expected_tables:
            self.assertIn(table_name, schema_data)
        
        # Check the structure and sampling of data for each table
        for table_name, expected in self.expected_data[self.expected_schema_name].items():
            table_data = schema_data[table_name]
            
            # Check row count
            self.assertEqual(len(table_data), expected["count"], 
                             f"Table {table_name} should have {expected['count']} rows")
            
            # Check columns
            self.assertListEqual(sorted(table_data[0].keys()), sorted(expected["columns"]),
                               f"Table {table_name} should have expected columns")
            
            # Check sample data
            sample = expected["sample_row"]
            row_index = sample["index"]
            for key, value in sample.items():
                if key != "index":
                    self.assertEqual(table_data[row_index][key], value,
                                   f"Sample value mismatch in {table_name} at row {row_index} for {key}")

    def test_csv_to_ir(self):
        """Test converting a multi-table CSV file to IR Schema."""
        ir_schemas = csv_to_ir(self.sample_data_file)
        
        # Check that we got the expected schema
        self.assertIn(self.expected_schema_name, ir_schemas)
        schema = ir_schemas[self.expected_schema_name]
        
        # Check the schema properties
        self.assertEqual(schema.name, self.expected_schema_name)
        self.assertEqual(len(schema.tables), len(self.expected_tables))
        
        # Check that we have all the expected tables
        for table_name in self.expected_tables:
            table = schema.get_table(table_name)
            self.assertIsNotNone(table, f"Table {table_name} should exist in schema")
        
        # Check table properties for each expected table
        for table_name, expected in self.expected_data[self.expected_schema_name].items():
            table = schema.get_table(table_name)
            
            # Check columns
            column_names = [col.name for col in table.columns]
            self.assertListEqual(sorted(column_names), sorted(expected["columns"]),
                               f"Table {table_name} should have expected columns")
            
            # Check reference data
            self.assertIsNotNone(table.reference_data)
            self.assertEqual(len(table.reference_data.rows), expected["count"],
                           f"Table {table_name} should have {expected['count']} rows of reference data")
            
            # Check sample data
            sample = expected["sample_row"]
            row_index = sample["index"]
            for key, value in sample.items():
                if key != "index":
                    self.assertEqual(table.reference_data.rows[row_index][key], value,
                                   f"Sample value mismatch in {table_name} at row {row_index} for {key}")
            
            # Check that the table is correctly identified as a reference table
            self.assertTrue(table.is_reference_table)

    def test_update_schema_with_reference_data(self):
        """Test updating an existing schema with reference data."""
        # Create a simple schema with just the table structure
        schema = Schema(name="Reference", tables=[])
        
        # Add a Countries table without reference data
        countries_table = Table(
            name="Countries",
            columns=[
                Column(name="CountryCode", data_type=ColumnType.NVARCHAR, length=2),
                Column(name="CountryName", data_type=ColumnType.NVARCHAR, length=100),
                Column(name="Continent", data_type=ColumnType.NVARCHAR, length=50)
            ]
        )
        schema.tables.append(countries_table)
        
        # Add a Languages table without reference data
        languages_table = Table(
            name="Languages",
            columns=[
                Column(name="LanguageCode", data_type=ColumnType.NVARCHAR, length=2),
                Column(name="LanguageName", data_type=ColumnType.NVARCHAR, length=100),
                Column(name="NativeName", data_type=ColumnType.NVARCHAR, length=100)
            ]
        )
        schema.tables.append(languages_table)
        
        # Update the schema with reference data
        updated_schema = update_schema_with_reference_data(schema, self.sample_data_file)
        
        # Check that reference data was added to both tables
        for table_name, expected in self.expected_data[self.expected_schema_name].items():
            if table_name in ["Countries", "Languages"]:  # Only these are in our schema
                table = updated_schema.get_table(table_name)
                self.assertIsNotNone(table.reference_data)
                self.assertEqual(len(table.reference_data.rows), expected["count"])
                
                # Check sample data
                sample = expected["sample_row"]
                row_index = sample["index"]
                for key, value in sample.items():
                    if key != "index":
                        self.assertEqual(table.reference_data.rows[row_index][key], value,
                                       f"Sample value mismatch in {table_name} at row {row_index} for {key}")
        
        # Check that the Currencies table wasn't added (since it wasn't in the original schema)
        self.assertIsNone(updated_schema.get_table("Currencies"))
        
    def test_schema_namespace_isolation(self):
        """Test that schemas are properly isolated."""
        # Create an empty schema file with tables in a different schema
        test_file_path = os.path.join(self.fixtures_dir, "temp_test_schema.csv")
        try:
            # Create a temp file with tables in two different schemas
            with open(test_file_path, 'w') as f:
                f.write("# [Schema1.Table1]\n")
                f.write("Col1, Col2\n")
                f.write("Val1, Val2\n\n")
                f.write("# [Schema2.Table1]\n")  # Same table name, different schema
                f.write("Col1, Col2\n")
                f.write("OtherVal1, OtherVal2\n")
            
            # Parse the file
            schemas = parse_multi_table_csv(test_file_path)
            
            # Check that we have two separate schemas
            self.assertIn("Schema1", schemas)
            self.assertIn("Schema2", schemas)
            
            # Check that each schema has its own Table1
            self.assertIn("Table1", schemas["Schema1"])
            self.assertIn("Table1", schemas["Schema2"])
            
            # Check that the data is different
            self.assertEqual(schemas["Schema1"]["Table1"][0]["Col1"], "Val1")
            self.assertEqual(schemas["Schema2"]["Table1"][0]["Col1"], "OtherVal1")
            
            # Convert to IR
            ir_schemas = csv_to_ir(test_file_path)
            
            # Check that we have two separate schema objects
            self.assertIn("Schema1", ir_schemas)
            self.assertIn("Schema2", ir_schemas)
            
            # Verify content
            schema1 = ir_schemas["Schema1"]
            schema2 = ir_schemas["Schema2"]
            
            self.assertEqual(schema1.tables[0].reference_data.rows[0]["Col1"], "Val1")
            self.assertEqual(schema2.tables[0].reference_data.rows[0]["Col1"], "OtherVal1")
            
        finally:
            # Clean up
            if os.path.exists(test_file_path):
                os.remove(test_file_path)


if __name__ == "__main__":
    unittest.main() 