"""
Unit tests for SQL translation.
"""
import pytest
from generators.sql_translator import SQLTranslator


class TestSQLTranslator:
    """Test SQLTranslator class."""

    @pytest.fixture
    def translator(self):
        """Create SQLTranslator instance."""
        return SQLTranslator()

    def test_translate_iif_to_case(self, translator):
        """Test IIF to CASE conversion."""
        expr = "IIF(SALARY > 50000, 'HIGH', 'LOW')"
        result = translator.translate_expression(expr)

        assert "CASE" in result
        assert "WHEN" in result
        assert "THEN" in result

    def test_translate_isnull(self, translator):
        """Test ISNULL translation."""
        expr = "ISNULL(SALARY, 0) * 1.10"
        result = translator.translate_expression(expr)

        assert "COALESCE" in result
        assert "ISNULL" not in result

    def test_translate_string_functions(self, translator):
        """Test string function translation."""
        expr = "UPPER(TRIM(NAME))"
        result = translator.translate_expression(expr)

        assert "UPPER" in result
        assert "TRIM" in result

    def test_translate_substr(self, translator):
        """Test SUBSTR to SUBSTRING conversion."""
        expr = "SUBSTR(NAME, 1, 10)"
        result = translator.translate_expression(expr)

        assert "SUBSTRING" in result
        assert "SUBSTR" not in result

    def test_translate_date_functions(self, translator):
        """Test date function translation."""
        expr = "TRUNC(SYSDATE)"
        result = translator.translate_expression(expr)

        assert "DATE_TRUNC" in result
        assert "CURRENT_DATE" in result

    def test_translate_round_function(self, translator):
        """Test ROUND function translation."""
        expr = "ROUND(AMOUNT, 2)"
        result = translator.translate_expression(expr)

        assert "ROUND" in result
        assert result.count("ROUND") == 1

    def test_translate_filter_condition(self, translator):
        """Test filter condition translation."""
        condition = "DEPARTMENT = 'SALES' AND SALARY > 50000"
        result = translator.translate_filter_condition(condition)

        assert "DEPARTMENT" in result
        assert "SALARY" in result

    def test_translate_aggregation_sum(self, translator):
        """Test SUM aggregation translation."""
        result = translator.translate_aggregation('SUM', 'SALARY')
        assert result == "SUM(SALARY)"

    def test_translate_aggregation_count(self, translator):
        """Test COUNT aggregation translation."""
        result = translator.translate_aggregation('COUNT', '*')
        assert result == "COUNT(*)"

    def test_translate_join(self, translator):
        """Test JOIN translation."""
        result = translator.translate_join(
            'LEFT',
            'CUSTOMERS',
            'ORDERS',
            [('CUST_ID', 'CUSTOMER_ID')]
        )

        assert "LEFT JOIN" in result
        assert "CUSTOMERS" in result
        assert "ORDERS" in result

    def test_translate_lookup(self, translator):
        """Test LOOKUP to JOIN translation."""
        result = translator.translate_lookup(
            'DIM_PRODUCT',
            'PRODUCT_ID',
            'PRODUCT_ID',
            ['PRODUCT_NAME', 'CATEGORY']
        )

        assert "LEFT JOIN" in result
        assert "DIM_PRODUCT" in result

    def test_translate_router(self, translator):
        """Test ROUTER to CASE translation."""
        routes = {
            "SALARY > 100000": "HIGH",
            "SALARY > 50000": "MEDIUM",
            "SALARY <= 50000": "LOW"
        }

        result = translator.translate_router(routes)

        assert "CASE" in result
        assert "WHEN" in result
        assert "THEN" in result

    def test_translate_sorter(self, translator):
        """Test SORTER translation."""
        sort_cols = [('DEPARTMENT', 'ASC'), ('SALARY', 'DESC')]
        result = translator.translate_sorter(sort_cols)

        assert "ORDER BY" in result
        assert "DEPARTMENT" in result
        assert "SALARY" in result
        assert "ASC" in result
        assert "DESC" in result

    def test_translate_rank_function(self, translator):
        """Test window function translation."""
        result = translator.translate_rank_function(
            'ROW_NUMBER',
            ['SALARY DESC'],
            ['DEPARTMENT']
        )

        assert "ROW_NUMBER()" in result
        assert "PARTITION BY" in result
        assert "ORDER BY" in result

    def test_translate_union(self, translator):
        """Test UNION translation."""
        result = translator.translate_union(all_rows=True)
        assert result == "UNION ALL"

        result = translator.translate_union(all_rows=False)
        assert result == "UNION"

    def test_validate_snowflake_syntax(self, translator):
        """Test Snowflake SQL validation."""
        # Valid SQL
        is_valid, errors = translator.validate_snowflake_syntax(
            "SELECT UPPER(NAME) FROM CUSTOMERS WHERE ID = 1"
        )
        assert is_valid
        assert len(errors) == 0

        # Invalid SQL - unclosed parenthesis
        is_valid, errors = translator.validate_snowflake_syntax(
            "SELECT UPPER(NAME FROM CUSTOMERS"
        )
        assert not is_valid
        assert len(errors) > 0

    def test_conversion_log(self, translator):
        """Test conversion logging."""
        translator.translate_expression("IIF(X > 0, 1, 0)")
        translator.translate_expression("ISNULL(Y, 'N/A')")

        log = translator.get_conversion_log()
        assert len(log) == 2
        assert log[0]['original'] == "IIF(X > 0, 1, 0)"

    def test_complex_expression_translation(self, translator):
        """Test complex expression translation."""
        expr = "CASE WHEN IIF(ISNULL(SALARY, 0) > 50000, 'HIGH', 'LOW') = 'HIGH' THEN ROUND(SALARY * 1.10, 2) ELSE SALARY END"
        result = translator.translate_expression(expr)

        # Should not contain Informatica functions
        assert "IIF" not in result
        assert "ISNULL" not in result or "IS NULL" in result


class TestSQLTranslatorIntegration:
    """Integration tests for SQL translation."""

    def test_full_transformation_translation(self):
        """Test translating a complete transformation."""
        translator = SQLTranslator()

        # Simulate Informatica Expression transformation
        expressions = {
            'CUSTOMER_ID': 'CUST_ID',
            'FULL_NAME': "UPPER(CONCAT(FIRST_NAME, ' ', LAST_NAME))",
            'ANNUAL_SALARY': 'ROUND(SALARY * 12, 2)',
            'SALARY_CATEGORY': "IIF(SALARY > 75000, 'HIGH', 'LOW')",
            'LOAD_DATE': 'SYSDATE',
            'PHONE_NUMBER': 'COALESCE(MOBILE_PHONE, HOME_PHONE)'
        }

        translated = {}
        for col, expr in expressions.items():
            translated[col] = translator.translate_expression(expr, col)

        # Verify all expressions were translated
        assert len(translated) == 6
        assert all(v is not None for v in translated.values())

        # Verify no Informatica functions remain
        result_str = str(translated)
        assert 'IIF' not in result_str
        assert 'SYSDATE' not in result_str
