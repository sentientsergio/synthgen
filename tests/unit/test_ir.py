#!/usr/bin/env python3
"""
Simple test script for the Intermediate Representation (IR) model.

This script demonstrates the basic functionality of the IR model
to ensure it works correctly before proceeding with more complex
components.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.ir import (
    Column,
    ColumnType,
    PrimaryKey,
    ForeignKey,
    CheckConstraint,
    Table,
    GenerationRule,
    Schema,
    ReferenceData
)


def create_sample_schema() -> Schema:
    """Create a sample Schema instance for testing.
    
    Returns:
        A sample Schema instance
    """
    # Define columns for Customers table
    customer_columns = [
        Column(
            name="CustomerID",
            data_type=ColumnType.INTEGER,
            nullable=False,
            is_identity=True
        ),
        Column(
            name="FirstName",
            data_type=ColumnType.NVARCHAR,
            length=50,
            nullable=False
        ),
        Column(
            name="LastName",
            data_type=ColumnType.NVARCHAR,
            length=50,
            nullable=False
        ),
        Column(
            name="Email",
            data_type=ColumnType.NVARCHAR,
            length=100,
            nullable=True
        ),
        Column(
            name="StatusCode",
            data_type=ColumnType.CHAR,
            length=1,
            nullable=False,
            default_value="'A'"
        )
    ]
    
    # Define primary key for Customers
    customer_pk = PrimaryKey(
        name="PK_Customers",
        columns=["CustomerID"]
    )
    
    # Define CHECK constraint for StatusCode
    status_check = CheckConstraint(
        name="CK_Customers_StatusCode",
        definition="StatusCode IN ('A', 'I', 'D')"
    )
    
    # Create Customers table
    customers_table = Table(
        name="Customers",
        columns=customer_columns,
        primary_key=customer_pk,
        check_constraints=[status_check],
        description="Stores customer information"
    )
    
    # Define columns for CustomerStatus table (reference table)
    status_columns = [
        Column(
            name="StatusCode",
            data_type=ColumnType.CHAR,
            length=1,
            nullable=False
        ),
        Column(
            name="StatusDescription",
            data_type=ColumnType.NVARCHAR,
            length=50,
            nullable=False
        )
    ]
    
    # Define primary key for CustomerStatus
    status_pk = PrimaryKey(
        name="PK_CustomerStatus",
        columns=["StatusCode"]
    )
    
    # Define reference data for CustomerStatus
    status_data = ReferenceData(
        rows=[
            {"StatusCode": "A", "StatusDescription": "Active"},
            {"StatusCode": "I", "StatusDescription": "Inactive"},
            {"StatusCode": "D", "StatusDescription": "Deleted"}
        ]
    )
    
    # Create CustomerStatus table
    status_table = Table(
        name="CustomerStatus",
        columns=status_columns,
        primary_key=status_pk,
        reference_data=status_data,
        description="Customer status reference table"
    )
    
    # Define foreign key from Customers to CustomerStatus
    customer_status_fk = ForeignKey(
        name="FK_Customers_CustomerStatus",
        columns=["StatusCode"],
        ref_table="CustomerStatus",
        ref_columns=["StatusCode"],
        on_delete="NO ACTION",
        on_update="CASCADE"
    )
    
    # Add foreign key to Customers table
    customers_table.foreign_keys.append(customer_status_fk)
    
    # Create a generation rule
    email_rule = GenerationRule(
        rule_id="rule-001",
        rule_type="pattern",
        target="Customers.Email",
        definition={
            "pattern": "{firstName}.{lastName}@example.com",
            "lowercase": True
        },
        description="Generate email addresses based on first and last name"
    )
    
    # Create the schema
    schema = Schema(
        name="SampleSchema",
        tables=[customers_table, status_table],
        generation_rules=[email_rule],
        description="Sample schema for testing"
    )
    
    return schema


def test_serialization():
    """Test serialization to and from JSON."""
    print("\n=== Testing IR serialization ===")
    
    # Create sample schema
    schema = create_sample_schema()
    
    # Serialize to JSON
    json_str = schema.to_json(indent=2)
    print(f"Serialized schema (excerpt):\n{json_str[:500]}...\n")
    
    # Deserialize from JSON
    deserialized = Schema.from_json(json_str)
    
    # Verify deserialization
    assert deserialized.name == schema.name, "Schema name doesn't match"
    assert len(deserialized.tables) == len(schema.tables), "Table count doesn't match"
    assert len(deserialized.generation_rules) == len(schema.generation_rules), "Rule count doesn't match"
    print("✅ Serialization and deserialization work correctly")


def test_file_persistence():
    """Test saving and loading from file."""
    print("\n=== Testing file persistence ===")
    
    # Create sample schema
    schema = create_sample_schema()
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
        # Save schema to file
        schema.save_to_file(temp_file.name)
        print(f"Saved schema to {temp_file.name}")
        
        # Load schema from file
        loaded = Schema.load_from_file(temp_file.name)
        
        # Verify loading worked
        assert loaded.name == schema.name, "Schema name doesn't match"
        assert len(loaded.tables) == len(schema.tables), "Table count doesn't match"
        print("✅ File persistence works correctly")


def test_query_methods():
    """Test schema query methods."""
    print("\n=== Testing schema query methods ===")
    
    # Create sample schema
    schema = create_sample_schema()
    
    # Test get_table
    customers_table = schema.get_table("Customers")
    assert customers_table is not None, "Customers table not found"
    assert customers_table.name == "Customers", "Table name doesn't match"
    print("✅ get_table works correctly")
    
    # Debug output for tables
    for table in schema.tables:
        print(f"Table: {table.name}, Is Reference: {table.is_reference_table}")
        if table.name == "CustomerStatus":
            print(f"  Has reference_data: {table.reference_data is not None}")
            if table.reference_data:
                print(f"  Has rows attribute: {hasattr(table.reference_data, 'rows')}")
                print(f"  Rows: {table.reference_data.rows}")
    
    # Test get_reference_tables
    ref_tables = schema.get_reference_tables()
    print(f"Reference tables: {[t.name for t in ref_tables]}")
    assert len(ref_tables) == 1, "Expected 1 reference table"
    assert ref_tables[0].name == "CustomerStatus", "Reference table name doesn't match"
    print("✅ get_reference_tables works correctly")
    
    # Test get_data_tables
    data_tables = schema.get_data_tables()
    assert len(data_tables) == 1, "Expected 1 data table"
    assert data_tables[0].name == "Customers", "Data table name doesn't match"
    print("✅ get_data_tables works correctly")
    
    # Test get_column
    email_column = customers_table.get_column("Email")
    assert email_column is not None, "Email column not found"
    assert email_column.name == "Email", "Column name doesn't match"
    assert email_column.data_type == ColumnType.NVARCHAR, "Column type doesn't match"
    print("✅ get_column works correctly")


def main():
    """Run all tests."""
    print("Testing IR model...")
    
    test_serialization()
    test_file_persistence()
    test_query_methods()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main() 