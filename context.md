# SynthGen Project Context

## Current Project State

SynthGen is a synthetic data generator for SQL Server schemas that uses LLM-based agents to create realistic, constraint-valid data. The project follows a pipeline architecture where each agent handles a specific task in the data generation process.

### Completed Components

- Schema Parser Agent: Parses SQL schema files into an Intermediate Representation (IR)
- Reference Data Parser: Parses multi-table CSV files with schema-qualified tables
- Reference Data Agent: Maps reference data to schema tables with intelligent matching

### Current Focus

- Data Synthesis Agent: Next component to implement, will use reference data with distribution weights

## Key Design Decisions

### IR Model

- Using JSON as the Intermediate Representation
- Added distribution weights to reference data to influence generation patterns
- Enhanced ReferenceData class with `distribution_strategy` and `description` fields

### Schema-Qualified Tables

- Reference data format supports schema qualification: `[SchemaName.TableName]`
- Default schema is "dbo" when not specified

### LLM Integration

- Agents use LLM for intelligent tasks (parsing, mapping, etc.)
- Implemented retry logic with exponential backoff
- Prioritize .env files over system environment variables for API keys

## Development Environment

### Repository

- GitHub: https://github.com/sentientsergio/synthgen.git
- Main branch initialized and pushed

### Important Files

- `utils/ref_data_parser.py`: Multi-table CSV parser with schema support
- `agents/ref_data_agent.py`: Agent for loading and mapping reference data
- `models/ir.py`: Intermediate Representation with distribution weights

## Workflow Notes

### Testing Reference Data

- Created `tests/fixtures/sample_orders_ref_data.csv` for the sample schema
- Added weights for realistic distribution (e.g., more "Active" than "Inactive" records)

### Git Setup

- Initialized with main branch
- Created .gitignore for Python projects
- First commit contains complete Schema Parser and Reference Data components

## Next Steps

1. Implement Data Synthesis Agent that leverages reference data weights
2. Integrate agents into a complete pipeline
3. Add demonstration with a full end-to-end example

See `plan.md` for detailed development phases and progress tracking.
