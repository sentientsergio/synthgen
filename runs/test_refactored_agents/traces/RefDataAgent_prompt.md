# Task: Map Reference Data to Schema Tables

You are a data expert who needs to map reference data to the appropriate tables in a database schema.

## Schema Information

```json
{
  "name": "SampleOrdersDB",
  "tables": [
    {
      "name": "CustomerStatus",
      "columns": [
        {
          "name": "StatusCode",
          "data_type": "CHAR",
          "nullable": false,
          "length": 1,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Primary key for customer status"
        },
        {
          "name": "StatusName",
          "data_type": "NVARCHAR",
          "nullable": false,
          "length": 50,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Name of the customer status"
        },
        {
          "name": "StatusDescription",
          "data_type": "NVARCHAR",
          "nullable": true,
          "length": 255,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Description of the customer status"
        },
        {
          "name": "IsActive",
          "data_type": "BIT",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": "1",
          "is_identity": false,
          "is_computed": false,
          "description": "Indicates if the status is active"
        }
      ],
      "primary_key": {
        "name": "PK_CustomerStatus",
        "columns": [
          "StatusCode"
        ]
      },
      "foreign_keys": [],
      "indices": [],
      "check_constraints": [],
      "unique_constraints": [],
      "default_constraints": [],
      "reference_data": null,
      "description": "Customer Status reference table"
    },
    {
      "name": "Customer",
      "columns": [
        {
          "name": "CustomerID",
          "data_type": "INTEGER",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": true,
          "is_computed": false,
          "description": "Primary key for customer"
        },
        {
          "name": "FirstName",
          "data_type": "NVARCHAR",
          "nullable": false,
          "length": 50,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "First name of the customer"
        },
        {
          "name": "LastName",
          "data_type": "NVARCHAR",
          "nullable": false,
          "length": 50,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Last name of the customer"
        },
        {
          "name": "Email",
          "data_type": "NVARCHAR",
          "nullable": true,
          "length": 100,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Email address of the customer"
        },
        {
          "name": "Phone",
          "data_type": "VARCHAR",
          "nullable": true,
          "length": 20,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Phone number of the customer"
        },
        {
          "name": "StatusCode",
          "data_type": "CHAR",
          "nullable": false,
          "length": 1,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Status code of the customer"
        },
        {
          "name": "CreatedDate",
          "data_type": "DATETIME",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": "GETDATE()",
          "is_identity": false,
          "is_computed": false,
          "description": "Date the customer was created"
        },
        {
          "name": "ModifiedDate",
          "data_type": "DATETIME",
          "nullable": true,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Date the customer was last modified"
        }
      ],
      "primary_key": {
        "name": "PK_Customer",
        "columns": [
          "CustomerID"
        ]
      },
      "foreign_keys": [
        {
          "name": "FK_Customer_CustomerStatus",
          "columns": [
            "StatusCode"
          ],
          "ref_table": "CustomerStatus",
          "ref_columns": [
            "StatusCode"
          ],
          "on_delete": "NO ACTION",
          "on_update": "CASCADE"
        }
      ],
      "indices": [],
      "check_constraints": [
        {
          "name": "CK_Customer_Email",
          "definition": "Email LIKE '%@%.%'"
        }
      ],
      "unique_constraints": [],
      "default_constraints": [],
      "reference_data": null,
      "description": "Customer table"
    },
    {
      "name": "ProductCategory",
      "columns": [
        {
          "name": "CategoryID",
          "data_type": "INTEGER",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": true,
          "is_computed": false,
          "description": "Primary key for product category"
        },
        {
          "name": "CategoryName",
          "data_type": "NVARCHAR",
          "nullable": false,
          "length": 50,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Name of the product category"
        },
        {
          "name": "CategoryDescription",
          "data_type": "NVARCHAR",
          "nullable": true,
          "length": 255,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Description of the product category"
        },
        {
          "name": "IsActive",
          "data_type": "BIT",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": "1",
          "is_identity": false,
          "is_computed": false,
          "description": "Indicates if the category is active"
        }
      ],
      "primary_key": {
        "name": "PK_ProductCategory",
        "columns": [
          "CategoryID"
        ]
      },
      "foreign_keys": [],
      "indices": [],
      "check_constraints": [],
      "unique_constraints": [],
      "default_constraints": [],
      "reference_data": null,
      "description": "Product Category reference table"
    },
    {
      "name": "Product",
      "columns": [
        {
          "name": "ProductID",
          "data_type": "INTEGER",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": true,
          "is_computed": false,
          "description": "Primary key for product"
        },
        {
          "name": "ProductName",
          "data_type": "NVARCHAR",
          "nullable": false,
          "length": 100,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Name of the product"
        },
        {
          "name": "ProductDescription",
          "data_type": "NVARCHAR",
          "nullable": true,
          "length": "MAX",
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Description of the product"
        },
        {
          "name": "CategoryID",
          "data_type": "INTEGER",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Category ID of the product"
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
          "name": "IsDiscontinued",
          "data_type": "BIT",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": "0",
          "is_identity": false,
          "is_computed": false,
          "description": "Indicates if the product is discontinued"
        },
        {
          "name": "CreatedDate",
          "data_type": "DATETIME",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": "GETDATE()",
          "is_identity": false,
          "is_computed": false,
          "description": "Date the product was created"
        },
        {
          "name": "ModifiedDate",
          "data_type": "DATETIME",
          "nullable": true,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Date the product was last modified"
        }
      ],
      "primary_key": {
        "name": "PK_Product",
        "columns": [
          "ProductID"
        ]
      },
      "foreign_keys": [
        {
          "name": "FK_Product_ProductCategory",
          "columns": [
            "CategoryID"
          ],
          "ref_table": "ProductCategory",
          "ref_columns": [
            "CategoryID"
          ],
          "on_delete": null,
          "on_update": null
        }
      ],
      "indices": [],
      "check_constraints": [
        {
          "name": "CK_Product_UnitPrice",
          "definition": "UnitPrice >= 0"
        }
      ],
      "unique_constraints": [],
      "default_constraints": [],
      "reference_data": null,
      "description": "Product table"
    },
    {
      "name": "Order",
      "columns": [
        {
          "name": "OrderID",
          "data_type": "INTEGER",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": true,
          "is_computed": false,
          "description": "Primary key for order"
        },
        {
          "name": "CustomerID",
          "data_type": "INTEGER",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Customer ID associated with the order"
        },
        {
          "name": "OrderDate",
          "data_type": "DATETIME",
          "nullable": false,
          "length": null,
          "precision": null,
          "scale": null,
          "default_value": "GETDATE()",
          "is_identity": false,
          "is_computed": false,
          "description": "Date the order was placed"
        },
        {
          "name": "TotalAmount",
          "data_type": "DECIMAL",
          "nullable": false,
          "length": null,
          "precision": 12,
          "scale": 2,
          "default_value": null,
          "is_identity": false,
          "is_computed": false,
          "description": "Total amount of the order"
        },
        {
          "name": "Status",
          "data_type": "NVARCHAR",
          "nullable": false,
          "length": 20,
          "precision": null,
          "scale": null,
          "default_value": "'Pending'",
          "is_identity": false,
          "is_computed": false,
          "description": "Status of the order"
        }
      ],
      "primary_key": {
        "name": "PK_Order",
        "columns": [
          "OrderID"
        ]
      },
      "foreign_keys": [
        {
          "name": "FK_Order_Customer",
          "columns": [
            "CustomerID"
          ],
          "ref_table": "Customer",
          "ref_columns": [
            "CustomerID"
          ],
          "on_delete": null,
          "on_update": null
        }
      ],
      "indices": [],
      "check_constraints": [],
      "unique_constraints": [],
      "default_constraints": [],
      "reference_data": null,
      "description": "Order table"
    },
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
  ],
  "generation_rules": [],
  "ir_version": "1.0.0",
  "description": "Sample SQL Schema for Testing - A simplified version of a Customer Order database"
}
```

## Reference Data Content

```
# [Reference.Countries]
CountryCode, CountryName, Continent
US, United States, North America
CA, Canada, North America
UK, United Kingdom, Europe
FR, France, Europe
DE, Germany, Europe
JP, Japan, Asia
CN, China, Asia
AU, Australia, Oceania

# [Reference.Languages]
LanguageCode, LanguageName, NativeName
EN, English, English
FR, French, Français
DE, German, Deutsch
ES, Spanish, Español
IT, Italian, Italiano
JA, Japanese, 日本語
ZH, Chinese, 中文

# [Reference.Currencies]
CurrencyCode, CurrencyName, Symbol
USD, US Dollar, $
EUR, Euro, €
GBP, British Pound, £
JPY, Japanese Yen, ¥
CAD, Canadian Dollar, $
CNY, Chinese Yuan, ¥
AUD, Australian Dollar, $ 
```

## Instructions

1. Analyze the schema and reference data
2. Identify which reference data tables should map to which schema tables
3. Consider table name similarity, column names, and data content
4. Create a mapping in JSON format

## Output Format

Return ONLY a JSON object with the following structure:

```json
{
  "mapping": {
    "RefSchemaName.RefTableName": "SchemaTableName",
    "RefSchemaName.AnotherRefTable": "AnotherSchemaTable"
  }
}
```

If you can't find a matching schema table for a reference table, omit it from the mapping.
