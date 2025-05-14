# SQL Schema Analysis Task

## Objective

Analyze the provided SQL Server CREATE script and transform it into a structured Schema representation.

## Schema Name

SampleOrdersDB

## SQL Script to Analyze

```sql
-- Sample SQL Schema for Testing
-- This script contains a simplified version of a Customer Order database

-- Customer Status reference table
CREATE TABLE CustomerStatus (
    StatusCode CHAR(1) NOT NULL,
    StatusName NVARCHAR(50) NOT NULL,
    StatusDescription NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_CustomerStatus PRIMARY KEY (StatusCode)
);

-- Customer table
CREATE TABLE Customer (
    CustomerID INT IDENTITY(1,1) NOT NULL,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NULL,
    Phone VARCHAR(20) NULL,
    StatusCode CHAR(1) NOT NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_Customer PRIMARY KEY (CustomerID),
    CONSTRAINT FK_Customer_CustomerStatus FOREIGN KEY (StatusCode) 
        REFERENCES CustomerStatus (StatusCode) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT CK_Customer_Email CHECK (Email LIKE '%@%.%')
);

-- Product Category reference table
CREATE TABLE ProductCategory (
    CategoryID INT IDENTITY(1,1) NOT NULL,
    CategoryName NVARCHAR(50) NOT NULL,
    CategoryDescription NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_ProductCategory PRIMARY KEY (CategoryID)
);

-- Product table
CREATE TABLE Product (
    ProductID INT IDENTITY(1,1) NOT NULL,
    ProductName NVARCHAR(100) NOT NULL,
    ProductDescription NVARCHAR(MAX) NULL,
    CategoryID INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    IsDiscontinued BIT NOT NULL DEFAULT 0,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_Product PRIMARY KEY (ProductID),
    CONSTRAINT FK_Product_ProductCategory FOREIGN KEY (CategoryID) 
        REFERENCES ProductCategory (CategoryID),
    CONSTRAINT CK_Product_UnitPrice CHECK (UnitPrice >= 0)
);

-- Order table
CREATE TABLE [Order] (
    OrderID INT IDENTITY(1,1) NOT NULL,
    CustomerID INT NOT NULL,
    OrderDate DATETIME NOT NULL DEFAULT GETDATE(),
    TotalAmount DECIMAL(12, 2) NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Pending',
    CONSTRAINT PK_Order PRIMARY KEY (OrderID),
    CONSTRAINT FK_Order_Customer FOREIGN KEY (CustomerID) 
        REFERENCES Customer (CustomerID)
);

-- Order Detail table
CREATE TABLE OrderDetail (
    OrderDetailID INT IDENTITY(1,1) NOT NULL,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    Discount DECIMAL(5, 2) NOT NULL DEFAULT 0,
    CONSTRAINT PK_OrderDetail PRIMARY KEY (OrderDetailID),
    CONSTRAINT FK_OrderDetail_Order FOREIGN KEY (OrderID) 
        REFERENCES [Order] (OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderDetail_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID),
    CONSTRAINT CK_OrderDetail_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_OrderDetail_UnitPrice CHECK (UnitPrice >= 0),
    CONSTRAINT CK_OrderDetail_Discount CHECK (Discount >= 0 AND Discount <= 100)
);

-- Add some constraints separately to test constraint parsing
ALTER TABLE Customer ADD CONSTRAINT UQ_Customer_Email UNIQUE (Email);

-- Add an index
CREATE INDEX IX_Customer_LastName ON Customer(LastName, FirstName); 
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
{
  "name": "SchemaName",  // <-- This must be exactly "name", not "schemaName"
  "tables": [            // <-- This must be exactly "tables", not "Tables"
    {
      "name": "TableName",  // <-- This must be exactly "name", not "tableName"
      "description": "Description of the table",
      "columns": [          // <-- This must be exactly "columns", not "Columns"
        {
          "name": "ColumnName",
          "data_type": {   // <-- This must be a nested object with the format below
            "name": "DataTypeName", // e.g., "INTEGER", "VARCHAR", etc.
            "length": 50,    // Optional, for string types
            "precision": 10, // Optional, for numeric types
            "scale": 2       // Optional, for numeric types
          },
          "nullable": true,  // Boolean - must be exactly "nullable", not "isNullable"
          "default_value": "DefaultValue",  // Optional
          "is_identity": false,  // Boolean
          "description": "Description of the column"  // Optional
        }
      ],
      "primary_key": {   // <-- Optional, null if not present
        "name": "PKName",
        "columns": ["ColumnName"]
      },
      "foreign_keys": [   // <-- Array, empty if not present
        {
          "name": "FKName",
          "columns": ["ColumnName"],
          "ref_table": "ReferencedTable",
          "ref_columns": ["ReferencedColumn"],
          "on_delete": "OnDeleteAction",  // Optional
          "on_update": "OnUpdateAction"   // Optional
        }
      ],
      "check_constraints": [   // <-- Array, empty if not present
        {
          "name": "CheckName",
          "definition": "CheckDefinition"
        }
      ],
      "is_reference_table": false  // <-- Boolean
    }
  ],
  "description": "Description of the overall schema",
  "generation_rules": []  // <-- Empty array for this initial schema
}
```

Use your understanding of SQL Server syntax to properly interpret the script and create an accurate representation of the database schema. Include all constraints, even if they're defined separately from the table creation.

IMPORTANT: Follow the EXACT format above, including the exact property names as shown in the example. Ensure your response is a valid JSON object that exactly follows this structure.
