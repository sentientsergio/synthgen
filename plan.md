# SynthGen Implementation Plan

## Project Structure

```
synthgen/
├── agents/
│   ├── __init__.py
│   ├── base.py                # Base Agent class (✅ DONE)
│   ├── schema_parse_agent.py  # Schema parsing agent (✅ DONE)
│   ├── ref_data_agent.py      # Reference data loading agent (✅ DONE)
│   ├── data_synth_agent.py    # Data synthesis agent
│   ├── validation_agent.py    # Validation agent
│   └── artifact_agent.py      # Artifact writing agent
├── plugins/                   # Extensibility point
├── models/
│   └── ir.py                  # Intermediate Representation models (✅ DONE)
├── utils/
│   ├── __init__.py
│   ├── file_io.py             # File operations (✅ DONE)
│   ├── llm.py                 # LLM API wrapper (✅ DONE - OpenAI & Claude)
│   └── ref_data_parser.py     # Reference data parser (✅ DONE)
├── cli.py                     # Command-line interface (✅ DONE)
├── api.py                     # Python API
├── orchestrator.py            # Pipeline orchestrator (✅ DONE)
├── constants.py               # Configuration constants (✅ DONE)
├── schemas/                   # JSON schemas
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests for individual components
│   │   ├── test_file_io.py    # Tests for file I/O utilities (✅ DONE)
│   │   ├── test_llm.py        # Tests for LLM utilities (✅ DONE)
│   │   ├── test_ir.py         # Tests for IR model (✅ DONE)
│   │   └── test_ref_data_parser.py # Tests for ref data parser (✅ DONE)
│   ├── integration/           # Integration tests across components
│   │   ├── test_schema_parser.py  # Tests for schema parser (✅ DONE)
│   │   └── test_openai_connectivity.py # API key validation tests (✅ DONE)
│   ├── end_to_end/            # Full pipeline tests
│   └── fixtures/              # Test data and fixtures
├── samples/                   # Sample input files
│   ├── test_schema_parser.py  # Schema parser demonstration (✅ DONE)
│   ├── test_ref_data_parser.py # Ref data parser demonstration (✅ DONE)
│   ├── test_ref_data_agent.py # Ref data agent demonstration (✅ DONE)
│   ├── sql/                   # Example SQL schema files
│   ├── ref_data/              # Example reference data files
│   └── rules/                 # Example generation rules
├── docs/                      # Documentation
│   └── API_KEY_MANAGEMENT.md  # API key best practices (✅ DONE)
└── artifacts/                 # Generated artifacts (gitignored)
```

## Development Phases

### Phase 1: Foundation (✅ COMPLETED)

- ✅ Set up project structure
- ✅ Implement base Agent class
- ✅ Create Orchestrator skeleton
- ✅ Set up LLM API integration
- ✅ Implement file I/O utilities
- ✅ Create tests for foundation components

### Phase 2: Core Pipeline (⏳ IN PROGRESS)

- ✅ Implement Schema Parser Agent
- ✅ Define and implement Intermediate Representation (IR) model
- ✅ Enhance API key management and validation
- ✅ Create Reference Data Parser utility
- ✅ Build Reference Data Agent
  - ✅ Support schema-qualified tables
  - ✅ Implement distribution weights for reference data
  - ✅ Create intelligent mapping between schema tables and reference data
- 🔲 Create basic CLI

### Phase 3: Data Generation

- ✅ Implement Data Synthesis Agent
  - ✅ Support distribution weights from reference data
  - ✅ Generate realistic data based on schema constraints
- 🔲 Build Validation Agent
- 🔲 Implement Artifact Agent
- 🔲 Complete CLI functionality

### Phase 4: Refinement

- 🔲 Implement extensibility points (plugins)
- 🔲 Add Python API
- 🔲 Performance optimization
- 🔲 Complete documentation

### Phase 5: Testing & Validation

- 🔲 End-to-end testing
- 🔲 Performance benchmarking
- 🔲 Bug fixes and refinements

## Implementation Approach

We'll take an iterative approach, building and testing each component individually before integrating them into the full pipeline. The focus will be on creating a minimal viable product (MVP) that demonstrates the core functionality, then iteratively refining it based on feedback.

1. Start with implementing the base Agent class and orchestrator
2. Build and test each agent in isolation
3. Integrate agents into the pipeline one by one
4. Test with simple schemas before scaling to more complex ones
5. Add extensibility and optimization features once core functionality is stable

## Progress Summary

### Completed

- **Project Structure**: Created the basic directory structure
- **Base Agent Class**: Implemented the foundation class for all agents
- **Utilities**: Developed file I/O and LLM API wrappers
- **IR Model**: Designed and implemented the Intermediate Representation model with serialization/deserialization
- **Basic Testing**: Created and ran tests for file I/O, LLM utilities, and IR model
- **Schema Parser Agent**: Successfully implemented with proper error handling and response formatting
- **API Key Management**: Enhanced LLM utilities with proper key validation, prioritization of .env file, and helpful error messages
- **Documentation**: Added API key management best practices
- **Reference Data Parser**: Created utility for parsing multi-table CSV files with schema qualification
- **Reference Data Agent**: Implemented agent to load, map, and enhance reference data with distribution weights

### In Progress

- **Data Synthesis Agent**: Next component to be implemented, will leverage reference data with distribution weights

## Recent Updates

### API Key Management and LLM Integration

- Implemented proper dotenv integration with priority over system environment variables
- Added validation for API key formats (OpenAI and Claude/Anthropic)
- Created helpful error messages for misconfigured API keys
- Added documentation for API key management best practices
- Enhanced test scripts to detect and report API key issues

### Schema Parser Agent

- Fixed prompt engineering for more reliable JSON responses
- Added better error handling for failed API calls
- Improved handling of variant response formats
- Successfully tested parsing a sample SQL schema into structured IR
- Added a demonstration script in samples/ directory

### Reference Data Parser

- Implemented parser for multi-table CSV reference data files
- Added support for schema-qualified tables ([SchemaName.TableName])
- Created type inference for reference data columns
- Added utilities for updating existing IR schemas with reference data
- Designed for distribution weights to influence data generation

### Reference Data Agent

- Implemented intelligent mapping of reference data to schema tables
- Added support for both multi-table CSV files and directories of CSV files
- Enhanced IR model with distribution weights for reference data
- Integrated with LLM for intelligent mapping when table names don't match exactly
- Added automatic detection of boolean reference tables with sensible weight distribution
- Created demonstration script with sample schema and reference data

This plan will be updated as development progresses to reflect completed work, changes in approach, and new requirements.

## E-commerce Example Project Proposal

This comprehensive example will demonstrate SynthGen's full capabilities with an e-commerce dataset.

### 1. Enhanced E-commerce Schema

While we have a basic schema (sample.sql), we can expand it to be more representative of real-world e-commerce systems:

```
E-commerce Schema Enhancements:
- Add User/Account tables (separate from Customer)
- Add Shipping and Payment information tables
- Add Product Inventory management
- Add Review/Rating system
- Add Discount/Promotion functionality
- Add geographical tables (Countries, States/Provinces)
```

### 2. Comprehensive Reference Data

Create extensive reference data sets for all lookup tables:

```
Reference Data Sets:
- CustomerStatus: Active, Inactive, Suspended, VIP, etc. with distribution weights
- ProductCategory: Full hierarchy with weights (Electronics 30%, Clothing 25%, Home 20%, etc.)
- Countries: 190+ countries with distribution weights reflecting real-world e-commerce trends
- PaymentMethods: Credit card, PayPal, Bank transfer, etc. with realistic distributions
- ShippingMethods: Standard, Express, Same-day, etc.
- OrderStatus: Pending, Processing, Shipped, Delivered, Cancelled, Returned
- ProductBrands: 50+ popular brands with proper distribution
- UserRoles: Admin, Customer, Support, Marketing, etc.
- Currencies: Major world currencies with exchange rates
```

### 3. Demonstration Rules (12 examples)

A set of diverse generation rules that showcase the rule engine capabilities:

#### Value Pattern Rules

- Email Format Rule: Generate realistic email patterns based on first/last name
- Phone Number Rule: Country-specific phone number formats

#### Distribution Rules

- Price Distribution Rule: Log-normal distribution for product prices
- Order Value Rule: Higher-value orders less frequent than lower-value ones

#### Relationship Rules

- Shopping Pattern Rule: Customers who buy product X likely to buy product Y
- Cross-category Rule: Ensure customers purchase across multiple categories

#### Time-based Rules

- Seasonal Ordering Rule: Increase certain product categories during holidays
- Business Hours Rule: More orders during business hours than overnight

#### Demographic Rules

- Geographic Clustering Rule: Customers from same region buy similar products
- Age Group Preference Rule: Different product preferences by age group

#### Realistic Business Rules

- Repeat Purchase Rule: Customers likely to buy same products again
- Abandoned Cart Rule: Generate realistic cart abandonment scenarios

### Implementation Plan

1. **Schema Enhancement** (1-2 days)

   - Extend the existing sample.sql with additional tables
   - Document the schema relationships and constraints

2. **Reference Data Creation** (2-3 days)

   - Research realistic values and distributions
   - Create CSV files for each reference table with proper weights
   - Document the reasoning behind distributions

3. **Generation Rules Development** (3-4 days)

   - Create the rule JSON definitions
   - Document each rule with examples
   - Write test cases to validate rule behavior

4. **Integration & Testing** (1-2 days)

   - Create a comprehensive sample script that runs the entire pipeline
   - Generate sample data with different rule combinations
   - Validate that generated data follows expected patterns

5. **Documentation** (1 day)
   - Create a detailed guide explaining the example
   - Include visualizations of data distributions
   - Show how to extend and modify the rules
