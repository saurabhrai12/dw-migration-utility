"""
Snowflake database crawler for metadata extraction.
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
from ..utils.db_connector import SnowflakeConnector


class SnowflakeCrawler:
    """Crawler for extracting metadata from Snowflake database."""

    def __init__(self, connector: SnowflakeConnector, output_dir: str = "output/metadata"):
        """
        Initialize Snowflake crawler.

        Args:
            connector: Snowflake database connector
            output_dir: Directory to save output files
        """
        self.connector = connector
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def crawl_schema(self, database: str, schema_name: str, sample_size: int = 100) -> SchemaMetadata:
        """
        Crawl a specific Snowflake schema and extract all metadata.

        Args:
            database: Database name
            schema_name: Name of the schema to crawl
            sample_size: Number of sample rows to extract per table

        Returns:
            SchemaMetadata object containing all extracted metadata
        """
        logger.info(f"Starting to crawl Snowflake schema: {database}.{schema_name}")

        schema_metadata = SchemaMetadata(database=database, schema_name=schema_name)

        # Get list of tables in schema
        tables_query = f"""
            SELECT TABLE_NAME
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema_name}'
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """

        tables = self.connector.execute_query(tables_query)
        schema_metadata.total_tables = len(tables)

        logger.info(f"Found {len(tables)} tables in schema {database}.{schema_name}")

        # Extract metadata for each table
        for idx, table_row in enumerate(tables, 1):
            table_name = table_row['TABLE_NAME']
            logger.info(f"Processing table {idx}/{len(tables)}: {table_name}")

            try:
                table_metadata = self.extract_table_metadata(database, schema_name, table_name)
                schema_metadata.tables.append(table_metadata)

                # Extract sample data
                self.extract_sample_data(database, schema_name, table_name, sample_size)

                # Profile data
                table_profile = self.profile_table_data(database, schema_name, table_name, table_metadata)
                self.save_profile(table_profile)

            except Exception as e:
                logger.error(f"Failed to process table {table_name}: {e}")
                continue

        # Get list of views
        views_query = f"""
            SELECT TABLE_NAME
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema_name}'
            AND TABLE_TYPE = 'VIEW'
            ORDER BY TABLE_NAME
        """
        views = self.connector.execute_query(views_query)
        schema_metadata.views = [v['TABLE_NAME'] for v in views]
        schema_metadata.total_views = len(views)

        # Save schema metadata to JSON
        output_file = self.output_dir / f"snowflake_{database}_{schema_name}_metadata.json"
        schema_metadata.save_to_json(str(output_file))
        logger.info(f"Schema metadata saved to: {output_file}")

        return schema_metadata

    def extract_table_metadata(self, database: str, schema: str, table_name: str) -> TableMetadata:
        """
        Extract complete metadata for a specific table.

        Args:
            database: Database name
            schema: Schema name
            table_name: Table name

        Returns:
            TableMetadata object
        """
        table_metadata = TableMetadata(schema=schema, table_name=table_name)

        # Get column information
        columns_query = f"""
            SELECT
                COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION, NUMERIC_SCALE, IS_NULLABLE,
                COLUMN_DEFAULT, COMMENT, ORDINAL_POSITION
            FROM {database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """
        columns = self.connector.execute_query(columns_query)

        # Get primary key columns
        pk_query = f"""
            SELECT kcu.COLUMN_NAME
            FROM {database}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN {database}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                AND tc.TABLE_NAME = kcu.TABLE_NAME
            WHERE tc.TABLE_SCHEMA = '{schema}'
            AND tc.TABLE_NAME = '{table_name}'
            AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            ORDER BY kcu.ORDINAL_POSITION
        """
        pk_cols = self.connector.execute_query(pk_query)
        pk_set = {col['COLUMN_NAME'] for col in pk_cols}
        table_metadata.primary_keys = list(pk_set)

        # Build column metadata
        for col in columns:
            col_metadata = ColumnMetadata(
                name=col['COLUMN_NAME'],
                data_type=col['DATA_TYPE'],
                length=col['CHARACTER_MAXIMUM_LENGTH'],
                precision=col['NUMERIC_PRECISION'],
                scale=col['NUMERIC_SCALE'],
                nullable=col['IS_NULLABLE'] == 'YES',
                default_value=col['COLUMN_DEFAULT'],
                comment=col['COMMENT'],
                is_primary_key=col['COLUMN_NAME'] in pk_set
            )
            table_metadata.columns.append(col_metadata)

        # Get foreign keys
        fk_query = f"""
            SELECT
                tc.CONSTRAINT_NAME,
                kcu.COLUMN_NAME,
                rc.UNIQUE_CONSTRAINT_NAME,
                kcu2.TABLE_NAME AS REFERENCED_TABLE,
                kcu2.COLUMN_NAME AS REFERENCED_COLUMN
            FROM {database}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN {database}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            JOIN {database}.INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
                ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
            JOIN {database}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu2
                ON rc.UNIQUE_CONSTRAINT_NAME = kcu2.CONSTRAINT_NAME
            WHERE tc.TABLE_SCHEMA = '{schema}'
            AND tc.TABLE_NAME = '{table_name}'
            AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
            ORDER BY tc.CONSTRAINT_NAME, kcu.ORDINAL_POSITION
        """
        fks = self.connector.execute_query(fk_query)

        # Group foreign keys by constraint name
        fk_dict = {}
        for fk in fks:
            constraint_name = fk['CONSTRAINT_NAME']
            if constraint_name not in fk_dict:
                fk_dict[constraint_name] = {
                    'columns': [],
                    'ref_table': fk['REFERENCED_TABLE'],
                    'ref_columns': []
                }
            fk_dict[constraint_name]['columns'].append(fk['COLUMN_NAME'])
            fk_dict[constraint_name]['ref_columns'].append(fk['REFERENCED_COLUMN'])

        for constraint_name, fk_info in fk_dict.items():
            fk_metadata = ConstraintMetadata(
                name=constraint_name,
                constraint_type='FOREIGN KEY',
                columns=fk_info['columns'],
                reference_table=fk_info['ref_table'],
                reference_columns=fk_info['ref_columns']
            )
            table_metadata.foreign_keys.append(fk_metadata)

        # Get table statistics
        stats_query = f"""
            SELECT ROW_COUNT, BYTES, CREATED, LAST_ALTERED, COMMENT
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
        """
        stats = self.connector.execute_query(stats_query)
        if stats:
            table_metadata.row_count = stats[0]['ROW_COUNT'] or 0
            table_metadata.table_size_bytes = stats[0]['BYTES'] or 0
            table_metadata.comment = stats[0]['COMMENT']
            if stats[0]['CREATED']:
                table_metadata.created_date = stats[0]['CREATED']
            if stats[0]['LAST_ALTERED']:
                table_metadata.last_modified_date = stats[0]['LAST_ALTERED']

        # Get clustering keys
        try:
            cluster_query = f"SHOW TABLES LIKE '{table_name}' IN {database}.{schema}"
            self.connector.execute_query(cluster_query)
            # Note: Snowflake's clustering key info requires parsing SHOW TABLES output
            # This is a simplified version
        except Exception as e:
            logger.debug(f"Could not retrieve clustering keys: {e}")

        return table_metadata

    def extract_sample_data(self, database: str, schema: str, table_name: str, sample_size: int = 100) -> None:
        """
        Extract sample data from a table and save to CSV.

        Args:
            database: Database name
            schema: Schema name
            table_name: Table name
            sample_size: Number of rows to sample
        """
        try:
            query = f'SELECT * FROM {database}.{schema}.{table_name} LIMIT {sample_size}'
            results = self.connector.execute_query(query)

            if results:
                # Convert to pandas DataFrame for easier CSV writing
                df = pd.DataFrame(results)

                # Save to CSV
                output_file = self.output_dir / f"snowflake_{database}_{schema}_{table_name}_sample.csv"
                df.to_csv(output_file, index=False)

                logger.debug(f"Sample data saved: {output_file}")

        except Exception as e:
            logger.warning(f"Could not extract sample data for {database}.{schema}.{table_name}: {e}")

    def profile_table_data(self, database: str, schema: str, table_name: str, table_metadata: TableMetadata) -> TableProfile:
        """
        Profile table data to get statistics.

        Args:
            database: Database name
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
                    FROM {database}.{schema}.{table_name}
                """

                stats = self.connector.execute_query(stats_query)

                if stats:
                    null_count = stats[0]['NULL_COUNT']
                    distinct_count = stats[0]['DISTINCT_COUNT']

                    col_profile = DataProfile(
                        column_name=column.name,
                        null_count=null_count,
                        null_percentage=(null_count / table_metadata.row_count * 100) if table_metadata.row_count > 0 else 0,
                        distinct_count=distinct_count
                    )

                    # Get min/max for numeric and date columns
                    if column.data_type in ('NUMBER', 'INTEGER', 'FLOAT', 'DATE', 'TIMESTAMP', 'TIMESTAMP_NTZ', 'TIMESTAMP_LTZ', 'TIMESTAMP_TZ'):
                        minmax_query = f"SELECT MIN({column.name}), MAX({column.name}), AVG({column.name}) FROM {database}.{schema}.{table_name}"
                        try:
                            minmax = self.connector.execute_query(minmax_query)
                            if minmax:
                                col_profile.min_value = str(minmax[0]['MIN(' + column.name + ')']) if minmax[0]['MIN(' + column.name + ')'] else None
                                col_profile.max_value = str(minmax[0]['MAX(' + column.name + ')']) if minmax[0]['MAX(' + column.name + ')'] else None
                                if 'AVG(' + column.name + ')' in minmax[0]:
                                    col_profile.avg_value = str(minmax[0]['AVG(' + column.name + ')'])
                        except:
                            pass

                    # Get sample values (top 5)
                    sample_query = f"SELECT DISTINCT {column.name} FROM {database}.{schema}.{table_name} WHERE {column.name} IS NOT NULL LIMIT 5"
                    samples = self.connector.execute_query(sample_query)
                    col_profile.sample_values = [str(list(s.values())[0]) for s in samples]

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
        output_file = self.output_dir / f"snowflake_{profile.schema}_{profile.table_name}_profile.json"
        import json
        with open(output_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2, default=str)

    def crawl_multiple_schemas(self, database: str, schema_names: List[str], sample_size: int = 100) -> List[SchemaMetadata]:
        """
        Crawl multiple schemas in a database.

        Args:
            database: Database name
            schema_names: List of schema names
            sample_size: Number of sample rows per table

        Returns:
            List of SchemaMetadata objects
        """
        schemas = []
        for schema_name in schema_names:
            try:
                schema_metadata = self.crawl_schema(database, schema_name, sample_size)
                schemas.append(schema_metadata)
            except Exception as e:
                logger.error(f"Failed to crawl schema {schema_name}: {e}")
                continue

        return schemas

    def list_databases(self) -> List[str]:
        """
        List all databases in Snowflake account.

        Returns:
            List of database names
        """
        query = "SHOW DATABASES"
        results = self.connector.execute_query(query)
        return [row['name'] for row in results]

    def list_schemas(self, database: str) -> List[str]:
        """
        List all schemas in a database.

        Args:
            database: Database name

        Returns:
            List of schema names
        """
        query = f"SHOW SCHEMAS IN DATABASE {database}"
        results = self.connector.execute_query(query)
        return [row['name'] for row in results]
