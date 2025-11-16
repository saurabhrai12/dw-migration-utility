"""
Unit tests for fuzzy matching algorithms.
"""
import pytest
from mappers.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher:
    """Test FuzzyMatcher class."""

    @pytest.fixture
    def matcher(self):
        """Create FuzzyMatcher instance."""
        return FuzzyMatcher(threshold=0.85)

    def test_exact_match(self, matcher):
        """Test exact name matching."""
        source = "CUSTOMER"
        targets = ["CUSTOMER", "ORDER", "PRODUCT"]

        result = matcher.find_best_match(source, targets, use_normalization=False)
        assert result is not None
        assert result[0] == "CUSTOMER"
        assert result[2] == "exact"

    def test_fuzzy_match(self, matcher):
        """Test fuzzy string matching."""
        source = "CUSTOMER"
        targets = ["CUSTMER", "ORDER", "PRODUCT"]  # Typo in CUSTOMER

        result = matcher.find_best_match(source, targets, use_normalization=False)
        assert result is not None
        assert result[0] == "CUSTMER"
        assert result[1] >= 0.85  # Should have high score

    def test_normalized_match(self, matcher):
        """Test normalized matching with prefixes."""
        source = "STG_CUSTOMER"
        targets = ["CUSTOMER", "PRODUCT"]

        result = matcher.find_best_match(source, targets, use_normalization=True)
        assert result is not None
        assert result[0] == "CUSTOMER"

    def test_no_match(self, matcher):
        """Test when no match is found."""
        source = "XYZ_TABLE"
        targets = ["CUSTOMER", "ORDER", "PRODUCT"]

        result = matcher.find_best_match(source, targets)
        assert result is None

    def test_normalize_name(self, matcher):
        """Test name normalization."""
        # Test prefix removal
        normalized = matcher.normalize_name("STG_CUSTOMER")
        assert "STG_" not in normalized
        assert "CUSTOMER" in normalized

        # Test suffix removal
        normalized = matcher.normalize_name("CUSTOMER_BACKUP")
        assert "_BACKUP" not in normalized
        assert "CUSTOMER" in normalized

    def test_tokenize(self, matcher):
        """Test tokenization."""
        tokens = matcher._tokenize("CUSTOMER_ORDER")
        assert len(tokens) > 0
        assert all(t.isupper() for t in tokens)

    def test_token_similarity(self, matcher):
        """Test token-based similarity matching."""
        source = "CUST_ORDER"
        targets = ["CUSTOMER_ORDER", "ORDER_CUST"]

        result = matcher.match_by_token_similarity(source, targets)
        assert result is not None
        assert result[1] >= (matcher.threshold / 100.0)

    def test_column_metadata_matching(self, matcher):
        """Test column matching by metadata."""
        source_cols = [
            {'name': 'ID', 'data_type': 'NUMBER'},
            {'name': 'NAME', 'data_type': 'VARCHAR2'},
        ]
        target_cols = [
            {'name': 'ID', 'data_type': 'DECIMAL'},
            {'name': 'NAME', 'data_type': 'VARCHAR'},
        ]

        mappings = matcher.match_columns_by_metadata(source_cols, target_cols)
        assert 'ID' in mappings
        assert 'NAME' in mappings

    def test_type_compatibility(self, matcher):
        """Test data type compatibility checking."""
        # Numeric types
        assert matcher._types_compatible('NUMBER', 'DECIMAL')
        assert matcher._types_compatible('INTEGER', 'INT')

        # String types
        assert matcher._types_compatible('VARCHAR2', 'VARCHAR')
        assert matcher._types_compatible('CHAR', 'CHAR')

        # Date types
        assert matcher._types_compatible('DATE', 'TIMESTAMP')

        # Incompatible types
        assert not matcher._types_compatible('NUMBER', 'VARCHAR')

    def test_table_similarity(self, matcher):
        """Test overall table similarity calculation."""
        source_table = {
            'table_name': 'STG_CUSTOMER',
            'columns': [
                {'name': 'CUST_ID', 'data_type': 'NUMBER'},
                {'name': 'CUST_NAME', 'data_type': 'VARCHAR2'},
            ],
            'primary_keys': ['CUST_ID']
        }

        target_table = {
            'table_name': 'CUSTOMER',
            'columns': [
                {'name': 'ID', 'data_type': 'DECIMAL'},
                {'name': 'NAME', 'data_type': 'VARCHAR'},
            ],
            'primary_keys': ['ID']
        }

        similarity = matcher.calculate_table_similarity(source_table, target_table)
        assert 0 <= similarity <= 1

    def test_multiple_matches(self, matcher):
        """Test finding multiple best matches."""
        source = "CUSTOMER"
        targets = ["CUSTOMER", "CUSTOMER_OLD", "CUSTOMERS", "ORDER", "PRODUCT"]

        results = matcher.find_multiple_matches(source, targets, top_n=3)
        assert len(results) <= 3
        assert all(score >= (matcher.threshold / 100.0) for _, score in results)


class TestFuzzyMatcherIntegration:
    """Integration tests for fuzzy matching."""

    def test_realistic_table_mapping(self):
        """Test realistic table mapping scenario."""
        matcher = FuzzyMatcher(threshold=0.80)

        source_tables = ["STG_CUSTOMER", "STG_ORDER", "STG_PRODUCT"]
        target_tables = ["CUSTOMER", "ORDER", "PRODUCT"]

        matches = {}
        for source in source_tables:
            result = matcher.find_best_match(source, target_tables)
            if result:
                matches[source] = result[0]

        assert len(matches) == 3
        assert matches["STG_CUSTOMER"] == "CUSTOMER"
        assert matches["STG_ORDER"] == "ORDER"
        assert matches["STG_PRODUCT"] == "PRODUCT"

    def test_schema_naming_conventions(self):
        """Test different schema naming conventions."""
        matcher = FuzzyMatcher(
            threshold=0.85,
            ignore_prefixes=["STG_", "DW_", "TMP_"],
            ignore_suffixes=["_OLD", "_BAK", "_TEMP"]
        )

        # Different naming conventions should match
        source = "DW_CUSTOMER_OLD"
        targets = ["CUSTOMER", "CUSTOMER_TEMP", "CUSTOMER_BAK"]

        result = matcher.find_best_match(source, targets, use_normalization=True)
        assert result is not None
        assert "CUSTOMER" in result[0]
