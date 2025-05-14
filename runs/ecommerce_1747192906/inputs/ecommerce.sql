-- Enhanced E-commerce SQL Schema
-- A comprehensive schema for an e-commerce application with all necessary components

-- REFERENCE/LOOKUP TABLES ----------------------------------------------------------

-- Countries for international shipping and user addresses
CREATE TABLE Country (
    CountryID INT IDENTITY(1,1) NOT NULL,
    CountryCode CHAR(2) NOT NULL,  -- ISO 3166-1 alpha-2
    CountryName NVARCHAR(100) NOT NULL,
    PhonePrefix VARCHAR(10) NULL,
    IsSupported BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_Country PRIMARY KEY (CountryID),
    CONSTRAINT UQ_Country_Code UNIQUE (CountryCode)
);

-- States/Provinces for regional data
CREATE TABLE StateProvince (
    StateProvinceID INT IDENTITY(1,1) NOT NULL,
    CountryID INT NOT NULL,
    StateCode CHAR(5) NOT NULL,
    StateName NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_StateProvince PRIMARY KEY (StateProvinceID),
    CONSTRAINT FK_StateProvince_Country FOREIGN KEY (CountryID) 
        REFERENCES Country (CountryID) ON DELETE NO ACTION,
    CONSTRAINT UQ_StateProvince_Code UNIQUE (CountryID, StateCode)
);

-- Currencies for multi-currency support
CREATE TABLE Currency (
    CurrencyID INT IDENTITY(1,1) NOT NULL,
    CurrencyCode CHAR(3) NOT NULL,  -- ISO 4217
    CurrencyName NVARCHAR(50) NOT NULL,
    CurrencySymbol NVARCHAR(5) NOT NULL,
    ExchangeRate DECIMAL(18, 6) NOT NULL,
    IsDefault BIT NOT NULL DEFAULT 0,
    IsSupported BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_Currency PRIMARY KEY (CurrencyID),
    CONSTRAINT UQ_Currency_Code UNIQUE (CurrencyCode)
);

-- Payment Methods
CREATE TABLE PaymentMethod (
    PaymentMethodID INT IDENTITY(1,1) NOT NULL,
    PaymentMethodName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    DisplayOrder INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_PaymentMethod PRIMARY KEY (PaymentMethodID)
);

-- Shipping Methods
CREATE TABLE ShippingMethod (
    ShippingMethodID INT IDENTITY(1,1) NOT NULL,
    ShippingMethodName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255) NULL,
    BasePrice DECIMAL(10, 2) NOT NULL,
    EstimatedDays INT NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    DisplayOrder INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_ShippingMethod PRIMARY KEY (ShippingMethodID)
);

-- Order Statuses
CREATE TABLE OrderStatus (
    OrderStatusID INT IDENTITY(1,1) NOT NULL,
    StatusName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    DisplayOrder INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_OrderStatus PRIMARY KEY (OrderStatusID)
);

-- User Statuses
CREATE TABLE UserStatus (
    UserStatusID INT IDENTITY(1,1) NOT NULL,
    StatusName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_UserStatus PRIMARY KEY (UserStatusID)
);

-- User Roles
CREATE TABLE UserRole (
    UserRoleID INT IDENTITY(1,1) NOT NULL,
    RoleName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_UserRole PRIMARY KEY (UserRoleID)
);

-- Product Categories with hierarchical structure
CREATE TABLE ProductCategory (
    CategoryID INT IDENTITY(1,1) NOT NULL,
    ParentCategoryID INT NULL,
    CategoryName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500) NULL,
    ImageURL NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    DisplayOrder INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_ProductCategory PRIMARY KEY (CategoryID),
    CONSTRAINT FK_ProductCategory_ParentCategory FOREIGN KEY (ParentCategoryID) 
        REFERENCES ProductCategory (CategoryID),
    CONSTRAINT UQ_ProductCategory_Name UNIQUE (CategoryName)
);

-- Product Brands
CREATE TABLE ProductBrand (
    BrandID INT IDENTITY(1,1) NOT NULL,
    BrandName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500) NULL,
    LogoURL NVARCHAR(255) NULL,
    Website NVARCHAR(255) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_ProductBrand PRIMARY KEY (BrandID),
    CONSTRAINT UQ_ProductBrand_Name UNIQUE (BrandName)
);

-- USER MANAGEMENT ----------------------------------------------------------

-- User Accounts
CREATE TABLE [User] (
    UserID INT IDENTITY(1,1) NOT NULL,
    Email NVARCHAR(100) NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    PhoneNumber NVARCHAR(20) NULL,
    BirthDate DATE NULL,
    UserStatusID INT NOT NULL,
    UserRoleID INT NOT NULL,
    PreferredCurrencyID INT NULL,
    RegistrationDate DATETIME NOT NULL DEFAULT GETDATE(),
    LastLoginDate DATETIME NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_User PRIMARY KEY (UserID),
    CONSTRAINT FK_User_UserStatus FOREIGN KEY (UserStatusID) 
        REFERENCES UserStatus (UserStatusID),
    CONSTRAINT FK_User_UserRole FOREIGN KEY (UserRoleID) 
        REFERENCES UserRole (UserRoleID),
    CONSTRAINT FK_User_Currency FOREIGN KEY (PreferredCurrencyID) 
        REFERENCES Currency (CurrencyID),
    CONSTRAINT UQ_User_Email UNIQUE (Email)
);

-- User Addresses
CREATE TABLE UserAddress (
    AddressID INT IDENTITY(1,1) NOT NULL,
    UserID INT NOT NULL,
    AddressType NVARCHAR(20) NOT NULL, -- 'Billing', 'Shipping'
    IsDefault BIT NOT NULL DEFAULT 0,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Address1 NVARCHAR(100) NOT NULL,
    Address2 NVARCHAR(100) NULL,
    City NVARCHAR(100) NOT NULL,
    StateProvinceID INT NOT NULL,
    PostalCode NVARCHAR(20) NOT NULL,
    CountryID INT NOT NULL,
    PhoneNumber NVARCHAR(20) NULL,
    CONSTRAINT PK_UserAddress PRIMARY KEY (AddressID),
    CONSTRAINT FK_UserAddress_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE CASCADE,
    CONSTRAINT FK_UserAddress_Country FOREIGN KEY (CountryID) 
        REFERENCES Country (CountryID),
    CONSTRAINT FK_UserAddress_StateProvince FOREIGN KEY (StateProvinceID) 
        REFERENCES StateProvince (StateProvinceID),
    CONSTRAINT CK_UserAddress_Type CHECK (AddressType IN ('Billing', 'Shipping'))
);

-- User Payment Methods
CREATE TABLE UserPaymentMethod (
    UserPaymentMethodID INT IDENTITY(1,1) NOT NULL,
    UserID INT NOT NULL,
    PaymentMethodID INT NOT NULL,
    IsDefault BIT NOT NULL DEFAULT 0,
    AccountName NVARCHAR(100) NULL,
    -- Tokenized/masked payment details (stored securely)
    PaymentToken NVARCHAR(255) NULL,
    Last4Digits NVARCHAR(4) NULL,
    ExpiryMonth INT NULL,
    ExpiryYear INT NULL,
    BillingAddressID INT NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_UserPaymentMethod PRIMARY KEY (UserPaymentMethodID),
    CONSTRAINT FK_UserPaymentMethod_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE CASCADE,
    CONSTRAINT FK_UserPaymentMethod_PaymentMethod FOREIGN KEY (PaymentMethodID) 
        REFERENCES PaymentMethod (PaymentMethodID),
    CONSTRAINT FK_UserPaymentMethod_BillingAddress FOREIGN KEY (BillingAddressID) 
        REFERENCES UserAddress (AddressID)
);

-- PRODUCT MANAGEMENT ----------------------------------------------------------

-- Products
CREATE TABLE Product (
    ProductID INT IDENTITY(1,1) NOT NULL,
    SKU NVARCHAR(50) NOT NULL,
    ProductName NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX) NULL,
    CategoryID INT NOT NULL,
    BrandID INT NULL,
    BasePrice DECIMAL(10, 2) NOT NULL,
    DiscountPercentage DECIMAL(5, 2) NULL,
    TaxRate DECIMAL(5, 2) NULL,
    Weight DECIMAL(10, 2) NULL,
    Dimensions NVARCHAR(50) NULL, -- Format: L x W x H
    InventoryCount INT NOT NULL DEFAULT 0,
    ReorderThreshold INT NULL,
    IsPhysical BIT NOT NULL DEFAULT 1, -- False for digital products
    IsActive BIT NOT NULL DEFAULT 1,
    IsDiscontinued BIT NOT NULL DEFAULT 0,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_Product PRIMARY KEY (ProductID),
    CONSTRAINT FK_Product_Category FOREIGN KEY (CategoryID) 
        REFERENCES ProductCategory (CategoryID),
    CONSTRAINT FK_Product_Brand FOREIGN KEY (BrandID) 
        REFERENCES ProductBrand (BrandID),
    CONSTRAINT UQ_Product_SKU UNIQUE (SKU),
    CONSTRAINT CK_Product_BasePrice CHECK (BasePrice >= 0),
    CONSTRAINT CK_Product_DiscountPercentage CHECK (DiscountPercentage >= 0 AND DiscountPercentage <= 100)
);

-- Product Images
CREATE TABLE ProductImage (
    ProductImageID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    ImageURL NVARCHAR(255) NOT NULL,
    ImageAlt NVARCHAR(100) NULL,
    IsPrimary BIT NOT NULL DEFAULT 0,
    DisplayOrder INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_ProductImage PRIMARY KEY (ProductImageID),
    CONSTRAINT FK_ProductImage_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID) ON DELETE CASCADE
);

-- Product Variants (for products with options like size, color)
CREATE TABLE ProductVariant (
    VariantID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    VariantName NVARCHAR(100) NOT NULL,
    SKU NVARCHAR(50) NOT NULL,
    PriceAdjustment DECIMAL(10, 2) NOT NULL DEFAULT 0,
    InventoryCount INT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT PK_ProductVariant PRIMARY KEY (VariantID),
    CONSTRAINT FK_ProductVariant_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID) ON DELETE CASCADE,
    CONSTRAINT UQ_ProductVariant_SKU UNIQUE (SKU)
);

-- Product Reviews
CREATE TABLE ProductReview (
    ReviewID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    UserID INT NOT NULL,
    Rating INT NOT NULL, -- 1-5 stars
    Title NVARCHAR(100) NULL,
    ReviewText NVARCHAR(1000) NULL,
    IsVerifiedPurchase BIT NOT NULL DEFAULT 0,
    IsApproved BIT NOT NULL DEFAULT 0,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_ProductReview PRIMARY KEY (ReviewID),
    CONSTRAINT FK_ProductReview_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID) ON DELETE CASCADE,
    CONSTRAINT FK_ProductReview_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID),
    CONSTRAINT CK_ProductReview_Rating CHECK (Rating BETWEEN 1 AND 5)
);

-- Related Products
CREATE TABLE RelatedProduct (
    RelatedProductID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    RelatedToProductID INT NOT NULL,
    RelationType NVARCHAR(20) NOT NULL, -- 'CrossSell', 'UpSell', 'Accessory', 'Similar'
    DisplayOrder INT NOT NULL DEFAULT 0,
    CONSTRAINT PK_RelatedProduct PRIMARY KEY (RelatedProductID),
    CONSTRAINT FK_RelatedProduct_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID) ON DELETE CASCADE,
    CONSTRAINT FK_RelatedProduct_RelatedToProduct FOREIGN KEY (RelatedToProductID) 
        REFERENCES Product (ProductID),
    CONSTRAINT UQ_RelatedProduct UNIQUE (ProductID, RelatedToProductID),
    CONSTRAINT CK_RelatedProduct_Type CHECK (RelationType IN ('CrossSell', 'UpSell', 'Accessory', 'Similar')),
    CONSTRAINT CK_RelatedProduct_NotSelf CHECK (ProductID != RelatedToProductID)
);

-- Promotions and Discounts
CREATE TABLE Promotion (
    PromotionID INT IDENTITY(1,1) NOT NULL,
    PromotionName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500) NULL,
    DiscountType NVARCHAR(20) NOT NULL, -- 'Percentage', 'FixedAmount', 'FreeShipping'
    DiscountValue DECIMAL(10, 2) NOT NULL,
    CouponCode NVARCHAR(20) NULL,
    RequiredMinimumPurchase DECIMAL(10, 2) NULL,
    StartDate DATETIME NOT NULL,
    EndDate DATETIME NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    MaximumUses INT NULL,
    CurrentUses INT NOT NULL DEFAULT 0,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_Promotion PRIMARY KEY (PromotionID),
    CONSTRAINT CK_Promotion_DiscountType CHECK (DiscountType IN ('Percentage', 'FixedAmount', 'FreeShipping')),
    CONSTRAINT CK_Promotion_DiscountValue CHECK (DiscountValue >= 0),
    CONSTRAINT CK_Promotion_Dates CHECK (StartDate <= EndDate OR EndDate IS NULL)
);

-- Promotion-Product relationship (for promotions that apply to specific products)
CREATE TABLE PromotionProduct (
    PromotionProductID INT IDENTITY(1,1) NOT NULL,
    PromotionID INT NOT NULL,
    ProductID INT NOT NULL,
    CONSTRAINT PK_PromotionProduct PRIMARY KEY (PromotionProductID),
    CONSTRAINT FK_PromotionProduct_Promotion FOREIGN KEY (PromotionID) 
        REFERENCES Promotion (PromotionID) ON DELETE CASCADE,
    CONSTRAINT FK_PromotionProduct_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID) ON DELETE CASCADE,
    CONSTRAINT UQ_PromotionProduct UNIQUE (PromotionID, ProductID)
);

-- Promotion-Category relationship (for promotions that apply to entire categories)
CREATE TABLE PromotionCategory (
    PromotionCategoryID INT IDENTITY(1,1) NOT NULL,
    PromotionID INT NOT NULL,
    CategoryID INT NOT NULL,
    CONSTRAINT PK_PromotionCategory PRIMARY KEY (PromotionCategoryID),
    CONSTRAINT FK_PromotionCategory_Promotion FOREIGN KEY (PromotionID) 
        REFERENCES Promotion (PromotionID) ON DELETE CASCADE,
    CONSTRAINT FK_PromotionCategory_Category FOREIGN KEY (CategoryID) 
        REFERENCES ProductCategory (CategoryID) ON DELETE CASCADE,
    CONSTRAINT UQ_PromotionCategory UNIQUE (PromotionID, CategoryID)
);

-- ORDER MANAGEMENT ----------------------------------------------------------

-- Shopping Cart
CREATE TABLE ShoppingCart (
    CartID INT IDENTITY(1,1) NOT NULL,
    UserID INT NULL, -- NULL for anonymous carts
    SessionID NVARCHAR(100) NULL, -- For anonymous users
    CurrencyID INT NOT NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_ShoppingCart PRIMARY KEY (CartID),
    CONSTRAINT FK_ShoppingCart_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE SET NULL,
    CONSTRAINT FK_ShoppingCart_Currency FOREIGN KEY (CurrencyID) 
        REFERENCES Currency (CurrencyID)
);

-- Shopping Cart Items
CREATE TABLE ShoppingCartItem (
    CartItemID INT IDENTITY(1,1) NOT NULL,
    CartID INT NOT NULL,
    ProductID INT NOT NULL,
    VariantID INT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    AddedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_ShoppingCartItem PRIMARY KEY (CartItemID),
    CONSTRAINT FK_ShoppingCartItem_Cart FOREIGN KEY (CartID) 
        REFERENCES ShoppingCart (CartID) ON DELETE CASCADE,
    CONSTRAINT FK_ShoppingCartItem_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID),
    CONSTRAINT FK_ShoppingCartItem_Variant FOREIGN KEY (VariantID) 
        REFERENCES ProductVariant (VariantID),
    CONSTRAINT CK_ShoppingCartItem_Quantity CHECK (Quantity > 0)
);

-- Orders
CREATE TABLE [Order] (
    OrderID INT IDENTITY(1,1) NOT NULL,
    UserID INT NULL, -- NULL for guest checkout
    OrderNumber NVARCHAR(20) NOT NULL,
    OrderDate DATETIME NOT NULL DEFAULT GETDATE(),
    OrderStatusID INT NOT NULL,
    CurrencyID INT NOT NULL,
    SubtotalAmount DECIMAL(10, 2) NOT NULL,
    ShippingAmount DECIMAL(10, 2) NOT NULL,
    TaxAmount DECIMAL(10, 2) NOT NULL,
    DiscountAmount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    PaymentMethodID INT NOT NULL,
    PaymentTransactionID NVARCHAR(100) NULL,
    ShippingMethodID INT NOT NULL,
    TrackingNumber NVARCHAR(100) NULL,
    BillingAddressID INT NOT NULL,
    ShippingAddressID INT NOT NULL,
    CustomerNotes NVARCHAR(1000) NULL,
    InternalNotes NVARCHAR(1000) NULL,
    IsGuestCheckout BIT NOT NULL DEFAULT 0,
    IPAddress NVARCHAR(45) NULL,
    UserAgent NVARCHAR(500) NULL,
    CompletedDate DATETIME NULL,
    CancelledDate DATETIME NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_Order PRIMARY KEY (OrderID),
    CONSTRAINT FK_Order_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE SET NULL,
    CONSTRAINT FK_Order_OrderStatus FOREIGN KEY (OrderStatusID) 
        REFERENCES OrderStatus (OrderStatusID),
    CONSTRAINT FK_Order_Currency FOREIGN KEY (CurrencyID) 
        REFERENCES Currency (CurrencyID),
    CONSTRAINT FK_Order_PaymentMethod FOREIGN KEY (PaymentMethodID) 
        REFERENCES PaymentMethod (PaymentMethodID),
    CONSTRAINT FK_Order_ShippingMethod FOREIGN KEY (ShippingMethodID) 
        REFERENCES ShippingMethod (ShippingMethodID),
    CONSTRAINT UQ_Order_OrderNumber UNIQUE (OrderNumber)
);

-- Order Items
CREATE TABLE OrderItem (
    OrderItemID INT IDENTITY(1,1) NOT NULL,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    VariantID INT NULL,
    ProductName NVARCHAR(255) NOT NULL, -- Stored at time of order
    SKU NVARCHAR(50) NOT NULL, -- Stored at time of order
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    UnitCost DECIMAL(10, 2) NULL, -- For profit reporting
    Discount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    TaxAmount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    FulfillmentStatus NVARCHAR(20) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Shipped', 'Delivered', 'Cancelled'
    CONSTRAINT PK_OrderItem PRIMARY KEY (OrderItemID),
    CONSTRAINT FK_OrderItem_Order FOREIGN KEY (OrderID) 
        REFERENCES [Order] (OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderItem_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID),
    CONSTRAINT FK_OrderItem_Variant FOREIGN KEY (VariantID) 
        REFERENCES ProductVariant (VariantID),
    CONSTRAINT CK_OrderItem_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_OrderItem_UnitPrice CHECK (UnitPrice >= 0),
    CONSTRAINT CK_OrderItem_FulfillmentStatus CHECK (FulfillmentStatus IN ('Pending', 'Shipped', 'Delivered', 'Cancelled'))
);

-- Order History (for tracking status changes)
CREATE TABLE OrderHistory (
    OrderHistoryID INT IDENTITY(1,1) NOT NULL,
    OrderID INT NOT NULL,
    OrderStatusID INT NOT NULL,
    Notes NVARCHAR(1000) NULL,
    CreatedByUserID INT NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_OrderHistory PRIMARY KEY (OrderHistoryID),
    CONSTRAINT FK_OrderHistory_Order FOREIGN KEY (OrderID) 
        REFERENCES [Order] (OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderHistory_OrderStatus FOREIGN KEY (OrderStatusID) 
        REFERENCES OrderStatus (OrderStatusID),
    CONSTRAINT FK_OrderHistory_User FOREIGN KEY (CreatedByUserID) 
        REFERENCES [User] (UserID) ON DELETE SET NULL
);

-- Promotional codes used with orders
CREATE TABLE OrderPromotion (
    OrderPromotionID INT IDENTITY(1,1) NOT NULL,
    OrderID INT NOT NULL,
    PromotionID INT NOT NULL,
    DiscountAmount DECIMAL(10, 2) NOT NULL,
    CONSTRAINT PK_OrderPromotion PRIMARY KEY (OrderPromotionID),
    CONSTRAINT FK_OrderPromotion_Order FOREIGN KEY (OrderID) 
        REFERENCES [Order] (OrderID) ON DELETE CASCADE,
    CONSTRAINT FK_OrderPromotion_Promotion FOREIGN KEY (PromotionID) 
        REFERENCES Promotion (PromotionID),
    CONSTRAINT UQ_OrderPromotion UNIQUE (OrderID, PromotionID)
);

-- Order Shipping Events
CREATE TABLE ShippingEvent (
    ShippingEventID INT IDENTITY(1,1) NOT NULL,
    OrderID INT NOT NULL,
    EventType NVARCHAR(50) NOT NULL, -- 'Shipped', 'InTransit', 'OutForDelivery', 'Delivered', 'Exception'
    Location NVARCHAR(100) NULL,
    EventDate DATETIME NOT NULL,
    TrackingNumber NVARCHAR(100) NULL,
    Notes NVARCHAR(500) NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_ShippingEvent PRIMARY KEY (ShippingEventID),
    CONSTRAINT FK_ShippingEvent_Order FOREIGN KEY (OrderID) 
        REFERENCES [Order] (OrderID) ON DELETE CASCADE
);

-- MARKETING & ANALYTICS ----------------------------------------------------------

-- Wish Lists
CREATE TABLE WishList (
    WishListID INT IDENTITY(1,1) NOT NULL,
    UserID INT NOT NULL,
    WishListName NVARCHAR(100) NOT NULL,
    IsPublic BIT NOT NULL DEFAULT 0,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NULL,
    CONSTRAINT PK_WishList PRIMARY KEY (WishListID),
    CONSTRAINT FK_WishList_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE CASCADE
);

-- Wish List Items
CREATE TABLE WishListItem (
    WishListItemID INT IDENTITY(1,1) NOT NULL,
    WishListID INT NOT NULL,
    ProductID INT NOT NULL,
    VariantID INT NULL,
    AddedDate DATETIME NOT NULL DEFAULT GETDATE(),
    Notes NVARCHAR(500) NULL,
    CONSTRAINT PK_WishListItem PRIMARY KEY (WishListItemID),
    CONSTRAINT FK_WishListItem_WishList FOREIGN KEY (WishListID) 
        REFERENCES WishList (WishID) ON DELETE CASCADE,
    CONSTRAINT FK_WishListItem_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID),
    CONSTRAINT FK_WishListItem_Variant FOREIGN KEY (VariantID) 
        REFERENCES ProductVariant (VariantID),
    CONSTRAINT UQ_WishListItem UNIQUE (WishListID, ProductID, VariantID)
);

-- Product Views (for product view history and analytics)
CREATE TABLE ProductView (
    ProductViewID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    UserID INT NULL, -- NULL for anonymous users
    SessionID NVARCHAR(100) NULL, -- For anonymous users
    ViewDate DATETIME NOT NULL DEFAULT GETDATE(),
    IPAddress NVARCHAR(45) NULL,
    UserAgent NVARCHAR(500) NULL,
    CONSTRAINT PK_ProductView PRIMARY KEY (ProductViewID),
    CONSTRAINT FK_ProductView_Product FOREIGN KEY (ProductID) 
        REFERENCES Product (ProductID) ON DELETE CASCADE,
    CONSTRAINT FK_ProductView_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE SET NULL
);

-- User Searches
CREATE TABLE UserSearch (
    SearchID INT IDENTITY(1,1) NOT NULL,
    UserID INT NULL, -- NULL for anonymous users
    SessionID NVARCHAR(100) NULL, -- For anonymous users
    SearchTerm NVARCHAR(100) NOT NULL,
    ResultCount INT NOT NULL,
    SearchDate DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_UserSearch PRIMARY KEY (SearchID),
    CONSTRAINT FK_UserSearch_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE SET NULL
);

-- Email Marketing Subscriptions
CREATE TABLE EmailSubscription (
    SubscriptionID INT IDENTITY(1,1) NOT NULL,
    UserID INT NULL,
    Email NVARCHAR(100) NOT NULL,
    IsSubscribed BIT NOT NULL DEFAULT 1,
    SubscriptionDate DATETIME NOT NULL DEFAULT GETDATE(),
    UnsubscriptionDate DATETIME NULL,
    CONSTRAINT PK_EmailSubscription PRIMARY KEY (SubscriptionID),
    CONSTRAINT FK_EmailSubscription_User FOREIGN KEY (UserID) 
        REFERENCES [User] (UserID) ON DELETE SET NULL,
    CONSTRAINT UQ_EmailSubscription_Email UNIQUE (Email)
);

-- INDEXES for performance optimization

-- Index for looking up products by category
CREATE INDEX IX_Product_CategoryID ON Product(CategoryID);

-- Index for looking up products by brand
CREATE INDEX IX_Product_BrandID ON Product(BrandID);

-- Index for looking up active products
CREATE INDEX IX_Product_IsActive ON Product(IsActive);

-- Index for user searches
CREATE INDEX IX_UserSearch_SearchTerm ON UserSearch(SearchTerm);

-- Index for order status lookups
CREATE INDEX IX_Order_OrderStatusID ON [Order](OrderStatusID);

-- Index for order date range queries
CREATE INDEX IX_Order_OrderDate ON [Order](OrderDate);

-- Index for looking up user orders
CREATE INDEX IX_Order_UserID ON [Order](UserID);

-- Index for looking up orders by order number
CREATE INDEX IX_Order_OrderNumber ON [Order](OrderNumber);

-- Index for address lookups by user
CREATE INDEX IX_UserAddress_UserID ON UserAddress(UserID);

-- Index for product view analytics
CREATE INDEX IX_ProductView_ViewDate ON ProductView(ViewDate);

-- Index for shopping cart management
CREATE INDEX IX_ShoppingCart_UserID ON ShoppingCart(UserID);
CREATE INDEX IX_ShoppingCart_SessionID ON ShoppingCart(SessionID);

-- Index for order item lookups
CREATE INDEX IX_OrderItem_ProductID ON OrderItem(ProductID);

-- Index for shopping cart item lookups
CREATE INDEX IX_ShoppingCartItem_ProductID ON ShoppingCartItem(ProductID); 