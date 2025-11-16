"""
Data validation for Oracle to Snowflake migration.
"""
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger
import pandas as pd

from ..utils.db_connector import OracleConnector, SnowflakeConnector
from ..crawlers.metadata_models import TableMetadata


class DataValidator:
    """Validate data during migration."""

    def __init__(self, oracle_connector: OracleConnector, snowflake_connector: SnowflakeConnector):
        """
        Initialize data validator.

        Args:
            oracle_connector: Oracle database connector
            snowflake_connector: Snowflake database connector
        """
        self.oracle_conn = oracle_connector
        self.snowflake_conn = snowflake_connector
        self.validation_results = []

    def validate_row_count(
        self,
        oracle_schema: str,
        oracle_table: str,
        snowflake_database: str,
        snowflake_schema: str,
        snowflake_table: str,
        tolerance_percent: float = 0.1
    ) -> Dict[str, Any]:
        """
        Validate row counts between Oracle and Snowflake.

        Args:
            oracle_schema: Oracle schema name
            oracle_table: Oracle table name
            snowflake_database: Snowflake database name
            snowflake_schema: Snowflake schema name
            snowflake_table: Snowflake table name
            tolerance_percent: Acceptable difference percentage (default: 0.1%)

        Returns:
            Validation result dictionary
        """
        logger.info(f"Validating row count: {oracle_schema}.{oracle_table} -> {snowflake_database}.{snowflake_schema}.{snowflake_table}")

        try:
            # Get Oracle row count
            oracle_query = f"SELECT COUNT(*) FROM {oracle_schema}.{oracle_table}"
            oracle_result = self.oracle_conn.execute_query(oracle_query)
            oracle_count = oracle_result[0][0] if oracle_result else 0

            # Get Snowflake row count
            snowflake_query = f"SELECT COUNT(*) FROM {snowflake_database}.{snowflake_schema}.{snowflake_table}"
            snowflake_result = self.snowflake_conn.execute_query(snowflake_query)
            snowflake_count = snowflake_result[0]['COUNT(*)'] if snowflake_result else 0

            # Calculate difference
            if oracle_count > 0:
                difference_percent = abs(snowflake_count - oracle_count) / oracle_count * 100
            else:
                difference_percent = 0 if snowflake_count == 0 else 100

            # Determine validation status
            status = 'PASSED' if difference_percent <= tolerance_percent else 'FAILED'

            result = {
                'validation_type': 'ROW_COUNT',
                'table': f"{oracle_schema}.{oracle_table}",
                'oracle_count': oracle_count,
                'snowflake_count': snowflake_count,
                'difference': abs(snowflake_count - oracle_count),
                'difference_percent': difference_percent,
                'tolerance_percent': tolerance_percent,
                'status': status
            }

            logger.info(f"Row count validation: {status} (Oracle: {oracle_count}, Snowflake: {snowflake_count}, Difference: {difference_percent:.2f}%)")
            self.validation_results.append(result)
            return result

        except Exception as e:
            logger.error(f"Error validating row count: {e}")
            result = {
                'validation_type': 'ROW_COUNT',
                'table': f"{oracle_schema}.{oracle_table}",
                'status': 'ERROR',
                'error_message': str(e)
            }
            self.validation_results.append(result)
            return result

    def validate_sample_data(
        self,
        oracle_schema: str,
        oracle_table: str,
        snowflake_database: str,
        snowflake_schema: str,
        snowflake_table: str,
        sample_size: int = 100,
        key_columns: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare sample data between Oracle and Snowflake.

        Args:
            oracle_schema: Oracle schema name
            oracle_table: Oracle table name
            snowflake_database: Snowflake database name
            snowflake_schema: Snowflake schema name
            snowflake_table: Snowflake table name
            sample_size: Number of rows to sample
            key_columns: Key columns to use for comparison

        Returns:
            Validation result dictionary
        """
        logger.info(f"Validating sample data: {oracle_schema}.{oracle_table}")

        try:
            # Get Oracle sample data
            oracle_query = f"SELECT * FROM {oracle_schema}.{oracle_table} WHERE ROWNUM <= {sample_size}"
            oracle_data = self.oracle_conn.execute_query(oracle_query)
            oracle_cols = [desc[0] for desc in self.oracle_conn.cursor.description]
            oracle_df = pd.DataFrame(oracle_data, columns=oracle_cols)

            # Get Snowflake sample data
            snowflake_query = f"SELECT * FROM {snowflake_database}.{snowflake_schema}.{snowflake_table} LIMIT {sample_size}"
            snowflake_data = self.snowflake_conn.execute_query(snowflake_query)
            snowflake_df = pd.DataFrame(snowflake_data)

            # Compare data
            matches = 0
            mismatches = 0
            column_mismatches = []

            # Check if both dataframes have data
            if len(oracle_df) == 0 and len(snowflake_df) == 0:
                status = 'PASSED'
                matches = 0
            elif len(oracle_df) != len(snowflake_df):
                status = 'FAILED'
                mismatches = abs(len(oracle_df) - len(snowflake_df))
            else:
                # Compare row by row
                for col in oracle_cols:
                    if col in snowflake_df.columns:
                        col_matches = (oracle_df[col] == snowflake_df[col]).sum()
                        matches += col_matches
                        if col_matches < len(oracle_df):
                            mismatches += len(oracle_df) - col_matches
                            column_mismatches.append(col)
                    else:
                        column_mismatches.append(f"{col} (missing)")
                        mismatches += len(oracle_df)

                status = 'PASSED' if len(column_mismatches) == 0 else 'FAILED'

            result = {
                'validation_type': 'SAMPLE_DATA',
                'table': f"{oracle_schema}.{oracle_table}",
                'sample_size': min(len(oracle_df), len(snowflake_df)),
                'oracle_rows': len(oracle_df),
                'snowflake_rows': len(snowflake_df),
                'matching_rows': matches,
                'mismatched_rows': mismatches,
                'column_mismatches': column_mismatches,
                'status': status
            }

            logger.info(f"Sample data validation: {status}")
            self.validation_results.append(result)
            return result

        except Exception as e:
            logger.error(f"Error validating sample data: {e}")
            result = {
                'validation_type': 'SAMPLE_DATA',
                'table': f"{oracle_schema}.{oracle_table}",
                'status': 'ERROR',
                'error_message': str(e)
            }
            self.validation_results.append(result)
            return result

    def validate_null_values(
        self,
        oracle_schema: str,
        oracle_table: str,
        snowflake_database: str,
        snowflake_schema: str,
        snowflake_table: str,
        column_name: str,
        tolerance_percent: float = 5.0
    ) -> Dict[str, Any]:
        """
        Validate NULL value counts in a column.

        Args:
            oracle_schema: Oracle schema name
            oracle_table: Oracle table name
            snowflake_database: Snowflake database name
            snowflake_schema: Snowflake schema name
            snowflake_table: Snowflake table name
            column_name: Column to check
            tolerance_percent: Acceptable difference percentage

        Returns:
            Validation result dictionary
        """
        logger.info(f"Validating NULL values for {column_name}")

        try:
            # Get Oracle NULL count
            oracle_query = f"SELECT COUNT(*) - COUNT({column_name}) FROM {oracle_schema}.{oracle_table}"
            oracle_result = self.oracle_conn.execute_query(oracle_query)
            oracle_nulls = oracle_result[0][0] if oracle_result else 0

            # Get Snowflake NULL count
            snowflake_query = f"SELECT COUNT(*) - COUNT({column_name}) FROM {snowflake_database}.{snowflake_schema}.{snowflake_table}"
            snowflake_result = self.snowflake_conn.execute_query(snowflake_query)
            snowflake_nulls = snowflake_result[0].get('COUNT(*) - COUNT(' + column_name + ')') if snowflake_result else 0

            # Calculate difference
            if oracle_nulls > 0:
                difference_percent = abs(snowflake_nulls - oracle_nulls) / oracle_nulls * 100
            else:
                difference_percent = 0 if snowflake_nulls == 0 else 100

            status = 'PASSED' if difference_percent <= tolerance_percent else 'FAILED'

            result = {
                'validation_type': 'NULL_VALUES',
                'table': f"{oracle_schema}.{oracle_table}",
                'column': column_name,
                'oracle_nulls': oracle_nulls,
                'snowflake_nulls': snowflake_nulls,
                'difference': abs(snowflake_nulls - oracle_nulls),
                'difference_percent': difference_percent,
                'status': status
            }

            logger.info(f"NULL validation: {status} (Oracle: {oracle_nulls}, Snowflake: {snowflake_nulls})")
            self.validation_results.append(result)
            return result

        except Exception as e:
            logger.error(f"Error validating NULL values: {e}")
            result = {
                'validation_type': 'NULL_VALUES',
                'table': f"{oracle_schema}.{oracle_table}",
                'column': column_name,
                'status': 'ERROR',
                'error_message': str(e)
            }
            self.validation_results.append(result)
            return result

    def validate_distinct_values(
        self,
        oracle_schema: str,
        oracle_table: str,
        snowflake_database: str,
        snowflake_schema: str,
        snowflake_table: str,
        column_name: str,
        tolerance_percent: float = 5.0
    ) -> Dict[str, Any]:
        """
        Validate distinct value counts in a column.

        Args:
            oracle_schema: Oracle schema name
            oracle_table: Oracle table name
            snowflake_database: Snowflake database name
            snowflake_schema: Snowflake schema name
            snowflake_table: Snowflake table name
            column_name: Column to check
            tolerance_percent: Acceptable difference percentage

        Returns:
            Validation result dictionary
        """
        logger.info(f"Validating distinct values for {column_name}")

        try:
            # Get Oracle distinct count
            oracle_query = f"SELECT COUNT(DISTINCT {column_name}) FROM {oracle_schema}.{oracle_table}"
            oracle_result = self.oracle_conn.execute_query(oracle_query)
            oracle_distinct = oracle_result[0][0] if oracle_result else 0

            # Get Snowflake distinct count
            snowflake_query = f"SELECT COUNT(DISTINCT {column_name}) FROM {snowflake_database}.{snowflake_schema}.{snowflake_table}"
            snowflake_result = self.snowflake_conn.execute_query(snowflake_query)
            snowflake_distinct = snowflake_result[0].get('COUNT(DISTINCT ' + column_name + ')') if snowflake_result else 0

            # Calculate difference
            if oracle_distinct > 0:
                difference_percent = abs(snowflake_distinct - oracle_distinct) / oracle_distinct * 100
            else:
                difference_percent = 0 if snowflake_distinct == 0 else 100

            status = 'PASSED' if difference_percent <= tolerance_percent else 'FAILED'

            result = {
                'validation_type': 'DISTINCT_VALUES',
                'table': f"{oracle_schema}.{oracle_table}",
                'column': column_name,
                'oracle_distinct': oracle_distinct,
                'snowflake_distinct': snowflake_distinct,
                'difference': abs(snowflake_distinct - oracle_distinct),
                'difference_percent': difference_percent,
                'status': status
            }

            logger.info(f"Distinct validation: {status}")
            self.validation_results.append(result)
            return result

        except Exception as e:
            logger.error(f"Error validating distinct values: {e}")
            result = {
                'validation_type': 'DISTINCT_VALUES',
                'table': f"{oracle_schema}.{oracle_table}",
                'column': column_name,
                'status': 'ERROR',
                'error_message': str(e)
            }
            self.validation_results.append(result)
            return result

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of all validations.

        Returns:
            Summary dictionary
        """
        total = len(self.validation_results)
        passed = sum(1 for r in self.validation_results if r.get('status') == 'PASSED')
        failed = sum(1 for r in self.validation_results if r.get('status') == 'FAILED')
        errors = sum(1 for r in self.validation_results if r.get('status') == 'ERROR')

        return {
            'total_validations': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'validation_results': self.validation_results
        }
