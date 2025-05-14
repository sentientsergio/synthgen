# Task: Map Reference Data to Schema Tables

You are a data expert who needs to map reference data to the appropriate tables in a database schema.

## Schema Information

```json
{schema_json}
```

## Reference Data Content

```
{ref_data_content}
```

## Instructions

1. Analyze the schema and reference data
2. Identify which reference data tables should map to which schema tables
3. Consider table name similarity, column names, and data content
4. Create a mapping in JSON format

## Output Format

Return ONLY a JSON object with the following structure:

```json
{{
  "mapping": {{
    "RefSchemaName.RefTableName": "SchemaTableName",
    "RefSchemaName.AnotherRefTable": "AnotherSchemaTable"
  }}
}}
```

If you can't find a matching schema table for a reference table, omit it from the mapping.
