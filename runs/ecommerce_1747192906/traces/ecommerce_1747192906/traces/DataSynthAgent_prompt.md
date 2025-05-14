# Synthetic Data Generation Task

## Objective

Generate 10 rows of synthetic data for the SQL Server table 'EmailSubscription'.

## Table Structure

```json
{
  "name": "EmailSubscription",
  "columns": [
    {
      "name": "SubscriptionID",
      "data_type": "INTEGER",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": true,
      "is_computed": false,
      "description": "Unique identifier for each subscription."
    },
    {
      "name": "UserID",
      "data_type": "INTEGER",
      "nullable": true,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Identifier for the user associated with the subscription."
    },
    {
      "name": "Email",
      "data_type": "NVARCHAR",
      "nullable": false,
      "length": 100,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Email address of the subscriber."
    },
    {
      "name": "IsSubscribed",
      "data_type": "BIT",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": "1",
      "is_identity": false,
      "is_computed": false,
      "description": "Indicates if the user is currently subscribed."
    },
    {
      "name": "SubscriptionDate",
      "data_type": "DATETIME",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": "GETDATE()",
      "is_identity": false,
      "is_computed": false,
      "description": "Date when the subscription was created."
    },
    {
      "name": "UnsubscriptionDate",
      "data_type": "DATETIME",
      "nullable": true,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Date when the subscription was cancelled."
    }
  ],
  "primary_key": {
    "name": "PK_EmailSubscription",
    "columns": [
      "SubscriptionID"
    ]
  },
  "foreign_keys": [
    {
      "name": "FK_EmailSubscription_User",
      "columns": [
        "UserID"
      ],
      "ref_table": "User",
      "ref_columns": [
        "UserID"
      ],
      "on_delete": "SET NULL",
      "on_update": null
    }
  ],
  "indices": [],
  "check_constraints": [],
  "unique_constraints": [],
  "default_constraints": [],
  "reference_data": null,
  "description": "Table for managing email subscriptions of users."
}
```

## Foreign Key Reference Data

No foreign key references with reference data.

## Instructions

1. Generate 10 rows of realistic data for this table
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
  {
    "column1": "value1",
    "column2": 42,
    ...
  },
  ...
]
```


