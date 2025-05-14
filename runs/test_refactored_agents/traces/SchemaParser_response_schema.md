{
  "name": "SampleOrdersDB",
  "tables": [
    {
      "name": "CustomerStatus",
      "description": "Customer Status reference table",
      "columns": [
        {
          "name": "StatusCode",
          "data_type": {
            "name": "CHAR",
            "length": 1
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Primary key for customer status"
        },
        {
          "name": "StatusName",
          "data_type": {
            "name": "NVARCHAR",
            "length": 50
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Name of the customer status"
        },
        {
          "name": "StatusDescription",
          "data_type": {
            "name": "NVARCHAR",
            "length": 255
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Description of the customer status"
        },
        {
          "name": "IsActive",
          "data_type": {
            "name": "BIT"
          },
          "nullable": false,
          "default_value": "1",
          "is_identity": false,
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
      "check_constraints": [],
      "is_reference_table": true
    },
    {
      "name": "Customer",
      "description": "Customer table",
      "columns": [
        {
          "name": "CustomerID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": true,
          "description": "Primary key for customer"
        },
        {
          "name": "FirstName",
          "data_type": {
            "name": "NVARCHAR",
            "length": 50
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "First name of the customer"
        },
        {
          "name": "LastName",
          "data_type": {
            "name": "NVARCHAR",
            "length": 50
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Last name of the customer"
        },
        {
          "name": "Email",
          "data_type": {
            "name": "NVARCHAR",
            "length": 100
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Email address of the customer"
        },
        {
          "name": "Phone",
          "data_type": {
            "name": "VARCHAR",
            "length": 20
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Phone number of the customer"
        },
        {
          "name": "StatusCode",
          "data_type": {
            "name": "CHAR",
            "length": 1
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Status code of the customer"
        },
        {
          "name": "CreatedDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": false,
          "default_value": "GETDATE()",
          "is_identity": false,
          "description": "Date the customer was created"
        },
        {
          "name": "ModifiedDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
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
      "check_constraints": [
        {
          "name": "CK_Customer_Email",
          "definition": "Email LIKE '%@%.%'"
        }
      ],
      "is_reference_table": false
    },
    {
      "name": "ProductCategory",
      "description": "Product Category reference table",
      "columns": [
        {
          "name": "CategoryID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": true,
          "description": "Primary key for product category"
        },
        {
          "name": "CategoryName",
          "data_type": {
            "name": "NVARCHAR",
            "length": 50
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Name of the product category"
        },
        {
          "name": "CategoryDescription",
          "data_type": {
            "name": "NVARCHAR",
            "length": 255
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Description of the product category"
        },
        {
          "name": "IsActive",
          "data_type": {
            "name": "BIT"
          },
          "nullable": false,
          "default_value": "1",
          "is_identity": false,
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
      "check_constraints": [],
      "is_reference_table": true
    },
    {
      "name": "Product",
      "description": "Product table",
      "columns": [
        {
          "name": "ProductID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": true,
          "description": "Primary key for product"
        },
        {
          "name": "ProductName",
          "data_type": {
            "name": "NVARCHAR",
            "length": 100
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Name of the product"
        },
        {
          "name": "ProductDescription",
          "data_type": {
            "name": "NVARCHAR",
            "length": "MAX"
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
          "description": "Description of the product"
        },
        {
          "name": "CategoryID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Category ID of the product"
        },
        {
          "name": "UnitPrice",
          "data_type": {
            "name": "DECIMAL",
            "precision": 10,
            "scale": 2
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Unit price of the product"
        },
        {
          "name": "IsDiscontinued",
          "data_type": {
            "name": "BIT"
          },
          "nullable": false,
          "default_value": "0",
          "is_identity": false,
          "description": "Indicates if the product is discontinued"
        },
        {
          "name": "CreatedDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": false,
          "default_value": "GETDATE()",
          "is_identity": false,
          "description": "Date the product was created"
        },
        {
          "name": "ModifiedDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": true,
          "default_value": null,
          "is_identity": false,
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
      "check_constraints": [
        {
          "name": "CK_Product_UnitPrice",
          "definition": "UnitPrice >= 0"
        }
      ],
      "is_reference_table": false
    },
    {
      "name": "Order",
      "description": "Order table",
      "columns": [
        {
          "name": "OrderID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": true,
          "description": "Primary key for order"
        },
        {
          "name": "CustomerID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Customer ID associated with the order"
        },
        {
          "name": "OrderDate",
          "data_type": {
            "name": "DATETIME"
          },
          "nullable": false,
          "default_value": "GETDATE()",
          "is_identity": false,
          "description": "Date the order was placed"
        },
        {
          "name": "TotalAmount",
          "data_type": {
            "name": "DECIMAL",
            "precision": 12,
            "scale": 2
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Total amount of the order"
        },
        {
          "name": "Status",
          "data_type": {
            "name": "NVARCHAR",
            "length": 20
          },
          "nullable": false,
          "default_value": "'Pending'",
          "is_identity": false,
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
      "check_constraints": [],
      "is_reference_table": false
    },
    {
      "name": "OrderDetail",
      "description": "Order Detail table",
      "columns": [
        {
          "name": "OrderDetailID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": true,
          "description": "Primary key for order detail"
        },
        {
          "name": "OrderID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Order ID associated with the detail"
        },
        {
          "name": "ProductID",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Product ID associated with the detail"
        },
        {
          "name": "Quantity",
          "data_type": {
            "name": "INT"
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Quantity of the product ordered"
        },
        {
          "name": "UnitPrice",
          "data_type": {
            "name": "DECIMAL",
            "precision": 10,
            "scale": 2
          },
          "nullable": false,
          "default_value": null,
          "is_identity": false,
          "description": "Unit price of the product"
        },
        {
          "name": "Discount",
          "data_type": {
            "name": "DECIMAL",
            "precision": 5,
            "scale": 2
          },
          "nullable": false,
          "default_value": "0",
          "is_identity": false,
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
      "is_reference_table": false
    }
  ],
  "description": "Sample SQL Schema for Testing - A simplified version of a Customer Order database",
  "generation_rules": []
}