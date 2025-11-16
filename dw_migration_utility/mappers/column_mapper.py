"""
Column-level mapping for Oracle to Snowflake migration.
"""
from typing import Dict, List, Optional, Tuple
from loguru import logger

from .fuzzy_matcher import FuzzyMatcher
from ..crawlers.metadata_models import TableMetadata, ColumnMetadata


class ColumnMapper:
    """Map columns between Oracle and Snowflake tables."""

    # Data type mappings
    ORACLE_TO_SNOWFLAKE_TYPES = {
        'VARCHAR2': 'VARCHAR',
        'CHAR': 'CHAR',
        'NUMBER': 'DECIMAL',
        'INTEGER': 'INTEGER',
        'FLOAT': 'FLOAT',
        'DATE': 'DATE',
        'TIMESTAMP': 'TIMESTAMP_NTZ',
        'TIMESTAMP WITH TIME ZONE': 'TIMESTAMP_TZ',
        'CLOB': 'VARCHAR',
        'BLOB': 'BINARY',
        'RAW': 'BINARY',
        'LONG': 'VARCHAR',
        'LONG RAW': 'BINARY',
        'NVARCHAR2': 'VARCHAR',
        'NCHAR': 'CHAR',
    }

    def __init__(self, fuzzy_matcher: FuzzyMatcher = None):
        """
        Initialize column mapper.

        Args:
            fuzzy_matcher: FuzzyMatcher instance
        """
        self.fuzzy_matcher = fuzzy_matcher or FuzzyMatcher()
        self.column_mappings = {}

    def map_columns(
        self,
        oracle_table: TableMetadata,
        snowflake_table: TableMetadata,
        manual_mappings: Dict[str, str] = None,
        use_data_type_matching: bool = True
    ) -> Dict[str, Dict]:
        """
        Map columns from Oracle table to Snowflake table.

        Args:
            oracle_table: Source Oracle table metadata
            snowflake_table: Target Snowflake table metadata
            manual_mappings: Manual column mappings
            use_data_type_matching: Use data type similarity in matching

        Returns:
            Dictionary of column mappings
        """
        logger.info(f"Mapping columns: {oracle_table.schema}.{oracle_table.table_name} -> {snowflake_table.schema}.{snowflake_table.table_name}")

        table_key = f"{oracle_table.schema}.{oracle_table.table_name}"
        self.column_mappings[table_key] = {}

        # Build Snowflake column lookup
        sf_columns = {col.name: col for col in snowflake_table.columns}
        sf_column_names = list(sf_columns.keys())

        # Map each Oracle column
        for oracle_col in oracle_table.columns:
            col_key = oracle_col.name

            # Check manual mappings first
            if manual_mappings and col_key in manual_mappings:
                sf_col_name = manual_mappings[col_key]
                sf_col = sf_columns.get(sf_col_name)

                if sf_col:
                    self.column_mappings[table_key][col_key] = {
                        'oracle_column': col_key,
                        'oracle_type': oracle_col.data_type,
                        'snowflake_column': sf_col_name,
                        'snowflake_type': sf_col.data_type,
                        'match_type': 'manual',
                        'match_score': 1.0,
                        'transformation': self._get_type_transformation(oracle_col, sf_col)
                    }
                    logger.debug(f"Manual mapping: {col_key} -> {sf_col_name}")
                    continue

            # Try fuzzy matching
            column_data = [
                {
                    'name': col.name,
                    'data_type': col.data_type,
                    'nullable': col.nullable
                }
                for col in snowflake_table.columns
            ]

            match_result = self.fuzzy_matcher.find_best_match(
                col_key,
                sf_column_names,
                use_normalization=True
            )

            if match_result:
                matched_name, score, match_type = match_result
                sf_col = sf_columns.get(matched_name)

                self.column_mappings[table_key][col_key] = {
                    'oracle_column': col_key,
                    'oracle_type': oracle_col.data_type,
                    'snowflake_column': matched_name,
                    'snowflake_type': sf_col.data_type if sf_col else None,
                    'match_type': match_type,
                    'match_score': score,
                    'transformation': self._get_type_transformation(oracle_col, sf_col) if sf_col else None
                }
                logger.debug(f"Column match: {col_key} -> {matched_name} (score: {score:.2f})")
            else:
                self.column_mappings[table_key][col_key] = {
                    'oracle_column': col_key,
                    'oracle_type': oracle_col.data_type,
                    'snowflake_column': None,
                    'snowflake_type': None,
                    'match_type': 'unmapped',
                    'match_score': 0.0,
                    'manual_review_required': True
                }
                logger.warning(f"No column match found: {col_key}")

        return self.column_mappings[table_key]

    def _get_type_transformation(
        self,
        oracle_col: ColumnMetadata,
        snowflake_col: ColumnMetadata
    ) -> Optional[str]:
        """
        Get transformation needed for column type conversion.

        Args:
            oracle_col: Oracle column metadata
            snowflake_col: Snowflake column metadata

        Returns:
            Transformation SQL or None if no transformation needed
        """
        oracle_type = oracle_col.data_type.upper()
        snowflake_type = snowflake_col.data_type.upper()

        # If types are already compatible, no transformation needed
        if self._types_compatible(oracle_type, snowflake_type):
            return None

        # Check for common type conversions
        if oracle_type == 'CLOB' and 'VARCHAR' in snowflake_type:
            return f"CAST({oracle_col.name} AS VARCHAR({snowflake_col.length or 8000}))"

        if 'BLOB' in oracle_type and 'BINARY' in snowflake_type:
            return f"CAST({oracle_col.name} AS BINARY)"

        if oracle_type == 'DATE' and 'TIMESTAMP' in snowflake_type:
            return f"CAST({oracle_col.name} AS TIMESTAMP_NTZ)"

        if 'VARCHAR' in oracle_type and 'CHAR' in snowflake_type and snowflake_col.length:
            if oracle_col.length and oracle_col.length > snowflake_col.length:
                return f"SUBSTRING({oracle_col.name}, 1, {snowflake_col.length})"
            return f"CAST({oracle_col.name} AS {snowflake_type})"

        # Default transformation
        if oracle_type != snowflake_type:
            return f"CAST({oracle_col.name} AS {snowflake_type})"

        return None

    def _types_compatible(self, oracle_type: str, snowflake_type: str) -> bool:
        """Check if two data types are compatible."""
        # Numeric types
        numeric_oracle = ['NUMBER', 'INTEGER', 'INT', 'FLOAT', 'DECIMAL', 'NUMERIC']
        numeric_sf = ['DECIMAL', 'NUMBER', 'INTEGER', 'INT', 'FLOAT', 'DOUBLE', 'NUMERIC']

        if any(t in oracle_type for t in numeric_oracle) and any(t in snowflake_type for t in numeric_sf):
            return True

        # String types
        string_oracle = ['VARCHAR2', 'CHAR', 'VARCHAR', 'NVARCHAR2', 'NCHAR']
        string_sf = ['VARCHAR', 'CHAR', 'TEXT', 'STRING']

        if any(t in oracle_type for t in string_oracle) and any(t in snowflake_type for t in string_sf):
            return True

        # Date types
        date_oracle = ['DATE', 'TIMESTAMP']
        date_sf = ['DATE', 'TIMESTAMP', 'TIMESTAMP_NTZ', 'TIMESTAMP_LTZ', 'TIMESTAMP_TZ']

        if any(t in oracle_type for t in date_oracle) and any(t in snowflake_type for t in date_sf):
            return True

        # Exact match
        return oracle_type == snowflake_type

    def get_unmapped_columns(self, table_key: str) -> List[str]:
        """
        Get unmapped columns for a table.

        Args:
            table_key: Table key (schema.table)

        Returns:
            List of unmapped column names
        """
        if table_key not in self.column_mappings:
            return []

        return [
            col_name for col_name, mapping in self.column_mappings[table_key].items()
            if mapping.get('match_type') == 'unmapped'
        ]

    def get_columns_needing_transformation(self, table_key: str) -> Dict[str, str]:
        """
        Get columns that need type transformation.

        Args:
            table_key: Table key (schema.table)

        Returns:
            Dictionary of column_name -> transformation_sql
        """
        if table_key not in self.column_mappings:
            return {}

        return {
            col_name: mapping.get('transformation')
            for col_name, mapping in self.column_mappings[table_key].items()
            if mapping.get('transformation')
        }

    def get_mapping_summary(self) -> Dict:
        """
        Get overall mapping summary.

        Returns:
            Summary statistics
        """
        total_tables = len(self.column_mappings)
        total_columns = sum(len(cols) for cols in self.column_mappings.values())
        mapped_columns = sum(
            sum(1 for m in cols.values() if m.get('snowflake_column'))
            for cols in self.column_mappings.values()
        )
        unmapped_columns = total_columns - mapped_columns
        columns_needing_transformation = sum(
            sum(1 for m in cols.values() if m.get('transformation'))
            for cols in self.column_mappings.values()
        )

        return {
            'total_tables': total_tables,
            'total_columns': total_columns,
            'mapped_columns': mapped_columns,
            'unmapped_columns': unmapped_columns,
            'columns_needing_transformation': columns_needing_transformation,
            'mapping_success_rate': (mapped_columns / total_columns * 100) if total_columns > 0 else 0
        }

    def export_mappings(self, output_file: str) -> None:
        """
        Export column mappings to JSON file.

        Args:
            output_file: Path to output file
        """
        import json

        with open(output_file, 'w') as f:
            json.dump({
                'column_mappings': self.column_mappings,
                'summary': self.get_mapping_summary()
            }, f, indent=2)

        logger.info(f"Column mappings exported to: {output_file}")

    def generate_select_statement(self, table_key: str, alias: str = 'SRC') -> str:
        """
        Generate SELECT statement with column mappings and transformations.

        Args:
            table_key: Table key (schema.table)
            alias: Table alias

        Returns:
            SELECT clause SQL
        """
        if table_key not in self.column_mappings:
            return ""

        select_parts = []

        for col_name, mapping in self.column_mappings[table_key].items():
            transformation = mapping.get('transformation')
            sf_col = mapping.get('snowflake_column')

            if sf_col:
                if transformation:
                    select_parts.append(f"{transformation} AS {sf_col}")
                else:
                    select_parts.append(f"{alias}.{col_name} AS {sf_col}")

        return "SELECT\n    " + ",\n    ".join(select_parts)

    def generate_insert_columns(self, table_key: str) -> Tuple[str, str]:
        """
        Generate INSERT column list and values.

        Args:
            table_key: Table key (schema.table)

        Returns:
            Tuple of (column_list, values)
        """
        if table_key not in self.column_mappings:
            return "", ""

        insert_cols = []
        insert_vals = []

        for col_name, mapping in self.column_mappings[table_key].items():
            sf_col = mapping.get('snowflake_column')
            if sf_col:
                insert_cols.append(sf_col)
                insert_vals.append(f"SRC.{col_name}")

        cols_str = ", ".join(insert_cols)
        vals_str = ", ".join(insert_vals)

        return cols_str, vals_str
