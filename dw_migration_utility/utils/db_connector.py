"""
Database connector utility for Oracle and Snowflake databases.
"""
from typing import Any, Dict, List, Optional
import cx_Oracle
import snowflake.connector
from snowflake.connector import DictCursor
from loguru import logger


class OracleConnector:
    """Oracle database connector."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Oracle connector.

        Args:
            config: Oracle connection configuration
        """
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Establish connection to Oracle database."""
        try:
            dsn = cx_Oracle.makedsn(
                self.config['host'],
                self.config['port'],
                service_name=self.config['service_name']
            )

            self.connection = cx_Oracle.connect(
                user=self.config['username'],
                password=self.config['password'],
                dsn=dsn,
                encoding="UTF-8"
            )

            self.cursor = self.connection.cursor()
            logger.info("Successfully connected to Oracle database")

        except cx_Oracle.Error as e:
            logger.error(f"Failed to connect to Oracle: {e}")
            raise

    def disconnect(self) -> None:
        """Close Oracle database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from Oracle database")

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[tuple]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            List of result rows
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            return self.cursor.fetchall()

        except cx_Oracle.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def get_table_metadata(self, schema: str, table_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific table.

        Args:
            schema: Schema name
            table_name: Table name

        Returns:
            Table metadata dictionary
        """
        metadata = {
            'schema': schema,
            'table_name': table_name,
            'columns': [],
            'primary_keys': [],
            'foreign_keys': [],
            'indexes': [],
            'constraints': [],
            'row_count': 0,
            'comments': None
        }

        # Get column information
        column_query = """
            SELECT
                COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION,
                DATA_SCALE, NULLABLE, DATA_DEFAULT
            FROM ALL_TAB_COLUMNS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
            ORDER BY COLUMN_ID
        """
        columns = self.execute_query(column_query, {'schema': schema, 'table_name': table_name})

        for col in columns:
            metadata['columns'].append({
                'name': col[0],
                'data_type': col[1],
                'length': col[2],
                'precision': col[3],
                'scale': col[4],
                'nullable': col[5] == 'Y',
                'default': col[6]
            })

        # Get primary keys
        pk_query = """
            SELECT COLUMN_NAME
            FROM ALL_CONS_COLUMNS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
            AND CONSTRAINT_NAME IN (
                SELECT CONSTRAINT_NAME FROM ALL_CONSTRAINTS
                WHERE OWNER = :schema AND TABLE_NAME = :table_name
                AND CONSTRAINT_TYPE = 'P'
            )
            ORDER BY POSITION
        """
        pks = self.execute_query(pk_query, {'schema': schema, 'table_name': table_name})
        metadata['primary_keys'] = [pk[0] for pk in pks]

        # Get row count
        count_query = f'SELECT COUNT(*) FROM {schema}.{table_name}'
        try:
            count_result = self.execute_query(count_query)
            metadata['row_count'] = count_result[0][0] if count_result else 0
        except:
            logger.warning(f"Could not get row count for {schema}.{table_name}")
            metadata['row_count'] = 0

        # Get table comments
        comment_query = """
            SELECT COMMENTS
            FROM ALL_TAB_COMMENTS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
        """
        comments = self.execute_query(comment_query, {'schema': schema, 'table_name': table_name})
        metadata['comments'] = comments[0][0] if comments and comments[0][0] else None

        return metadata

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class SnowflakeConnector:
    """Snowflake database connector."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Snowflake connector.

        Args:
            config: Snowflake connection configuration
        """
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Establish connection to Snowflake database."""
        try:
            self.connection = snowflake.connector.connect(
                user=self.config['username'],
                password=self.config['password'],
                account=self.config['account'],
                warehouse=self.config.get('warehouse'),
                database=self.config.get('database'),
                schema=self.config.get('schema'),
                role=self.config.get('role')
            )

            self.cursor = self.connection.cursor(DictCursor)
            logger.info("Successfully connected to Snowflake")

        except snowflake.connector.Error as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise

    def disconnect(self) -> None:
        """Close Snowflake database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from Snowflake")

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            return self.cursor.fetchall()

        except snowflake.connector.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def get_table_metadata(self, database: str, schema: str, table_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific table.

        Args:
            database: Database name
            schema: Schema name
            table_name: Table name

        Returns:
            Table metadata dictionary
        """
        metadata = {
            'database': database,
            'schema': schema,
            'table_name': table_name,
            'columns': [],
            'primary_keys': [],
            'clustering_keys': [],
            'row_count': 0,
            'bytes': 0,
            'comments': None
        }

        # Get column information
        column_query = f"""
            SELECT
                COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION, NUMERIC_SCALE, IS_NULLABLE, COLUMN_DEFAULT,
                COMMENT
            FROM {database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """
        columns = self.execute_query(column_query)

        for col in columns:
            metadata['columns'].append({
                'name': col['COLUMN_NAME'],
                'data_type': col['DATA_TYPE'],
                'length': col['CHARACTER_MAXIMUM_LENGTH'],
                'precision': col['NUMERIC_PRECISION'],
                'scale': col['NUMERIC_SCALE'],
                'nullable': col['IS_NULLABLE'] == 'YES',
                'default': col['COLUMN_DEFAULT'],
                'comment': col['COMMENT']
            })

        # Get primary keys
        pk_query = f"""
            SELECT COLUMN_NAME
            FROM {database}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN {database}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            WHERE tc.TABLE_SCHEMA = '{schema}'
            AND tc.TABLE_NAME = '{table_name}'
            AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
            ORDER BY kcu.ORDINAL_POSITION
        """
        pks = self.execute_query(pk_query)
        metadata['primary_keys'] = [pk['COLUMN_NAME'] for pk in pks]

        # Get table statistics
        stats_query = f"""
            SELECT ROW_COUNT, BYTES
            FROM {database}.INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
        """
        stats = self.execute_query(stats_query)
        if stats:
            metadata['row_count'] = stats[0]['ROW_COUNT'] or 0
            metadata['bytes'] = stats[0]['BYTES'] or 0

        return metadata

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
