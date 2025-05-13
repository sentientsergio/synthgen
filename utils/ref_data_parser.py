#!/usr/bin/env python3
"""
Reference Data Parser Utility

This module provides utilities for parsing reference data from various formats
and converting it to the Intermediate Representation (IR) format for use in 
SynthGen data generation.

The main format supported is a multi-table CSV format that can contain multiple
tables in a single file, with the following format:

# [SchemaName.TableName]
[column1], [column2], ...
value1, value2, ...
value1, value2, ...

# [SchemaName.TableName2]
[column1], [column2], ...
value1, value2, ...
value1, value2, ...

This utility makes it easy to provide reference data for multiple tables
in a single file, which can then be used to populate the reference_data
field in the IR Schema.
"""

import csv
import io
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from models.ir import Schema, Table, Column, ColumnType, ReferenceData


def parse_multi_table_csv(file_path: Union[str, Path]) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """
    Parse a specially formatted CSV that contains multiple tables.
    
    Format:
    # [SchemaName.TableName]
    [column1], [column2], ...
    value1, value2, ...
    
    # [SchemaName.TableName2]
    [column1], [column2], ...
    value1, value2, ...
    
    Args:
        file_path: Path to the multi-table CSV file
        
    Returns:
        Dictionary mapping schema names to dictionaries of table names to lists of row dictionaries
        {schema_name: {table_name: [row_dict, row_dict, ...], ...}, ...}
    """
    schemas = {}
    current_schema = None
    current_table = None
    current_columns = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Check for table header (# [SchemaName.TableName])
        if line.startswith('#'):
            table_spec = line[1:].strip()
            # Remove brackets if present: [SchemaName.TableName] -> SchemaName.TableName
            if table_spec.startswith('[') and table_spec.endswith(']'):
                table_spec = table_spec[1:-1].strip()
            
            # Split into schema and table
            parts = table_spec.split('.', 1)
            
            if len(parts) == 2:
                # Schema-qualified table
                schema_name, table_name = parts
                schema_name = schema_name.strip()
                table_name = table_name.strip()
            else:
                # Default schema (dbo)
                schema_name = "dbo"
                table_name = table_spec.strip()
            
            current_schema = schema_name
            current_table = table_name
            
            # Initialize schema and table if needed
            if current_schema not in schemas:
                schemas[current_schema] = {}
            
            if current_table not in schemas[current_schema]:
                schemas[current_schema][current_table] = []
            
            # Next line should be column headers
            i += 1
            if i < len(lines):
                # Parse column headers from CSV format
                reader = csv.reader([lines[i].strip()])
                current_columns = [col.strip() for col in next(reader)]
                i += 1
                
                # Read data rows until next table or end
                while i < len(lines):
                    line = lines[i].strip()
                    if not line:
                        i += 1
                        continue
                    if line.startswith('#'):
                        break
                        
                    # Parse data row
                    try:
                        reader = csv.reader([line])
                        values = [val.strip() for val in next(reader)]
                        if len(values) == len(current_columns):
                            row = dict(zip(current_columns, values))
                            schemas[current_schema][current_table].append(row)
                    except Exception as e:
                        print(f"Error parsing line {i+1}: {line} - {str(e)}")
                    i += 1
                continue
        
        i += 1
    
    return schemas


def csv_to_ir(file_path: Union[str, Path], default_schema_name: str = "ReferenceData") -> Dict[str, Schema]:
    """
    Convert a multi-table CSV file to IR Schema format.
    
    This function reads a multi-table CSV file and converts it into
    IR Schema objects, which can be used directly in the SynthGen pipeline.
    
    Args:
        file_path: Path to the multi-table CSV file
        default_schema_name: Name to use for the generated Schema if not specified
        
    Returns:
        Dictionary mapping schema names to IR Schema objects
    """
    schemas_data = parse_multi_table_csv(file_path)
    
    # Create IR Schemas
    ir_schemas = {}
    
    # Process each schema and its tables
    for schema_name, tables in schemas_data.items():
        # Create Schema
        schema = Schema(
            name=schema_name,
            tables=[]
        )
        
        # Add tables to schema
        for table_name, rows in tables.items():
            if not rows:
                continue
                
            # Extract column names from first row
            column_names = list(rows[0].keys())
            
            # Infer column types from data
            column_types = _infer_column_types(rows)
            
            # Create IR Columns
            columns = []
            for col_name in column_names:
                col_type = column_types.get(col_name, ColumnType.UNKNOWN)
                columns.append(Column(
                    name=col_name,
                    data_type=col_type,
                    nullable=False  # Reference data typically doesn't have NULL values
                ))
            
            # Create IR Table with reference data
            table = Table(
                name=table_name,
                columns=columns,
                description=f"Reference data for {schema_name}.{table_name}"
            )
            
            # Add reference data
            table.reference_data = ReferenceData(rows=rows)
            
            # Add table to schema
            schema.tables.append(table)
        
        # Add schema to result
        ir_schemas[schema_name] = schema
    
    return ir_schemas


def _infer_column_types(rows: List[Dict[str, str]]) -> Dict[str, ColumnType]:
    """
    Infer column types from reference data.
    
    This is a simple type inference that checks if values look like
    numbers, dates, or strings.
    
    Args:
        rows: List of data rows
        
    Returns:
        Dictionary mapping column names to inferred ColumnType values
    """
    if not rows:
        return {}
    
    column_types = {}
    
    # Get column names from first row
    column_names = list(rows[0].keys())
    
    for col_name in column_names:
        # Check values for this column across all rows
        values = [row.get(col_name, '') for row in rows if row.get(col_name)]
        
        if not values:
            column_types[col_name] = ColumnType.UNKNOWN
            continue
        
        # Check if all values are integers
        try:
            all_integers = all(str(int(val)) == val.strip() for val in values if val.strip())
            if all_integers:
                column_types[col_name] = ColumnType.INTEGER
                continue
        except ValueError:
            pass
        
        # Check if all values are decimals
        try:
            all_decimals = all(isinstance(float(val), float) for val in values if val.strip())
            if all_decimals:
                column_types[col_name] = ColumnType.DECIMAL
                continue
        except ValueError:
            pass
        
        # Check if all values are dates (this is a simple check)
        date_patterns = ['/', '-']
        might_be_dates = any(
            any(pattern in val for pattern in date_patterns)
            for val in values if val
        )
        if might_be_dates:
            column_types[col_name] = ColumnType.DATE
            continue
        
        # Default to nvarchar for short strings, text for longer ones
        max_length = max(len(val) for val in values if val)
        if max_length <= 255:
            column_types[col_name] = ColumnType.NVARCHAR
        else:
            column_types[col_name] = ColumnType.TEXT
    
    return column_types


def update_schema_with_reference_data(
    target_schema: Schema, 
    ref_data_path: Union[str, Path]
) -> Schema:
    """
    Update an existing schema with reference data from a multi-table CSV file.
    
    This function reads reference data from a CSV file and updates the corresponding
    tables in the schema with that reference data.
    
    Args:
        target_schema: Existing IR Schema to update
        ref_data_path: Path to the multi-table CSV file with reference data
        
    Returns:
        Updated Schema with reference data
    """
    schemas_data = parse_multi_table_csv(ref_data_path)
    
    # Find the schema in the parsed data that matches the target schema
    schema_name = target_schema.name
    
    # If no exact match, try the default schema ('dbo')
    if schema_name not in schemas_data and 'dbo' in schemas_data:
        schema_name = 'dbo'
    
    # If still no match, use the first schema found
    if schema_name not in schemas_data and schemas_data:
        schema_name = next(iter(schemas_data))
    
    # If we found a matching schema, update the tables
    if schema_name in schemas_data:
        tables_data = schemas_data[schema_name]
        
        # Update tables in the schema with reference data
        for table_name, rows in tables_data.items():
            if not rows:
                continue
            
            # Find the table in the schema
            table = target_schema.get_table(table_name)
            if table is None:
                print(f"Warning: Table '{table_name}' not found in schema, skipping")
                continue
            
            # Check if we have a weight column
            has_weights = any("weight" in row.keys() or "Weight" in row.keys() for row in rows)
            
            # If we have weights, apply them
            if has_weights:
                # Standardize weight column name
                for row in rows:
                    if "Weight" in row:
                        row["weight"] = row["Weight"]
                        # Keep original for backward compatibility
                
                distribution_strategy = "weighted_random"
            else:
                distribution_strategy = None
            
            # Update the table with reference data
            table.reference_data = ReferenceData(
                rows=rows,
                distribution_strategy=distribution_strategy,
                description=f"Reference data for {schema_name}.{table_name}"
            )
    
    return target_schema


def directory_to_ir(
    dir_path: Union[str, Path], 
    schema_name: str = "ReferenceData"
) -> Schema:
    """
    Convert all CSV files in a directory to an IR Schema.
    
    This function assumes each CSV file represents a single table,
    with the first row being column headers.
    
    Args:
        dir_path: Path to directory containing CSV files
        schema_name: Name to use for the generated Schema
        
    Returns:
        IR Schema object containing all tables
    """
    schema = Schema(
        name=schema_name,
        tables=[]
    )
    
    # Process each CSV file in the directory
    for filename in os.listdir(dir_path):
        if not filename.lower().endswith('.csv'):
            continue
        
        # Use filename without extension as table name
        table_name = os.path.splitext(filename)[0]
        file_path = os.path.join(dir_path, filename)
        
        # Check if the table name includes a schema (SchemaName.TableName)
        parts = table_name.split('.', 1)
        if len(parts) == 2:
            # Skip if not for this schema
            file_schema, table_name = parts
            if file_schema != schema_name:
                continue
        
        # Read the CSV file
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({k: v.strip() for k, v in row.items()})
        
        if not rows:
            continue
        
        # Extract column names and infer types
        column_names = list(rows[0].keys())
        column_types = _infer_column_types(rows)
        
        # Create IR Columns
        columns = []
        for col_name in column_names:
            col_type = column_types.get(col_name, ColumnType.UNKNOWN)
            columns.append(Column(
                name=col_name,
                data_type=col_type,
                nullable=False
            ))
        
        # Create IR Table with reference data
        table = Table(
            name=table_name,
            columns=columns,
            description=f"Reference data for {schema_name}.{table_name}"
        )
        
        # Add reference data
        table.reference_data = ReferenceData(rows=rows)
        
        # Add table to schema
        schema.tables.append(table)
    
    return schema 