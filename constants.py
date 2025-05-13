"""
Constants and configuration values for SynthGen.

This module defines constants and configuration values that are used
throughout the application. Centralizing these values makes it
easier to maintain and update them.
"""

# Default directories
DEFAULT_ARTIFACTS_DIR = "artifacts"
DEFAULT_SCHEMAS_DIR = "schemas"

# LLM defaults
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_LLM_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0

# Pipeline configuration
AGENT_TIMEOUT_SECONDS = 60  # Maximum time for a single agent execution

# Error retry configuration
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0

# IR (Intermediate Representation) schema version
IR_SCHEMA_VERSION = "1.0.0"

# Template for system prompts
SYSTEM_PROMPT_TEMPLATE = """
You are a specialized agent in the SynthGen system, focused on {agent_role}.

Your goal is to {agent_goal}.

{additional_instructions}

Always format your response as valid JSON according to the provided schema:
{json_schema}

Think step-by-step about your approach before providing your final answer.
"""

# File encoding
DEFAULT_ENCODING = "utf-8"

# SQL data types and their corresponding Python/JSON representation
SQL_TYPE_MAPPING = {
    "INT": "integer",
    "BIGINT": "integer",
    "SMALLINT": "integer",
    "TINYINT": "integer",
    "BIT": "boolean",
    "DECIMAL": "number",
    "NUMERIC": "number",
    "FLOAT": "number",
    "REAL": "number",
    "MONEY": "number",
    "SMALLMONEY": "number",
    "CHAR": "string",
    "VARCHAR": "string",
    "TEXT": "string",
    "NCHAR": "string",
    "NVARCHAR": "string",
    "NTEXT": "string",
    "BINARY": "string",
    "VARBINARY": "string",
    "IMAGE": "string",
    "DATE": "string",
    "DATETIME": "string",
    "DATETIME2": "string",
    "DATETIMEOFFSET": "string",
    "SMALLDATETIME": "string",
    "TIME": "string",
    "UNIQUEIDENTIFIER": "string",
    "XML": "string",
    "JSON": "object",
}

# Maximum chunk size for parsing large SQL scripts
MAX_SQL_CHUNK_SIZE = 32000  # In characters 