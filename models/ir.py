"""
Intermediate Representation (IR) model for SQL Server schemas.

This module defines the data structures that represent SQL Server schemas,
tables, columns, constraints, etc., which will be passed between agents
in the pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from constants import IR_SCHEMA_VERSION


class ColumnType(Enum):
    """SQL Server column data types."""
    INTEGER = auto()
    BIGINT = auto()
    SMALLINT = auto()
    TINYINT = auto()
    DECIMAL = auto()
    NUMERIC = auto()
    FLOAT = auto()
    REAL = auto()
    MONEY = auto()
    BIT = auto()
    CHAR = auto()
    VARCHAR = auto()
    TEXT = auto()
    NCHAR = auto()
    NVARCHAR = auto()
    NTEXT = auto()
    DATE = auto()
    DATETIME = auto()
    DATETIME2 = auto()
    SMALLDATETIME = auto()
    TIME = auto()
    DATETIMEOFFSET = auto()
    UNIQUEIDENTIFIER = auto()
    XML = auto()
    BINARY = auto()
    VARBINARY = auto()
    IMAGE = auto()
    JSON = auto()
    UNKNOWN = auto()

    @classmethod
    def from_sql_type(cls, sql_type: str) -> 'ColumnType':
        """Convert SQL type string to ColumnType.
        
        Args:
            sql_type: SQL type string (e.g., 'INT', 'NVARCHAR')
        
        Returns:
            Corresponding ColumnType
        """
        type_map = {
            'INT': cls.INTEGER,
            'INTEGER': cls.INTEGER,
            'BIGINT': cls.BIGINT,
            'SMALLINT': cls.SMALLINT,
            'TINYINT': cls.TINYINT,
            'DECIMAL': cls.DECIMAL,
            'NUMERIC': cls.NUMERIC,
            'FLOAT': cls.FLOAT,
            'REAL': cls.REAL,
            'MONEY': cls.MONEY,
            'SMALLMONEY': cls.MONEY,
            'BIT': cls.BIT,
            'CHAR': cls.CHAR,
            'VARCHAR': cls.VARCHAR,
            'TEXT': cls.TEXT,
            'NCHAR': cls.NCHAR,
            'NVARCHAR': cls.NVARCHAR,
            'NTEXT': cls.NTEXT,
            'DATE': cls.DATE,
            'DATETIME': cls.DATETIME,
            'DATETIME2': cls.DATETIME2,
            'SMALLDATETIME': cls.SMALLDATETIME,
            'TIME': cls.TIME,
            'DATETIMEOFFSET': cls.DATETIMEOFFSET,
            'UNIQUEIDENTIFIER': cls.UNIQUEIDENTIFIER,
            'XML': cls.XML,
            'BINARY': cls.BINARY,
            'VARBINARY': cls.VARBINARY,
            'IMAGE': cls.IMAGE,
            'JSON': cls.JSON,
        }
        
        # Remove parentheses and parameters from type
        # e.g., 'NVARCHAR(50)' -> 'NVARCHAR'
        sql_type = sql_type.split('(')[0].strip().upper()
        
        return type_map.get(sql_type, cls.UNKNOWN)


@dataclass
class Column:
    """Represents a column in a SQL Server table."""
    name: str
    data_type: ColumnType
    nullable: bool = True
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    default_value: Optional[str] = None
    is_identity: bool = False
    is_computed: bool = False
    description: Optional[str] = None
    
    @property
    def is_numeric(self) -> bool:
        """Check if column is a numeric type."""
        numeric_types = {
            ColumnType.INTEGER,
            ColumnType.BIGINT,
            ColumnType.SMALLINT,
            ColumnType.TINYINT,
            ColumnType.DECIMAL,
            ColumnType.NUMERIC,
            ColumnType.FLOAT,
            ColumnType.REAL,
            ColumnType.MONEY,
        }
        return self.data_type in numeric_types
    
    @property
    def is_string(self) -> bool:
        """Check if column is a string type."""
        string_types = {
            ColumnType.CHAR,
            ColumnType.VARCHAR,
            ColumnType.TEXT,
            ColumnType.NCHAR,
            ColumnType.NVARCHAR,
            ColumnType.NTEXT,
        }
        return self.data_type in string_types
    
    @property
    def is_datetime(self) -> bool:
        """Check if column is a datetime type."""
        datetime_types = {
            ColumnType.DATE,
            ColumnType.DATETIME,
            ColumnType.DATETIME2,
            ColumnType.SMALLDATETIME,
            ColumnType.TIME,
            ColumnType.DATETIMEOFFSET,
        }
        return self.data_type in datetime_types
    
    @property
    def is_boolean(self) -> bool:
        """Check if column is a boolean type."""
        return self.data_type == ColumnType.BIT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the column
        """
        return {
            "name": self.name,
            "data_type": self.data_type.name,
            "nullable": self.nullable,
            "length": self.length,
            "precision": self.precision,
            "scale": self.scale,
            "default_value": self.default_value,
            "is_identity": self.is_identity,
            "is_computed": self.is_computed,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Column':
        """Create a Column from a dictionary.
        
        Args:
            data: Dictionary representation of the column
        
        Returns:
            Column instance
        """
        return cls(
            name=data["name"],
            data_type=ColumnType[data["data_type"]],
            nullable=data.get("nullable", True),
            length=data.get("length"),
            precision=data.get("precision"),
            scale=data.get("scale"),
            default_value=data.get("default_value"),
            is_identity=data.get("is_identity", False),
            is_computed=data.get("is_computed", False),
            description=data.get("description"),
        )


@dataclass
class PrimaryKey:
    """Represents a primary key constraint in a SQL Server table."""
    name: str
    columns: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "columns": self.columns,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrimaryKey':
        """Create a PrimaryKey from a dictionary."""
        return cls(
            name=data["name"],
            columns=data["columns"],
        )


@dataclass
class ForeignKey:
    """Represents a foreign key constraint in a SQL Server table."""
    name: str
    columns: List[str]
    ref_table: str
    ref_columns: List[str]
    on_delete: Optional[str] = None  # NO ACTION, CASCADE, SET NULL, SET DEFAULT
    on_update: Optional[str] = None  # NO ACTION, CASCADE, SET NULL, SET DEFAULT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "columns": self.columns,
            "ref_table": self.ref_table,
            "ref_columns": self.ref_columns,
            "on_delete": self.on_delete,
            "on_update": self.on_update,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ForeignKey':
        """Create a ForeignKey from a dictionary."""
        return cls(
            name=data["name"],
            columns=data["columns"],
            ref_table=data["ref_table"],
            ref_columns=data["ref_columns"],
            on_delete=data.get("on_delete"),
            on_update=data.get("on_update"),
        )


@dataclass
class Index:
    """Represents an index in a SQL Server table."""
    name: str
    columns: List[str]
    is_unique: bool = False
    is_clustered: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "columns": self.columns,
            "is_unique": self.is_unique,
            "is_clustered": self.is_clustered,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Index':
        """Create an Index from a dictionary."""
        return cls(
            name=data["name"],
            columns=data["columns"],
            is_unique=data.get("is_unique", False),
            is_clustered=data.get("is_clustered", False),
        )


@dataclass
class CheckConstraint:
    """Represents a CHECK constraint in a SQL Server table."""
    name: str
    definition: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "definition": self.definition,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckConstraint':
        """Create a CheckConstraint from a dictionary."""
        return cls(
            name=data["name"],
            definition=data["definition"],
        )


@dataclass
class UniqueConstraint:
    """Represents a UNIQUE constraint in a SQL Server table."""
    name: str
    columns: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "columns": self.columns,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniqueConstraint':
        """Create a UniqueConstraint from a dictionary."""
        return cls(
            name=data["name"],
            columns=data["columns"],
        )


@dataclass
class DefaultConstraint:
    """Represents a DEFAULT constraint in a SQL Server table."""
    name: str
    column: str
    definition: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "column": self.column,
            "definition": self.definition,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DefaultConstraint':
        """Create a DefaultConstraint from a dictionary."""
        return cls(
            name=data["name"],
            column=data["column"],
            definition=data["definition"],
        )


@dataclass
class ReferenceData:
    """Represents reference data for a table."""
    rows: List[Dict[str, Any]]
    distribution_strategy: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "rows": self.rows,
        }
        if self.distribution_strategy:
            result["distribution_strategy"] = self.distribution_strategy
        if self.description:
            result["description"] = self.description
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferenceData':
        """Create a ReferenceData from a dictionary."""
        return cls(
            rows=data["rows"],
            distribution_strategy=data.get("distribution_strategy"),
            description=data.get("description"),
        )
    
    def get_weighted_distribution(self) -> Dict[int, float]:
        """
        Get a mapping of row indices to their normalized weights.
        
        If weights are specified in the rows, use those.
        Otherwise, use equal weights for all rows.
        
        Returns:
            Dictionary mapping row indices to normalized weights
        """
        weights = {}
        
        # Check if rows have weight attribute
        has_weights = any("weight" in row for row in self.rows)
        
        if has_weights:
            # Extract weights from rows
            total_weight = 0.0
            for i, row in enumerate(self.rows):
                weight = float(row.get("weight", 1.0))
                weights[i] = weight
                total_weight += weight
                
            # Normalize weights
            if total_weight > 0:
                for i in weights:
                    weights[i] /= total_weight
        else:
            # Equal weights if none specified
            equal_weight = 1.0 / len(self.rows) if self.rows else 0.0
            weights = {i: equal_weight for i in range(len(self.rows))}
        
        return weights


@dataclass
class Table:
    """Represents a table in a SQL Server database."""
    name: str
    columns: List[Column]
    primary_key: Optional[PrimaryKey] = None
    foreign_keys: List[ForeignKey] = field(default_factory=list)
    indices: List[Index] = field(default_factory=list)
    check_constraints: List[CheckConstraint] = field(default_factory=list)
    unique_constraints: List[UniqueConstraint] = field(default_factory=list)
    default_constraints: List[DefaultConstraint] = field(default_factory=list)
    reference_data: Optional[ReferenceData] = None
    description: Optional[str] = None
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name.
        
        Args:
            name: Column name
        
        Returns:
            Column object or None if not found
        """
        for column in self.columns:
            if column.name.lower() == name.lower():
                return column
        return None
    
    @property
    def is_reference_table(self) -> bool:
        """Determine if this is a reference table.
        
        Reference tables are typically small lookup tables used for
        foreign key references. They usually have a small number of
        columns, a primary key, and often contain a "code" and "description" pair.
        
        Returns:
            True if this appears to be a reference table
        """
        # If it has reference data loaded, it's definitely a reference table
        if self.reference_data is not None and hasattr(self.reference_data, 'rows') and len(self.reference_data.rows) > 0:
            return True
        
        # If the table name clearly indicates it's a reference table
        name_lower = self.name.lower()
        reference_indicators = ["lookup", "reference", "type", "status", "code"]
        if any(indicator in name_lower for indicator in reference_indicators):
            # But only if it's a small table with a primary key
            if len(self.columns) <= 5 and self.primary_key is not None:
                return True
        
        # If it has few columns and many foreign keys reference it, it's likely a reference table
        # This would require checking across all tables, which we don't have context for here
        
        # Default to considering it NOT a reference table
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "columns": [col.to_dict() for col in self.columns],
            "primary_key": self.primary_key.to_dict() if self.primary_key else None,
            "foreign_keys": [fk.to_dict() for fk in self.foreign_keys],
            "indices": [idx.to_dict() for idx in self.indices],
            "check_constraints": [cc.to_dict() for cc in self.check_constraints],
            "unique_constraints": [uc.to_dict() for uc in self.unique_constraints],
            "default_constraints": [dc.to_dict() for dc in self.default_constraints],
            "reference_data": self.reference_data.to_dict() if self.reference_data else None,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """Create a Table from a dictionary."""
        return cls(
            name=data["name"],
            columns=[Column.from_dict(col) for col in data["columns"]],
            primary_key=PrimaryKey.from_dict(data["primary_key"]) if data.get("primary_key") else None,
            foreign_keys=[ForeignKey.from_dict(fk) for fk in data.get("foreign_keys", [])],
            indices=[Index.from_dict(idx) for idx in data.get("indices", [])],
            check_constraints=[CheckConstraint.from_dict(cc) for cc in data.get("check_constraints", [])],
            unique_constraints=[UniqueConstraint.from_dict(uc) for uc in data.get("unique_constraints", [])],
            default_constraints=[DefaultConstraint.from_dict(dc) for dc in data.get("default_constraints", [])],
            reference_data=ReferenceData.from_dict(data["reference_data"]) if data.get("reference_data") else None,
            description=data.get("description"),
        )


@dataclass
class GenerationRule:
    """Represents a rule for synthetic data generation."""
    rule_id: str
    rule_type: str  # e.g., "value", "distribution", "relationship"
    target: str  # table.column or table
    definition: Dict[str, Any]  # Rule-specific definition
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "target": self.target,
            "definition": self.definition,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationRule':
        """Create a GenerationRule from a dictionary."""
        return cls(
            rule_id=data["rule_id"],
            rule_type=data["rule_type"],
            target=data["target"],
            definition=data["definition"],
            description=data.get("description"),
        )


@dataclass
class Schema:
    """Represents a complete SQL Server schema."""
    name: str
    tables: List[Table]
    generation_rules: List[GenerationRule] = field(default_factory=list)
    ir_version: str = IR_SCHEMA_VERSION
    description: Optional[str] = None
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get a table by name.
        
        Args:
            name: Table name
        
        Returns:
            Table object or None if not found
        """
        for table in self.tables:
            if table.name.lower() == name.lower():
                return table
        return None
    
    def get_reference_tables(self) -> List[Table]:
        """Get all reference tables in the schema.
        
        Returns:
            List of reference tables
        """
        return [table for table in self.tables if table.is_reference_table]
    
    def get_data_tables(self) -> List[Table]:
        """Get all non-reference tables in the schema.
        
        Returns:
            List of data tables
        """
        return [table for table in self.tables if not table.is_reference_table]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "tables": [table.to_dict() for table in self.tables],
            "generation_rules": [rule.to_dict() for rule in self.generation_rules],
            "ir_version": self.ir_version,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schema':
        """Create a Schema from a dictionary."""
        return cls(
            name=data["name"],
            tables=[Table.from_dict(table) for table in data["tables"]],
            generation_rules=[GenerationRule.from_dict(rule) for rule in data.get("generation_rules", [])],
            ir_version=data.get("ir_version", "1.0.0"),
            description=data.get("description"),
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string.
        
        Args:
            indent: Number of spaces for indentation
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Schema':
        """Create a Schema from a JSON string.
        
        Args:
            json_str: JSON string representation
        
        Returns:
            Schema instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: Union[str, Path], indent: int = 2) -> None:
        """Save the schema to a JSON file.
        
        Args:
            file_path: Path to save the file
            indent: Number of spaces for indentation
        """
        with open(file_path, 'w') as f:
            f.write(self.to_json(indent=indent))
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'Schema':
        """Load a schema from a JSON file.
        
        Args:
            file_path: Path to the JSON file
        
        Returns:
            Schema instance
        """
        with open(file_path, 'r') as f:
            return cls.from_json(f.read()) 