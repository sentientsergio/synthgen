# Synthetic Data Generation Task

## Objective

Generate {row_count} rows of synthetic data for the SQL Server table '{table_name}'.

## Table Structure

```json
{table_info}
```

## Foreign Key Reference Data

{fk_section}

## Instructions

1. Generate {row_count} rows of realistic data for this table
2. Follow all constraints:
   - Respect data types and length limits for each column
   - Ensure primary key values are unique
   - Reference valid foreign key values from related tables
   - Follow check constraints
   - Respect NOT NULL constraints
3. When using reference data with weights, distribute foreign key references proportionally
4. Create realistic and varied values, avoid repetitive patterns
5. For columns that are part of both a primary key and foreign key, ensure values don't conflict

## Output Format

Return ONLY a JSON array of objects, with each object representing a row.
Each object should have column names as keys and values should be appropriate for the column data type.

Example:

```json
[
  {{
    "column1": "value1",
    "column2": 42,
    ...
  }},
  ...
]
```

{custom_rules_section}
