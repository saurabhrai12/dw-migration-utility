"""
SQL translator for converting Informatica transformations to Snowflake SQL.
"""
import re
from typing import Dict, List, Tuple, Optional, Any
from loguru import logger


class SQLTranslator:
    """Translate Informatica expressions and transformations to Snowflake SQL."""

    # Informatica to Snowflake function mapping
    FUNCTION_MAPPING = {
        # NULL handling
        'ISNULL': 'COALESCE',
        'IIF': 'CASE WHEN',
        'DECODE': 'CASE',

        # String functions
        'UPPER': 'UPPER',
        'LOWER': 'LOWER',
        'SUBSTR': 'SUBSTRING',
        'INSTR': 'POSITION',
        'LENGTH': 'LENGTH',
        'LTRIM': 'LTRIM',
        'RTRIM': 'RTRIM',
        'TRIM': 'TRIM',
        'CONCAT': 'CONCAT',
        'LPAD': 'LPAD',
        'RPAD': 'RPAD',
        'REPLACE': 'REPLACE',

        # Numeric functions
        'ABS': 'ABS',
        'ROUND': 'ROUND',
        'TRUNC': 'TRUNC',
        'CEIL': 'CEIL',
        'FLOOR': 'FLOOR',
        'SQRT': 'SQRT',
        'POWER': 'POWER',
        'MOD': 'MOD',

        # Date functions
        'TRUNC': 'DATE_TRUNC',
        'ADD_MONTHS': 'DATE_ADD',
        'SYSDATE': 'CURRENT_DATE',
        'SYSTIMESTAMP': 'CURRENT_TIMESTAMP',
        'TO_DATE': 'TO_DATE',
        'TO_CHAR': 'TO_VARCHAR',

        # Aggregate functions
        'SUM': 'SUM',
        'COUNT': 'COUNT',
        'AVG': 'AVG',
        'MIN': 'MIN',
        'MAX': 'MAX',
        'STDDEV': 'STDDEV_POP',
        'VARIANCE': 'VAR_POP',
    }

    def __init__(self):
        """Initialize SQL translator."""
        self.conversion_log = []

    def translate_expression(self, informatica_expr: str, column_name: str = None) -> str:
        """
        Translate Informatica expression to Snowflake SQL.

        Args:
            informatica_expr: Informatica expression string
            column_name: Optional column name for context

        Returns:
            Snowflake SQL expression
        """
        if not informatica_expr:
            return None

        logger.debug(f"Translating expression: {informatica_expr}")

        snowflake_expr = informatica_expr

        # Handle ISNULL pattern: ISNULL(SALARY)
        snowflake_expr = re.sub(
            r'ISNULL\s*\(\s*(\w+)\s*\)',
            r'\1 IS NULL',
            snowflake_expr,
            flags=re.IGNORECASE
        )

        # Handle IIF pattern: IIF(condition, true_value, false_value)
        snowflake_expr = self._convert_iif_to_case(snowflake_expr)

        # Handle NULL coalescing: ISNULL(col, 0) -> COALESCE(col, 0)
        snowflake_expr = re.sub(
            r'ISNULL\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)',
            r'COALESCE(\1, \2)',
            snowflake_expr,
            flags=re.IGNORECASE
        )

        # Replace common Informatica functions
        for informatica_func, snowflake_func in self.FUNCTION_MAPPING.items():
            # Case-insensitive function replacement
            pattern = r'\b' + informatica_func + r'\s*\('
            snowflake_expr = re.sub(
                pattern,
                snowflake_func + '(',
                snowflake_expr,
                flags=re.IGNORECASE
            )

        # Handle date format conversions
        snowflake_expr = self._convert_date_formats(snowflake_expr)

        # Handle numeric conversions
        snowflake_expr = self._convert_numeric_types(snowflake_expr)

        # Handle string conversions
        snowflake_expr = self._convert_string_types(snowflake_expr)

        # Clean up multiple spaces
        snowflake_expr = ' '.join(snowflake_expr.split())

        logger.debug(f"Translated to: {snowflake_expr}")
        self.conversion_log.append({
            'original': informatica_expr,
            'translated': snowflake_expr,
            'column': column_name
        })

        return snowflake_expr

    def _convert_iif_to_case(self, expr: str) -> str:
        """Convert IIF statements to CASE statements."""
        # Pattern: IIF(condition, true_value, false_value)
        pattern = r'IIF\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'

        def replace_iif(match):
            condition = match.group(1)
            true_val = match.group(2)
            false_val = match.group(3)
            return f"CASE WHEN {condition} THEN {true_val} ELSE {false_val} END"

        return re.sub(pattern, replace_iif, expr, flags=re.IGNORECASE)

    def _convert_date_formats(self, expr: str) -> str:
        """Convert Informatica date format strings to Snowflake."""
        # Convert TO_DATE patterns
        expr = re.sub(
            r"TO_DATE\s*\(\s*([^,]+)\s*,\s*'([^']+)'\s*\)",
            r"TO_DATE(\1, '\2')",
            expr,
            flags=re.IGNORECASE
        )

        # Convert TRUNC(date) to DATE_TRUNC
        expr = re.sub(
            r"TRUNC\s*\(\s*(\w+)\s*\)",
            r"DATE_TRUNC('DAY', \1)",
            expr,
            flags=re.IGNORECASE
        )

        return expr

    def _convert_numeric_types(self, expr: str) -> str:
        """Convert Informatica numeric operations to Snowflake."""
        # Convert ROUND(value, decimals)
        expr = re.sub(
            r"ROUND\s*\(\s*([^,]+)\s*,\s*(\d+)\s*\)",
            r"ROUND(\1, \2)",
            expr,
            flags=re.IGNORECASE
        )

        # Handle multiplication with implicit conversion
        expr = re.sub(
            r"(\w+)\s*\*\s*([\d.]+)",
            r"(\1 * \2)",
            expr
        )

        return expr

    def _convert_string_types(self, expr: str) -> str:
        """Convert Informatica string operations to Snowflake."""
        # Convert SUBSTR to SUBSTRING
        expr = re.sub(
            r"SUBSTR\s*\(",
            r"SUBSTRING(",
            expr,
            flags=re.IGNORECASE
        )

        # Handle string concatenation
        expr = re.sub(
            r"(\w+)\s*\|\|\s*(\w+)",
            r"\1 || \2",
            expr
        )

        return expr

    def translate_filter_condition(self, condition: str) -> str:
        """
        Translate Informatica filter condition to SQL WHERE clause.

        Args:
            condition: Filter condition

        Returns:
            WHERE clause condition
        """
        return self.translate_expression(condition)

    def translate_aggregation(self, agg_type: str, column: str, group_by: List[str] = None) -> str:
        """
        Translate Informatica aggregation to SQL.

        Args:
            agg_type: Aggregation type (SUM, COUNT, AVG, etc.)
            column: Column to aggregate
            group_by: List of columns to group by

        Returns:
            Aggregation SQL
        """
        agg_upper = agg_type.upper()

        if agg_upper not in ['SUM', 'COUNT', 'AVG', 'MIN', 'MAX', 'STDDEV', 'VARIANCE']:
            logger.warning(f"Unknown aggregation type: {agg_type}")
            return None

        # Map to Snowflake equivalent
        sf_agg = self.FUNCTION_MAPPING.get(agg_upper, agg_upper)

        if agg_upper == 'COUNT' and column == '*':
            sql = f"COUNT(*)"
        else:
            sql = f"{sf_agg}({column})"

        return sql

    def translate_join(
        self,
        join_type: str,
        left_table: str,
        right_table: str,
        join_conditions: List[Tuple[str, str]]
    ) -> str:
        """
        Translate Informatica join to SQL.

        Args:
            join_type: Type of join (INNER, LEFT, RIGHT, FULL)
            left_table: Left table name
            right_table: Right table name
            join_conditions: List of (left_column, right_column) tuples

        Returns:
            JOIN SQL clause
        """
        join_type_upper = join_type.upper()

        if join_type_upper not in ['INNER', 'LEFT', 'RIGHT', 'FULL']:
            join_type_upper = 'INNER'

        # Build join condition
        join_on_parts = [f"lt.{lc} = rt.{rc}" for lc, rc in join_conditions]
        join_on = " AND ".join(join_on_parts)

        sql = f"""
{join_type_upper} JOIN {right_table} rt
ON {join_on}
        """.strip()

        return sql

    def translate_lookup(
        self,
        lookup_table: str,
        lookup_column: str,
        source_column: str,
        return_columns: List[str]
    ) -> str:
        """
        Translate Informatica lookup to SQL (LEFT JOIN).

        Args:
            lookup_table: Lookup table name
            lookup_column: Column to join on in lookup table
            source_column: Source column to match
            return_columns: Columns to return from lookup

        Returns:
            LEFT JOIN SQL
        """
        return_cols_str = ", ".join([f"lk.{col}" for col in return_columns])

        sql = f"""
LEFT JOIN {lookup_table} lk
ON src.{source_column} = lk.{lookup_column}
        """.strip()

        return sql

    def translate_router(self, routes: Dict[str, str]) -> str:
        """
        Translate Informatica router to SQL CASE.

        Args:
            routes: Dictionary of condition -> target_group

        Returns:
            Router group assignment SQL
        """
        case_parts = []

        for condition, group in routes.items():
            case_parts.append(f"WHEN {condition} THEN '{group}'")

        case_sql = "CASE\n    " + "\n    ".join(case_parts) + "\n    ELSE 'OTHER'\nEND"

        return case_sql

    def translate_sorter(self, sort_columns: List[Tuple[str, str]]) -> str:
        """
        Translate Informatica sorter to SQL ORDER BY.

        Args:
            sort_columns: List of (column_name, direction) tuples

        Returns:
            ORDER BY clause
        """
        order_by_parts = []

        for col, direction in sort_columns:
            direction_upper = direction.upper() if direction else 'ASC'
            order_by_parts.append(f"{col} {direction_upper}")

        return "ORDER BY " + ", ".join(order_by_parts)

    def translate_rank_function(
        self,
        rank_type: str,
        order_by: List[str],
        partition_by: List[str] = None
    ) -> str:
        """
        Translate Informatica rank function to Snowflake window function.

        Args:
            rank_type: Type of rank (ROW_NUMBER, RANK, DENSE_RANK)
            order_by: Columns to order by
            partition_by: Columns to partition by

        Returns:
            Window function SQL
        """
        rank_upper = rank_type.upper()

        if rank_upper not in ['ROW_NUMBER', 'RANK', 'DENSE_RANK']:
            rank_upper = 'ROW_NUMBER'

        order_by_str = ", ".join(order_by)

        if partition_by:
            partition_by_str = ", ".join(partition_by)
            sql = f"{rank_upper}() OVER (PARTITION BY {partition_by_str} ORDER BY {order_by_str})"
        else:
            sql = f"{rank_upper}() OVER (ORDER BY {order_by_str})"

        return sql

    def translate_union(self, all_rows: bool = False) -> str:
        """
        Translate Informatica union to SQL.

        Args:
            all_rows: Whether to use UNION ALL

        Returns:
            UNION clause
        """
        return "UNION ALL" if all_rows else "UNION"

    def translate_update_strategy(
        self,
        insert_sql: str,
        update_sql: str,
        delete_sql: str = None
    ) -> str:
        """
        Translate Informatica update strategy to MERGE statement.

        Args:
            insert_sql: INSERT logic
            update_sql: UPDATE logic
            delete_sql: Optional DELETE logic

        Returns:
            MERGE statement
        """
        merge_sql = f"""
MERGE INTO target_table tgt
USING source_query src
ON tgt.key_column = src.key_column
WHEN MATCHED THEN
    UPDATE SET
        {update_sql}
WHEN NOT MATCHED THEN
    INSERT (columns)
    VALUES (values)
        """.strip()

        if delete_sql:
            merge_sql += f"\nWHEN MATCHED AND {delete_sql} THEN DELETE"

        return merge_sql

    def get_conversion_log(self) -> List[Dict]:
        """Get log of all conversions performed."""
        return self.conversion_log

    def clear_conversion_log(self) -> None:
        """Clear conversion log."""
        self.conversion_log = []

    def validate_snowflake_syntax(self, sql: str) -> Tuple[bool, List[str]]:
        """
        Validate Snowflake SQL syntax (basic validation).

        Args:
            sql: SQL statement to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check for unclosed parentheses
        if sql.count('(') != sql.count(')'):
            errors.append("Unclosed parentheses detected")

        # Check for unclosed quotes
        single_quotes = sql.count("'") - sql.count("\\'")
        if single_quotes % 2 != 0:
            errors.append("Unclosed single quotes detected")

        # Check for common Informatica functions that weren't converted
        unconverted_functions = ['IIF(', 'ISNULL(', 'DECODE(']
        for func in unconverted_functions:
            if func in sql.upper():
                errors.append(f"Unconverted Informatica function detected: {func}")

        return len(errors) == 0, errors

    def translate_transformation_logic(self, transformation: Any) -> Dict[str, str]:
        """
        Translate complete transformation logic from Informatica object.

        Args:
            transformation: Informatica Transformation object

        Returns:
            Dictionary with translated logic
        """
        result = {
            'name': transformation.name,
            'type': transformation.type,
            'translated_expressions': {},
            'errors': []
        }

        try:
            # Translate all port expressions
            for port in transformation.ports:
                if port.get('expression'):
                    translated = self.translate_expression(
                        port['expression'],
                        port['name']
                    )
                    result['translated_expressions'][port['name']] = {
                        'original': port['expression'],
                        'translated': translated
                    }

        except Exception as e:
            result['errors'].append(str(e))
            logger.error(f"Error translating transformation {transformation.name}: {e}")

        return result
