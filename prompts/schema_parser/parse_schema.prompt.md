# SQL Schema Analysis Task

## Objective

Analyze the provided SQL Server CREATE script and transform it into a structured Schema representation.

## Schema Name

{schema_name}

## SQL Script to Analyze

```sql
{sql_script}
```

## Instructions

1. Extract all tables from the script
2. For each table, identify:
   - Table name and description
   - All columns with their names, data types, nullability, etc.
   - Primary key constraints
   - Foreign key constraints
   - Check constraints
3. Determine relationships between tables
4. Format the output as a JSON object matching the provided schema template EXACTLY

## Output Format Requirements

Your output MUST conform to this exact structure, with these exact property names:

```json
{{
  "name": "SchemaName",  // <-- This must be exactly "name", not "schemaName"
  "tables": [            // <-- This must be exactly "tables", not "Tables"
    {{
      "name": "TableName",  // <-- This must be exactly "name", not "tableName"
      "description": "Description of the table",
      "columns": [          // <-- This must be exactly "columns", not "Columns"
        {{
          "name": "ColumnName",
          "data_type": {{   // <-- This must be a nested object with the format below
            "name": "DataTypeName", // e.g., "INTEGER", "VARCHAR", etc.
            "length": 50,    // Optional, for string types
            "precision": 10, // Optional, for numeric types
            "scale": 2       // Optional, for numeric types
          }},
          "nullable": true,  // Boolean - must be exactly "nullable", not "isNullable"
          "default_value": "DefaultValue",  // Optional
          "is_identity": false,  // Boolean
          "description": "Description of the column"  // Optional
        }}
      ],
      "primary_key": {{   // <-- Optional, null if not present
        "name": "PKName",
        "columns": ["ColumnName"]
      }},
      "foreign_keys": [   // <-- Array, empty if not present
        {{
          "name": "FKName",
          "columns": ["ColumnName"],
          "ref_table": "ReferencedTable",
          "ref_columns": ["ReferencedColumn"],
          "on_delete": "OnDeleteAction",  // Optional
          "on_update": "OnUpdateAction"   // Optional
        }}
      ],
      "check_constraints": [   // <-- Array, empty if not present
        {{
          "name": "CheckName",
          "definition": "CheckDefinition"
        }}
      ],
      "is_reference_table": false  // <-- Boolean
    }}
  ],
  "description": "Description of the overall schema",
  "generation_rules": []  // <-- Empty array for this initial schema
}}
```

Use your understanding of SQL Server syntax to properly interpret the script and create an accurate representation of the database schema. Include all constraints, even if they're defined separately from the table creation.

IMPORTANT: Follow the EXACT format above, including the exact property names as shown in the example. Ensure your response is a valid JSON object that exactly follows this structure.
