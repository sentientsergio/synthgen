# SynthGen: E-commerce Synthetic Data Generation Demo

This document provides a step-by-step walkthrough of the SynthGen e-commerce data generation demo, explaining the process, input files, intermediate representations, and output files.

## Overview

SynthGen is a sophisticated synthetic data generation system that can create realistic, coherent data based on a database schema, reference data, and generation rules. The e-commerce demo showcases the system's capabilities by generating a complete synthetic e-commerce dataset with users, products, orders, reviews, and more.

The process involves four main steps:

1. Parse the SQL schema
2. Process reference data
3. Load generation rules
4. Generate synthetic data

## Input Files

The demo uses three primary input files:

### 1. SQL Schema (`/samples/sql/ecommerce.sql`)

This file contains the SQL DDL (Data Definition Language) statements that define the structure of the e-commerce database. It includes:

- 33 tables covering all aspects of an e-commerce system
- Foreign key relationships between tables
- Constraints and indexes
- Column data types and descriptions

The schema includes tables for:

- Reference/lookup tables (Countries, Currencies, Payment methods)
- User management (User accounts, addresses, payment methods)
- Product management (Products, variants, images, reviews)
- Order management (Orders, items, history, shipping)
- Marketing & analytics (Wishlists, product views, user searches)

[View the Input Schema File](/Users/sergio/synthgen/runs/ecommerce_1747192906/inputs/ecommerce.sql)

### 2. Reference Data (`/samples/ecommerce_reference.csv`)

This CSV file contains pre-defined reference data for lookup tables in the schema. It provides baseline data for tables like:

- Countries and states
- Currencies
- Product categories and brands
- Payment methods
- Shipping methods
- User roles and statuses

The reference data ensures that generated data has realistic values for these core entities and maintains referential integrity.

[View the Reference Data File](/Users/sergio/synthgen/runs/ecommerce_1747192906/inputs/ecommerce_reference.csv)

### 3. Generation Rules (`/samples/rules/ecommerce_rules.json`)

This JSON file defines rules and patterns for data generation, including:

- Value patterns (e.g., email formats based on user names)
- Conditional rules (e.g., different price ranges for different product categories)
- Relationship rules (e.g., related products often purchased together)
- Conceptual patterns (e.g., shopping behavior, inventory levels, product ratings)

These rules guide the data generation process to create realistic relationships and distributions in the data.

[View the Rules File](/Users/sergio/synthgen/runs/ecommerce_1747192906/inputs/ecommerce_rules.json)

## Intermediate Representation (IR) Files

During the process, SynthGen creates several IR (Intermediate Representation) files that represent the processed input data in a standardized format. These files are stored in the `/runs/[run_id]/ir/` directory:

### 1. Schema IR (`schema_ir.json`)

This file contains the parsed SQL schema in a structured JSON format. It includes all tables, columns, data types, primary keys, foreign keys, and constraints from the SQL schema. The parser extracts this information and organizes it in a way that's easy for the downstream components to use.

[View the Schema IR File](/Users/sergio/synthgen/runs/ecommerce_1747192906/ir/schema_ir.json)

### 2. Reference Data IR (`ref_data_ir.json`)

This file extends the schema IR by incorporating the reference data. It maps the data from the CSV file to the appropriate tables and columns in the schema, creating a unified representation of the database structure with pre-populated reference data.

[View the Reference Data IR File](/Users/sergio/synthgen/runs/ecommerce_1747192906/ir/ref_data_ir.json)

### 3. Rules IR (`rules_ir.json`)

This file contains the processed generation rules in a format that's ready to be consumed by the data synthesis agent. It maps rules to specific tables and columns and provides the detailed instructions for generating synthetic data.

[View the Rules IR File](/Users/sergio/synthgen/runs/ecommerce_1747192906/ir/rules_ir.json)

## Traces and Logging

SynthGen maintains detailed traces and logs of the generation process in the `/runs/[run_id]/traces/` directory:

### 1. Agent Prompts and Responses

For each LLM call, the system saves:

- The prompt sent to the LLM (`*_prompt.md`)
- The raw response from the LLM (`llm_response_*.md`)
- The processed data extracted from the response (`data_*.md`)

These traces provide transparency into how the system is generating data and can be used for debugging or improving the generation process.

[Browse All Traces](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces)

Example traces:

- [Schema Parser Prompt](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces/SchemaParser_prompt.md)
- [DataSynthAgent Prompt (Product)](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces/DataSynthAgent_prompt.md)
- [LLM Response (User table)](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces/llm_response_User.md)
- [Generated Data (Product table)](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces/data_Product.md)

### 2. Input/Output Schema

The system also saves copies of the schema before and after processing:

- [Input Schema](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces/input_schema.json)
- [Output Schema](/Users/sergio/synthgen/runs/ecommerce_1747192906/traces/ecommerce_1747192906/traces/output_schema.json)

These can be used to track changes and transformations.

## Output Files

The final output of the demo is a set of CSV files representing the generated data for each table in the schema. These files are stored in the `/runs/[run_id]/outputs/` directory.

[Browse All Output Files](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs)

The main output files include:

### Reference Data Files

- [Country.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/Country.csv), [StateProvince.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/StateProvince.csv) - Geographical data
- [Currency.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/Currency.csv) - Currency information
- [PaymentMethod.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/PaymentMethod.csv), [ShippingMethod.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ShippingMethod.csv) - Transaction methods
- [OrderStatus.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/OrderStatus.csv), [UserStatus.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/UserStatus.csv), [UserRole.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/UserRole.csv) - Status and role definitions
- [ProductCategory.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ProductCategory.csv), [ProductBrand.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ProductBrand.csv) - Product categorization

### Core Data Files

- [User.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/User.csv) - User accounts with profiles and preferences
- [UserAddress.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/UserAddress.csv) - User shipping and billing addresses
- [UserPaymentMethod.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/UserPaymentMethod.csv) - User payment methods (tokenized for security)
- [Product.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/Product.csv) - Product information including pricing and inventory
- [ProductVariant.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ProductVariant.csv) - Product size/color variations
- [ProductImage.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ProductImage.csv) - Product images and display order
- [ProductReview.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ProductReview.csv) - User reviews and ratings of products

### Transaction Data Files

- [Order.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/Order.csv) - Order header information
- [OrderItem.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/OrderItem.csv) - Individual line items in orders
- [OrderHistory.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/OrderHistory.csv) - Status changes of orders
- [ShippingEvent.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ShippingEvent.csv) - Shipping and delivery information
- [OrderPromotion.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/OrderPromotion.csv) - Promotions applied to orders

### Marketing Data Files

- [Promotion.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/Promotion.csv), [PromotionProduct.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/PromotionProduct.csv), [PromotionCategory.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/PromotionCategory.csv) - Marketing promotions
- [WishList.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/WishList.csv), [WishListItem.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/WishListItem.csv) - User wishlists
- [ProductView.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/ProductView.csv) - Product view tracking
- [UserSearch.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/UserSearch.csv) - User search history
- [EmailSubscription.csv](/Users/sergio/synthgen/runs/ecommerce_1747192906/outputs/EmailSubscription.csv) - Email marketing subscriptions

All output files maintain referential integrity, with foreign keys properly linking related records across tables.

## Step-by-Step Process

### 1. Schema Parsing

The SchemaParseAgent processes the SQL schema file and extracts the structure, including tables, columns, data types, relationships, and constraints. It handles complex SQL syntax and builds a comprehensive representation of the database structure.

```
=== STEP 1: Parse SQL Schema ===
```

The agent processes the schema table by table, extracting all the necessary metadata and building the IR. This step is crucial as it forms the foundation for all subsequent data generation.

### 2. Reference Data Processing

The RefDataAgent takes the schema IR and the reference data file, mapping the CSV data to the appropriate tables and columns. This process involves:

- Identifying which tables the reference data belongs to
- Mapping columns from the CSV to the schema
- Validating the data against schema constraints
- Integrating the data into the schema IR

```
=== STEP 2: Process Reference Data ===
```

This step ensures that all reference tables have appropriate data that can be used when generating foreign key references.

### 3. Rules Loading

The system loads the generation rules from the rules JSON file, preparing them for use in the data generation process.

```
=== STEP 3: Load Rules ===
```

These rules add sophistication to the generated data, ensuring it follows realistic patterns and distributions.

### 4. Synthetic Data Generation

The DataSynthAgent is the core of the system, generating synthetic data for all tables in the schema. It works in a specific order to maintain referential integrity:

1. Generate reference/lookup tables first
2. Process tables in dependency order (tables referenced by foreign keys before the tables with those foreign keys)
3. Use LLM generation in batches of 20 rows
4. Fall back to algorithmic generation only when necessary

```
=== STEP 4: Generate Synthetic Data ===
```

For each table, the agent:

1. Creates a detailed prompt describing the table structure, constraints, and any reference data
2. Calls the LLM to generate data in JSON format
3. Processes and validates the generated data
4. Converts the data to the appropriate types
5. Writes the data to a CSV file

The agent implements safeguards to ensure:

- Primary key uniqueness
- Foreign key validity
- Data type conformance
- Constraint satisfaction

### 5. Results Summarization

Finally, the system summarizes the results, providing statistics about the generated data:

```
=== STEP 5: Summarize Results ===
```

This includes counts of generated entities (users, products, orders, etc.) and a list of all output files with their sizes.

## Running the Demo

To run the demo yourself:

```bash
cd /path/to/synthgen
python samples/ecommerce_demo.py
```

You can customize the generation by providing command-line arguments:

```bash
python samples/ecommerce_demo.py --users 200 --products 500 --orders 1000 --reviews 300
```

You can also change which LLM model is used by modifying the `DEFAULT_LLM_MODEL` in [constants.py](/Users/sergio/synthgen/constants.py).

After running the demo, you'll find all outputs in a timestamped directory under the `runs/` folder.

## Understanding the Generated Data

The generated data maintains complex relationships between entities, such as:

- Users have addresses and payment methods
- Orders reference users, addresses, and payment methods
- Order items reference products and their variants
- Product reviews are tied to both users and products

This comprehensive, interconnected dataset can be used for:

- Testing e-commerce applications
- Populating development environments
- Training machine learning models
- Prototyping data visualizations and analytics
- Benchmarking database performance

The data follows realistic patterns defined in the rules file, such as:

- Order frequency increases during evenings and weekends
- Product prices vary by category
- User shopping behaviors follow typical segmentation patterns
- Promotional usage correlates with order size and customer history

## Customization

The demo can be customized in several ways:

1. Modify the SQL schema to add or change tables
2. Edit the reference data to change lookup values
3. Adjust the generation rules to create different data patterns
4. Update the constants.py file to change the LLM model or other system settings

## Conclusion

The SynthGen e-commerce demo showcases a powerful approach to synthetic data generation that combines the strengths of LLMs with structured data constraints. By following this process, you can generate high-quality synthetic data for any database schema, maintaining referential integrity and realistic data distributions.
