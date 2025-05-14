# Synthetic Data Generation Task

## Objective

Generate 3 rows of synthetic data for the SQL Server table 'OrderDetail'.

## Table Structure

```json
{
  "name": "OrderDetail",
  "columns": [
    {
      "name": "OrderDetailID",
      "data_type": "INTEGER",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": true,
      "is_computed": false,
      "description": "Primary key for order detail"
    },
    {
      "name": "OrderID",
      "data_type": "INTEGER",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Order ID associated with the detail"
    },
    {
      "name": "ProductID",
      "data_type": "INTEGER",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Product ID associated with the detail"
    },
    {
      "name": "Quantity",
      "data_type": "INTEGER",
      "nullable": false,
      "length": null,
      "precision": null,
      "scale": null,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Quantity of the product ordered"
    },
    {
      "name": "UnitPrice",
      "data_type": "DECIMAL",
      "nullable": false,
      "length": null,
      "precision": 10,
      "scale": 2,
      "default_value": null,
      "is_identity": false,
      "is_computed": false,
      "description": "Unit price of the product"
    },
    {
      "name": "Discount",
      "data_type": "DECIMAL",
      "nullable": false,
      "length": null,
      "precision": 5,
      "scale": 2,
      "default_value": "0",
      "is_identity": false,
      "is_computed": false,
      "description": "Discount applied to the product"
    }
  ],
  "primary_key": {
    "name": "PK_OrderDetail",
    "columns": [
      "OrderDetailID"
    ]
  },
  "foreign_keys": [
    {
      "name": "FK_OrderDetail_Order",
      "columns": [
        "OrderID"
      ],
      "ref_table": "Order",
      "ref_columns": [
        "OrderID"
      ],
      "on_delete": "CASCADE",
      "on_update": null
    },
    {
      "name": "FK_OrderDetail_Product",
      "columns": [
        "ProductID"
      ],
      "ref_table": "Product",
      "ref_columns": [
        "ProductID"
      ],
      "on_delete": null,
      "on_update": null
    }
  ],
  "indices": [],
  "check_constraints": [
    {
      "name": "CK_OrderDetail_Quantity",
      "definition": "Quantity > 0"
    },
    {
      "name": "CK_OrderDetail_UnitPrice",
      "definition": "UnitPrice >= 0"
    },
    {
      "name": "CK_OrderDetail_Discount",
      "definition": "Discount >= 0 AND Discount <= 100"
    }
  ],
  "unique_constraints": [],
  "default_constraints": [],
  "reference_data": null,
  "description": "Order Detail table"
}
```

## Foreign Key Reference Data

No foreign key references with reference data.

## Instructions

1. Generate 3 rows of realistic data for this table
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


