"""
Schema-level mapping for Oracle to Snowflake migration.
"""
from typing import Dict, List, Tuple, Optional
from loguru import logger

from .fuzzy_matcher import FuzzyMatcher
from ..crawlers.metadata_models import SchemaMetadata, TableMetadata


class SchemaMapper:
    """Map Oracle schemas to Snowflake schemas."""

    def __init__(self, fuzzy_matcher: FuzzyMatcher = None):
        """
        Initialize schema mapper.

        Args:
            fuzzy_matcher: FuzzyMatcher instance for table matching
        """
        self.fuzzy_matcher = fuzzy_matcher or FuzzyMatcher()
        self.schema_mappings = {}
        self.table_mappings = {}

    def map_schemas(
        self,
        oracle_schemas: List[SchemaMetadata],
        snowflake_schemas: List[SchemaMetadata],
        manual_mappings: Dict[str, str] = None
    ) -> Dict[str, Dict]:
        """
        Map Oracle schemas to Snowflake schemas.

        Args:
            oracle_schemas: List of Oracle SchemaMetadata objects
            snowflake_schemas: List of Snowflake SchemaMetadata objects
            manual_mappings: Manual schema mappings

        Returns:
            Dictionary of schema mappings
        """
        logger.info("Mapping Oracle schemas to Snowflake schemas")

        self.schema_mappings = {}

        for oracle_schema in oracle_schemas:
            schema_name = oracle_schema.schema_name

            # Check manual mappings first
            if manual_mappings and schema_name in manual_mappings:
                sf_schema = manual_mappings[schema_name]
                self.schema_mappings[schema_name] = {
                    'oracle_schema': schema_name,
                    'snowflake_schema': sf_schema,
                    'match_type': 'manual',
                    'match_score': 1.0,
                    'table_count': len(oracle_schema.tables)
                }
                logger.info(f"Manual mapping: {schema_name} -> {sf_schema}")
                continue

            # Try to find automatic match
            snowflake_schema_names = [s.schema_name for s in snowflake_schemas]
            match_result = self.fuzzy_matcher.find_best_match(
                schema_name,
                snowflake_schema_names,
                use_normalization=True
            )

            if match_result:
                matched_name, score, match_type = match_result
                self.schema_mappings[schema_name] = {
                    'oracle_schema': schema_name,
                    'snowflake_schema': matched_name,
                    'match_type': match_type,
                    'match_score': score,
                    'table_count': len(oracle_schema.tables)
                }
                logger.info(f"Fuzzy match: {schema_name} -> {matched_name} (score: {score:.2f})")
            else:
                # Default to PUBLIC schema if no match
                self.schema_mappings[schema_name] = {
                    'oracle_schema': schema_name,
                    'snowflake_schema': 'PUBLIC',
                    'match_type': 'default',
                    'match_score': 0.0,
                    'table_count': len(oracle_schema.tables),
                    'manual_review_required': True
                }
                logger.warning(f"No match found for schema {schema_name}, defaulting to PUBLIC")

        return self.schema_mappings

    def get_target_schema(self, oracle_schema: str) -> str:
        """
        Get target Snowflake schema for Oracle schema.

        Args:
            oracle_schema: Oracle schema name

        Returns:
            Target Snowflake schema name
        """
        if oracle_schema in self.schema_mappings:
            return self.schema_mappings[oracle_schema]['snowflake_schema']
        return 'PUBLIC'

    def get_schema_mapping_summary(self) -> Dict:
        """
        Get summary of schema mappings.

        Returns:
            Summary dictionary
        """
        total = len(self.schema_mappings)
        automatic = sum(1 for m in self.schema_mappings.values() if m['match_type'] != 'manual')
        manual = sum(1 for m in self.schema_mappings.values() if m['match_type'] == 'manual')
        defaults = sum(1 for m in self.schema_mappings.values() if m['match_type'] == 'default')

        return {
            'total_schemas': total,
            'automatic_matches': automatic,
            'manual_mappings': manual,
            'default_mappings': defaults,
            'mapping_success_rate': (total - defaults) / total * 100 if total > 0 else 0
        }

    def map_tables_in_schemas(
        self,
        oracle_schemas: List[SchemaMetadata],
        snowflake_schemas: List[SchemaMetadata],
        manual_table_mappings: Dict[str, str] = None
    ) -> Dict[str, Dict]:
        """
        Map tables across all schemas.

        Args:
            oracle_schemas: List of Oracle schemas
            snowflake_schemas: List of Snowflake schemas
            manual_table_mappings: Manual table mappings

        Returns:
            Dictionary of table mappings
        """
        logger.info("Mapping tables across schemas")

        self.table_mappings = {}

        # First ensure schemas are mapped
        if not self.schema_mappings:
            self.map_schemas(oracle_schemas, snowflake_schemas)

        # Build Snowflake table lookup
        sf_tables_by_schema = {}
        for sf_schema in snowflake_schemas:
            sf_tables_by_schema[sf_schema.schema_name] = {
                'database': sf_schema.database,
                'tables': {t.table_name: t for t in sf_schema.tables}
            }

        # Map tables in each Oracle schema
        for oracle_schema in oracle_schemas:
            target_sf_schema = self.get_target_schema(oracle_schema.schema_name)

            # Get Snowflake tables in target schema
            sf_tables = sf_tables_by_schema.get(target_sf_schema, {}).get('tables', {})
            sf_table_names = list(sf_tables.keys())

            logger.info(f"Mapping {len(oracle_schema.tables)} tables in {oracle_schema.schema_name}")

            for oracle_table in oracle_schema.tables:
                table_key = f"{oracle_schema.schema_name}.{oracle_table.table_name}"

                # Check manual mappings first
                if manual_table_mappings and table_key in manual_table_mappings:
                    sf_table_path = manual_table_mappings[table_key]
                    self.table_mappings[table_key] = {
                        'oracle_schema': oracle_schema.schema_name,
                        'oracle_table': oracle_table.table_name,
                        'snowflake_table_path': sf_table_path,
                        'match_type': 'manual',
                        'match_score': 1.0
                    }
                    logger.debug(f"Manual table mapping: {table_key} -> {sf_table_path}")
                    continue

                # Try to find automatic match
                match_result = self.fuzzy_matcher.find_best_match(
                    oracle_table.table_name,
                    sf_table_names,
                    use_normalization=True
                )

                if match_result:
                    matched_name, score, match_type = match_result
                    sf_database = sf_tables_by_schema.get(target_sf_schema, {}).get('database', '')
                    sf_table_path = f"{sf_database}.{target_sf_schema}.{matched_name}"

                    self.table_mappings[table_key] = {
                        'oracle_schema': oracle_schema.schema_name,
                        'oracle_table': oracle_table.table_name,
                        'snowflake_table_path': sf_table_path,
                        'match_type': match_type,
                        'match_score': score
                    }
                    logger.debug(f"Table match: {table_key} -> {sf_table_path} (score: {score:.2f})")
                else:
                    self.table_mappings[table_key] = {
                        'oracle_schema': oracle_schema.schema_name,
                        'oracle_table': oracle_table.table_name,
                        'snowflake_table_path': None,
                        'match_type': 'unmapped',
                        'match_score': 0.0,
                        'manual_review_required': True
                    }
                    logger.warning(f"No table match found: {table_key}")

        return self.table_mappings

    def get_unmapped_tables(self) -> List[str]:
        """
        Get list of unmapped tables.

        Returns:
            List of unmapped table keys
        """
        return [
            key for key, mapping in self.table_mappings.items()
            if mapping.get('match_type') == 'unmapped'
        ]

    def get_table_mapping_summary(self) -> Dict:
        """
        Get summary of table mappings.

        Returns:
            Summary dictionary
        """
        total = len(self.table_mappings)
        mapped = sum(1 for m in self.table_mappings.values() if m.get('snowflake_table_path'))
        unmapped = total - mapped

        # Count by match type
        by_type = {}
        for mapping in self.table_mappings.values():
            match_type = mapping.get('match_type', 'unknown')
            by_type[match_type] = by_type.get(match_type, 0) + 1

        return {
            'total_tables': total,
            'mapped_tables': mapped,
            'unmapped_tables': unmapped,
            'mapping_success_rate': (mapped / total * 100) if total > 0 else 0,
            'by_match_type': by_type
        }

    def export_mappings(self, output_file: str) -> None:
        """
        Export mappings to JSON file.

        Args:
            output_file: Path to output JSON file
        """
        import json

        export_data = {
            'schema_mappings': self.schema_mappings,
            'table_mappings': self.table_mappings,
            'summary': {
                'schemas': self.get_schema_mapping_summary(),
                'tables': self.get_table_mapping_summary()
            }
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Mappings exported to: {output_file}")
