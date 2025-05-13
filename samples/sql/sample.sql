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