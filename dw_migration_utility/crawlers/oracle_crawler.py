"""
Oracle database crawler for metadata extraction.
"""
import csv
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd
from loguru import logger

from .metadata_models import (
    SchemaMetadata, TableMetadata, ColumnMetadata,
    IndexMetadata, ConstraintMetadata, DataProfile, TableProfile
)
from ..utils.db_connector import OracleConnector


class OracleCrawler:
    """Crawler for extracting metadata from Oracle database."""

    def __init__(self, connector: OracleConnector, output_dir: str = "output/metadata"):
        """
        Initialize Oracle crawler.

        Args:
            connector: Oracle database connector
            output_dir: Directory to save output files
        """
        self.connector = connector
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def crawl_schema(self, schema_name: str, sample_size: int = 100) -> SchemaMetadata:
        """
        Crawl a specific Oracle schema and extract all metadata.

        Args:
            schema_name: Name of the schema to crawl
            sample_size: Number of sample rows to extract per table

        Returns:
            SchemaMetadata object containing all extracted metadata
        """
        logger.info(f"Starting to crawl Oracle schema: {schema_name}")

        schema_metadata = SchemaMetadata(schema_name=schema_name)

        # Get list of tables in schema
        tables_query = """
            SELECT TABLE_NAME
            FROM ALL_TABLES
            WHERE OWNER = :schema
            ORDER BY TABLE_NAME
        """

        tables = self.connector.execute_query(tables_query, {'schema': schema_name})
        schema_metadata.total_tables = len(tables)

        logger.info(f"Found {len(tables)} tables in schema {schema_name}")

        # Extract metadata for each table
        for idx, (table_name,) in enumerate(tables, 1):
            logger.info(f"Processing table {idx}/{len(tables)}: {table_name}")

            try:
                table_metadata = self.extract_table_metadata(schema_name, table_name)
                schema_metadata.tables.append(table_metadata)

                # Extract sample data
                self.extract_sample_data(schema_name, table_name, sample_size)

                # Profile data
                table_profile = self.profile_table_data(schema_name, table_name, table_metadata)
                self.save_profile(table_profile)

            except Exception as e:
                logger.error(f"Failed to process table {table_name}: {e}")
                continue

        # Get list of views
        views_query = """
            SELECT VIEW_NAME
            FROM ALL_VIEWS
            WHERE OWNER = :schema
            ORDER BY VIEW_NAME
        """
        views = self.connector.execute_query(views_query, {'schema': schema_name})
        schema_metadata.views = [v[0] for v in views]
        schema_metadata.total_views = len(views)

        # Save schema metadata to JSON
        output_file = self.output_dir / f"oracle_{schema_name}_metadata.json"
        schema_metadata.save_to_json(str(output_file))
        logger.info(f"Schema metadata saved to: {output_file}")

        return schema_metadata

    def extract_table_metadata(self, schema: str, table_name: str) -> TableMetadata:
        """
        Extract complete metadata for a specific table.

        Args:
            schema: Schema name
            table_name: Table name

        Returns:
            TableMetadata object
        """
        table_metadata = TableMetadata(schema=schema, table_name=table_name)

        # Get column information
        columns_query = """
            SELECT
                COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION,
                DATA_SCALE, NULLABLE, DATA_DEFAULT, COLUMN_ID
            FROM ALL_TAB_COLUMNS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
            ORDER BY COLUMN_ID
        """
        columns = self.connector.execute_query(columns_query, {'schema': schema, 'table_name': table_name})

        # Get column comments
        col_comments_query = """
            SELECT COLUMN_NAME, COMMENTS
            FROM ALL_COL_COMMENTS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
        """
        col_comments = self.connector.execute_query(col_comments_query, {'schema': schema, 'table_name': table_name})
        comments_dict = {col[0]: col[1] for col in col_comments}

        # Get primary key columns
        pk_query = """
            SELECT COLUMN_NAME
            FROM ALL_CONS_COLUMNS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
            AND CONSTRAINT_NAME IN (
                SELECT CONSTRAINT_NAME FROM ALL_CONSTRAINTS
                WHERE OWNER = :schema AND TABLE_NAME = :table_name
                AND CONSTRAINT_TYPE = 'P'
            )
        """
        pk_cols = self.connector.execute_query(pk_query, {'schema': schema, 'table_name': table_name})
        pk_set = {col[0] for col in pk_cols}
        table_metadata.primary_keys = list(pk_set)

        # Build column metadata
        for col in columns:
            col_metadata = ColumnMetadata(
                name=col[0],
                data_type=col[1],
                length=col[2],
                precision=col[3],
                scale=col[4],
                nullable=col[5] == 'Y',
                default_value=col[6],
                comment=comments_dict.get(col[0]),
                is_primary_key=col[0] in pk_set
            )
            table_metadata.columns.append(col_metadata)

        # Get foreign keys
        fk_query = """
            SELECT
                ac.CONSTRAINT_NAME, acc.COLUMN_NAME,
                ac_ref.TABLE_NAME, acc_ref.COLUMN_NAME
            FROM ALL_CONSTRAINTS ac
            JOIN ALL_CONS_COLUMNS acc ON ac.CONSTRAINT_NAME = acc.CONSTRAINT_NAME
            JOIN ALL_CONSTRAINTS ac_ref ON ac.R_CONSTRAINT_NAME = ac_ref.CONSTRAINT_NAME
            JOIN ALL_CONS_COLUMNS acc_ref ON ac_ref.CONSTRAINT_NAME = acc_ref.CONSTRAINT_NAME
            WHERE ac.OWNER = :schema AND ac.TABLE_NAME = :table_name
            AND ac.CONSTRAINT_TYPE = 'R'
            ORDER BY ac.CONSTRAINT_NAME, acc.POSITION
        """
        fks = self.connector.execute_query(fk_query, {'schema': schema, 'table_name': table_name})

        # Group foreign keys by constraint name
        fk_dict = {}
        for fk in fks:
            constraint_name = fk[0]
            if constraint_name not in fk_dict:
                fk_dict[constraint_name] = {
                    'columns': [],
                    'ref_table': fk[2],
                    'ref_columns': []
                }
            fk_dict[constraint_name]['columns'].append(fk[1])
            fk_dict[constraint_name]['ref_columns'].append(fk[3])

        for constraint_name, fk_info in fk_dict.items():
            fk_metadata = ConstraintMetadata(
                name=constraint_name,
                constraint_type='FOREIGN KEY',
                columns=fk_info['columns'],
                reference_table=fk_info['ref_table'],
                reference_columns=fk_info['ref_columns']
            )
            table_metadata.foreign_keys.append(fk_metadata)

        # Get indexes
        idx_query = """
            SELECT INDEX_NAME, UNIQUENESS
            FROM ALL_INDEXES
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
            AND INDEX_NAME NOT IN (
                SELECT CONSTRAINT_NAME FROM ALL_CONSTRAINTS
                WHERE OWNER = :schema AND TABLE_NAME = :table_name
                AND CONSTRAINT_TYPE IN ('P', 'U')
            )
        """
        indexes = self.connector.execute_query(idx_query, {'schema': schema, 'table_name': table_name})

        for idx in indexes:
            idx_name = idx[0]
            # Get index columns
            idx_cols_query = """
                SELECT COLUMN_NAME
                FROM ALL_IND_COLUMNS
                WHERE INDEX_OWNER = :schema AND INDEX_NAME = :idx_name
                ORDER BY COLUMN_POSITION
            """
            idx_cols = self.connector.execute_query(idx_cols_query, {'schema': schema, 'idx_name': idx_name})

            idx_metadata = IndexMetadata(
                name=idx_name,
                columns=[col[0] for col in idx_cols],
                is_unique=idx[1] == 'UNIQUE'
            )
            table_metadata.indexes.append(idx_metadata)

        # Get row count
        try:
            count_query = f'SELECT COUNT(*) FROM {schema}.{table_name}'
            count_result = self.connector.execute_query(count_query)
            table_metadata.row_count = count_result[0][0] if count_result else 0
        except Exception as e:
            logger.warning(f"Could not get row count for {schema}.{table_name}: {e}")
            table_metadata.row_count = 0

        # Get table comment
        table_comment_query = """
            SELECT COMMENTS
            FROM ALL_TAB_COMMENTS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
        """
        comments = self.connector.execute_query(table_comment_query, {'schema': schema, 'table_name': table_name})
        table_metadata.comment = comments[0][0] if comments and comments[0][0] else None

        # Get partitioning info
        part_query = """
            SELECT PARTITIONING_TYPE, PARTITION_COUNT
            FROM ALL_PART_TABLES
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
        """
        part_info = self.connector.execute_query(part_query, {'schema': schema, 'table_name': table_name})
        if part_info:
            table_metadata.partitioning_info = {
                'type': part_info[0][0],
                'partition_count': part_info[0][1]
            }

        return table_metadata

    def extract_sample_data(self, schema: str, table_name: str, sample_size: int = 100) -> None:
        """
        Extract sample data from a table and save to CSV.

        Args:
            schema: Schema name
            table_name: Table name
            sample_size: Number of rows to sample
        """
        try:
            query = f'SELECT * FROM {schema}.{table_name} WHERE ROWNUM <= {sample_size}'
            results = self.connector.execute_query(query)

            if results:
                # Get column names
                col_names = [desc[0] for desc in self.connector.cursor.description]

                # Save to CSV
                output_file = self.output_dir / f"oracle_{schema}_{table_name}_sample.csv"
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(col_names)
                    writer.writerows(results)

                logger.debug(f"Sample data saved: {output_file}")

        except Exception as e:
            logger.warning(f"Could not extract sample data for {schema}.{table_name}: {e}")

    def profile_table_data(self, schema: str, table_name: str, table_metadata: TableMetadata) -> TableProfile:
        """
        Profile table data to get statistics.

        Args:
            schema: Schema name
            table_name: Table name
            table_metadata: Table metadata

        Returns:
            TableProfile object
        """
        profile = TableProfile(schema=schema, table_name=table_name, row_count=table_metadata.row_count)

        if table_metadata.row_count == 0:
            return profile

        for column in table_metadata.columns:
            try:
                # Get column statistics
                stats_query = f"""
                    SELECT
                        COUNT(*) - COUNT({column.name}) as NULL_COUNT,
                        COUNT(DISTINCT {column.name}) as DISTINCT_COUNT
                    FROM {schema}.{table_name}
                """

                stats = self.connector.execute_query(stats_query)

                if stats:
                    null_count = stats[0][0]
                    distinct_count = stats[0][1]

                    col_profile = DataProfile(
                        column_name=column.name,
                        null_count=null_count,
                        null_percentage=(null_count / table_metadata.row_count * 100) if table_metadata.row_count > 0 else 0,
                        distinct_count=distinct_count
                    )

                    # Get min/max for numeric and date columns
                    if column.data_type in ('NUMBER', 'INTEGER', 'FLOAT', 'DATE', 'TIMESTAMP'):
                        minmax_query = f"SELECT MIN({column.name}), MAX({column.name}) FROM {schema}.{table_name}"
                        minmax = self.connector.execute_query(minmax_query)
                        if minmax:
                            col_profile.min_value = str(minmax[0][0]) if minmax[0][0] else None
                            col_profile.max_value = str(minmax[0][1]) if minmax[0][1] else None

                    # Get sample values (top 5)
                    sample_query = f"SELECT DISTINCT {column.name} FROM {schema}.{table_name} WHERE {column.name} IS NOT NULL AND ROWNUM <= 5"
                    samples = self.connector.execute_query(sample_query)
                    col_profile.sample_values = [str(s[0]) for s in samples]

                    profile.column_profiles.append(col_profile)

            except Exception as e:
                logger.debug(f"Could not profile column {column.name}: {e}")
                continue

        return profile

    def save_profile(self, profile: TableProfile) -> None:
        """
        Save table profile to JSON file.

        Args:
            profile: TableProfile object
        """
        output_file = self.output_dir / f"oracle_{profile.schema}_{profile.table_name}_profile.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2, default=str)

    def crawl_multiple_schemas(self, schema_names: List[str], sample_size: int = 100) -> List[SchemaMetadata]:
        """
        Crawl multiple schemas.

        Args:
            schema_names: List of schema names
            sample_size: Number of sample rows per table

        Returns:
            List of SchemaMetadata objects
        """
        schemas = []
        for schema_name in schema_names:
            try:
                schema_metadata = self.crawl_schema(schema_name, sample_size)
                schemas.append(schema_metadata)
            except Exception as e:
                logger.error(f"Failed to crawl schema {schema_name}: {e}")
                continue

        return schemas
