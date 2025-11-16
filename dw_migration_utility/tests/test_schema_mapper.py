"""
Unit tests for schema mapping.
"""
import pytest
from mappers.schema_mapper import SchemaMapper
from crawlers.metadata_models import SchemaMetadata, TableMetadata, ColumnMetadata


class TestSchemaMapper:
    """Test SchemaMapper class."""

    @pytest.fixture
    def mapper(self):
        """Create SchemaMapper instance."""
        return SchemaMapper()

    @pytest.fixture
    def oracle_schemas(self):
        """Create sample Oracle schemas."""
        schema1 = SchemaMetadata(schema_name="DW_STAGE")
        schema1.tables = [
            TableMetadata(
                schema="DW_STAGE",
                table_name="CUSTOMER",
                columns=[ColumnMetadata(name="ID", data_type="NUMBER")]
            )
        ]

        schema2 = SchemaMetadata(schema_name="DW_CORE")
        schema2.tables = [
            TableMetadata(
                schema="DW_CORE",
                table_name="DIM_CUSTOMER",
                columns=[ColumnMetadata(name="CUSTOMER_KEY", data_type="NUMBER")]
            )
        ]

        return [schema1, schema2]

    @pytest.fixture
    def snowflake_schemas(self):
        """Create sample Snowflake schemas."""
        schema1 = SchemaMetadata(database="DW_PROD", schema_name="STAGING")
        schema1.tables = [
            TableMetadata(
                schema="STAGING",
                table_name="CUSTOMER",
                columns=[ColumnMetadata(name="ID", data_type="DECIMAL")]
            )
        ]

        schema2 = SchemaMetadata(database="DW_PROD", schema_name="PUBLIC")
        schema2.tables = [
            TableMetadata(
                schema="PUBLIC",
                table_name="DIM_CUSTOMER",
                columns=[ColumnMetadata(name="CUSTOMER_KEY", data_type="DECIMAL")]
            )
        ]

        return [schema1, schema2]

    def test_map_schemas(self, mapper, oracle_schemas, snowflake_schemas):
        """Test schema mapping."""
        mappings = mapper.map_schemas(oracle_schemas, snowflake_schemas)

        assert len(mappings) == 2
        assert "DW_STAGE" in mappings
        assert "DW_CORE" in mappings

    def test_manual_schema_mapping(self, mapper, oracle_schemas, snowflake_schemas):
        """Test manual schema mapping."""
        manual_mappings = {
            "DW_STAGE": "STAGING",
            "DW_CORE": "PUBLIC"
        }

        mappings = mapper.map_schemas(oracle_schemas, snowflake_schemas, manual_mappings)

        assert mappings["DW_STAGE"]["snowflake_schema"] == "STAGING"
        assert mappings["DW_STAGE"]["match_type"] == "manual"
        assert mappings["DW_CORE"]["snowflake_schema"] == "PUBLIC"

    def test_get_target_schema(self, mapper, oracle_schemas, snowflake_schemas):
        """Test getting target schema."""
        mapper.map_schemas(oracle_schemas, snowflake_schemas)

        target = mapper.get_target_schema("DW_STAGE")
        assert target in ["STAGING", "PUBLIC"]

    def test_schema_mapping_summary(self, mapper, oracle_schemas, snowflake_schemas):
        """Test schema mapping summary."""
        mapper.map_schemas(oracle_schemas, snowflake_schemas)

        summary = mapper.get_schema_mapping_summary()

        assert summary['total_schemas'] == 2
        assert 'automatic_matches' in summary
        assert 'mapping_success_rate' in summary

    def test_map_tables_in_schemas(self, mapper, oracle_schemas, snowflake_schemas):
        """Test table mapping across schemas."""
        mapper.map_schemas(oracle_schemas, snowflake_schemas)
        table_mappings = mapper.map_tables_in_schemas(oracle_schemas, snowflake_schemas)

        assert len(table_mappings) > 0

    def test_get_unmapped_tables(self, mapper, oracle_schemas, snowflake_schemas):
        """Test getting unmapped tables."""
        mapper.map_schemas(oracle_schemas, snowflake_schemas)
        mapper.map_tables_in_schemas(oracle_schemas, snowflake_schemas)

        unmapped = mapper.get_unmapped_tables()
        assert isinstance(unmapped, list)

    def test_table_mapping_summary(self, mapper, oracle_schemas, snowflake_schemas):
        """Test table mapping summary."""
        mapper.map_schemas(oracle_schemas, snowflake_schemas)
        mapper.map_tables_in_schemas(oracle_schemas, snowflake_schemas)

        summary = mapper.get_table_mapping_summary()

        assert 'total_tables' in summary
        assert 'mapped_tables' in summary
        assert 'mapping_success_rate' in summary

    def test_export_mappings(self, mapper, oracle_schemas, snowflake_schemas, tmp_path):
        """Test exporting mappings to JSON."""
        mapper.map_schemas(oracle_schemas, snowflake_schemas)
        mapper.map_tables_in_schemas(oracle_schemas, snowflake_schemas)

        output_file = tmp_path / "mappings.json"
        mapper.export_mappings(str(output_file))

        assert output_file.exists()

        # Verify JSON content
        import json
        with open(output_file) as f:
            data = json.load(f)

        assert 'schema_mappings' in data
        assert 'table_mappings' in data
        assert 'summary' in data


class TestSchemaMapperIntegration:
    """Integration tests for schema mapping."""

    def test_realistic_dw_mapping(self):
        """Test realistic data warehouse schema mapping."""
        mapper = SchemaMapper()

        # Create realistic Oracle schemas
        oracle_schemas = []
        for schema in ["DW_STAGE", "DW_CORE", "DW_MARTS"]:
            s = SchemaMetadata(schema_name=schema)
            s.tables = [
                TableMetadata(schema=schema, table_name="CUSTOMER"),
                TableMetadata(schema=schema, table_name="ORDER"),
                TableMetadata(schema=schema, table_name="PRODUCT")
            ]
            oracle_schemas.append(s)

        # Create realistic Snowflake schemas
        snowflake_schemas = []
        for schema in ["STAGING", "CORE", "MARTS"]:
            s = SchemaMetadata(database="DW_PROD", schema_name=schema)
            s.tables = [
                TableMetadata(schema=schema, table_name="CUSTOMER"),
                TableMetadata(schema=schema, table_name="ORDER"),
                TableMetadata(schema=schema, table_name="PRODUCT")
            ]
            snowflake_schemas.append(s)

        # Map schemas and tables
        mapper.map_schemas(oracle_schemas, snowflake_schemas)
        table_mappings = mapper.map_tables_in_schemas(oracle_schemas, snowflake_schemas)

        # Verify results
        assert len(mapper.schema_mappings) == 3
        assert len(table_mappings) > 0

        summary = mapper.get_table_mapping_summary()
        assert summary['mapped_tables'] > 0
