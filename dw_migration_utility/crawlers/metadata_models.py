"""
Data models for database metadata.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any, Dict
from datetime import datetime
import json


@dataclass
class ColumnMetadata:
    """Metadata for a database column."""
    name: str
    data_type: str
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    nullable: bool = True
    default_value: Optional[str] = None
    comment: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class IndexMetadata:
    """Metadata for a database index."""
    name: str
    columns: List[str]
    is_unique: bool = False
    index_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ConstraintMetadata:
    """Metadata for a database constraint."""
    name: str
    constraint_type: str  # PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
    columns: List[str]
    reference_table: Optional[str] = None
    reference_columns: Optional[List[str]] = None
    check_condition: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TableMetadata:
    """Metadata for a database table."""
    schema: str
    table_name: str
    columns: List[ColumnMetadata] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[ConstraintMetadata] = field(default_factory=list)
    indexes: List[IndexMetadata] = field(default_factory=list)
    constraints: List[ConstraintMetadata] = field(default_factory=list)
    row_count: int = 0
    table_size_bytes: int = 0
    comment: Optional[str] = None
    partitioning_info: Optional[Dict[str, Any]] = None
    clustering_keys: List[str] = field(default_factory=list)
    created_date: Optional[datetime] = None
    last_modified_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'schema': self.schema,
            'table_name': self.table_name,
            'columns': [col.to_dict() for col in self.columns],
            'primary_keys': self.primary_keys,
            'foreign_keys': [fk.to_dict() for fk in self.foreign_keys],
            'indexes': [idx.to_dict() for idx in self.indexes],
            'constraints': [cons.to_dict() for cons in self.constraints],
            'row_count': self.row_count,
            'table_size_bytes': self.table_size_bytes,
            'comment': self.comment,
            'partitioning_info': self.partitioning_info,
            'clustering_keys': self.clustering_keys,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'last_modified_date': self.last_modified_date.isoformat() if self.last_modified_date else None
        }

    def get_column(self, column_name: str) -> Optional[ColumnMetadata]:
        """Get column metadata by name."""
        for col in self.columns:
            if col.name.upper() == column_name.upper():
                return col
        return None

    def get_primary_key_columns(self) -> List[ColumnMetadata]:
        """Get list of primary key column metadata."""
        return [col for col in self.columns if col.is_primary_key]


@dataclass
class SchemaMetadata:
    """Metadata for a database schema."""
    database: Optional[str] = None  # For Snowflake
    schema_name: str = ""
    tables: List[TableMetadata] = field(default_factory=list)
    views: List[str] = field(default_factory=list)
    total_tables: int = 0
    total_views: int = 0
    extraction_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'database': self.database,
            'schema_name': self.schema_name,
            'tables': [table.to_dict() for table in self.tables],
            'views': self.views,
            'total_tables': self.total_tables,
            'total_views': self.total_views,
            'extraction_date': self.extraction_date.isoformat()
        }

    def get_table(self, table_name: str) -> Optional[TableMetadata]:
        """Get table metadata by name."""
        for table in self.tables:
            if table.table_name.upper() == table_name.upper():
                return table
        return None

    def save_to_json(self, output_path: str) -> None:
        """Save metadata to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load_from_json(cls, input_path: str) -> 'SchemaMetadata':
        """Load metadata from JSON file."""
        with open(input_path, 'r') as f:
            data = json.load(f)

        schema = cls(
            database=data.get('database'),
            schema_name=data['schema_name'],
            total_tables=data.get('total_tables', 0),
            total_views=data.get('total_views', 0),
            extraction_date=datetime.fromisoformat(data['extraction_date'])
        )

        # Reconstruct tables
        for table_data in data.get('tables', []):
            columns = [ColumnMetadata(**col) for col in table_data.get('columns', [])]
            foreign_keys = [ConstraintMetadata(**fk) for fk in table_data.get('foreign_keys', [])]
            indexes = [IndexMetadata(**idx) for idx in table_data.get('indexes', [])]
            constraints = [ConstraintMetadata(**cons) for cons in table_data.get('constraints', [])]

            table = TableMetadata(
                schema=table_data['schema'],
                table_name=table_data['table_name'],
                columns=columns,
                primary_keys=table_data.get('primary_keys', []),
                foreign_keys=foreign_keys,
                indexes=indexes,
                constraints=constraints,
                row_count=table_data.get('row_count', 0),
                table_size_bytes=table_data.get('table_size_bytes', 0),
                comment=table_data.get('comment'),
                partitioning_info=table_data.get('partitioning_info'),
                clustering_keys=table_data.get('clustering_keys', []),
                created_date=datetime.fromisoformat(table_data['created_date']) if table_data.get('created_date') else None,
                last_modified_date=datetime.fromisoformat(table_data['last_modified_date']) if table_data.get('last_modified_date') else None
            )
            schema.tables.append(table)

        return schema


@dataclass
class DataProfile:
    """Data profiling statistics for a column."""
    column_name: str
    null_count: int = 0
    null_percentage: float = 0.0
    distinct_count: int = 0
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    avg_value: Optional[Any] = None
    sample_values: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TableProfile:
    """Data profiling for a table."""
    schema: str
    table_name: str
    row_count: int
    column_profiles: List[DataProfile] = field(default_factory=list)
    profiling_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'schema': self.schema,
            'table_name': self.table_name,
            'row_count': self.row_count,
            'column_profiles': [prof.to_dict() for prof in self.column_profiles],
            'profiling_date': self.profiling_date.isoformat()
        }
