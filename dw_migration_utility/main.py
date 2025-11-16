"""
Main orchestrator for the data warehouse migration utility.
"""
import click
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from utils.logger import setup_logger
from utils.config_loader import ConfigLoader
from utils.db_connector import OracleConnector, SnowflakeConnector
from utils.report_generator import ReportGenerator

from crawlers.oracle_crawler import OracleCrawler
from crawlers.snowflake_crawler import SnowflakeCrawler
from parsers.informatica_xml_parser import parse_multiple_xml_files
from mappers.fuzzy_matcher import FuzzyMatcher
from mappers.schema_mapper import SchemaMapper
from mappers.column_mapper import ColumnMapper
from generators.sql_translator import SQLTranslator
from generators.stored_proc_generator import StoredProcedureGenerator
from validators.data_validator import DataValidator


class MigrationOrchestrator:
    """Orchestrate the complete migration workflow."""

    def __init__(self, config_file: str):
        """
        Initialize migration orchestrator.

        Args:
            config_file: Path to configuration file
        """
        # Setup logger
        setup_logger()
        logger.info("Initializing Migration Orchestrator")

        # Load configuration
        self.config_loader = ConfigLoader(config_file)
        self.config = self.config_loader.load_config()

        # Initialize report generator
        self.report_gen = ReportGenerator()

        # Results storage
        self.oracle_schemas = []
        self.snowflake_schemas = []
        self.informatica_mappings = []
        self.table_mappings = []
        self.validation_results = []

    def run_full_migration(
        self,
        crawl_oracle: bool = True,
        crawl_snowflake: bool = True,
        parse_informatica: bool = True,
        generate_mappings: bool = True,
        generate_procedures: bool = False,
        validate: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete migration workflow.

        Args:
            crawl_oracle: Whether to crawl Oracle database
            crawl_snowflake: Whether to crawl Snowflake database
            parse_informatica: Whether to parse Informatica XML files
            generate_mappings: Whether to generate table/column mappings
            generate_procedures: Whether to generate stored procedures
            validate: Whether to run validation

        Returns:
            Summary dictionary
        """
        logger.info("=" * 80)
        logger.info("Starting Full Migration Workflow")
        logger.info("=" * 80)

        try:
            # Step 1: Crawl Oracle
            if crawl_oracle:
                logger.info("\n[Step 1] Crawling Oracle Database...")
                self.crawl_oracle_metadata()

            # Step 2: Crawl Snowflake
            if crawl_snowflake:
                logger.info("\n[Step 2] Crawling Snowflake Database...")
                self.crawl_snowflake_metadata()

            # Step 3: Parse Informatica
            if parse_informatica:
                logger.info("\n[Step 3] Parsing Informatica XML Files...")
                self.parse_informatica_mappings()

            # Step 4: Generate Mappings
            if generate_mappings:
                logger.info("\n[Step 4] Generating Table and Column Mappings...")
                self.generate_table_mappings()

            # Step 5: Generate Stored Procedures
            if generate_procedures:
                logger.info("\n[Step 5] Generating Snowflake Stored Procedures...")
                self.generate_stored_procedures()

            # Step 6: Validation
            if validate:
                logger.info("\n[Step 6] Running Validation...")
                self.run_validation()

            # Generate summary report
            logger.info("\n[Final] Generating Summary Report...")
            summary = self.get_summary()
            self.generate_reports()

            logger.info("=" * 80)
            logger.info("Migration Workflow Completed Successfully!")
            logger.info("=" * 80)

            return summary

        except Exception as e:
            logger.error(f"Migration workflow failed: {e}")
            raise

    def crawl_oracle_metadata(self) -> None:
        """Crawl Oracle database metadata."""
        oracle_config = self.config_loader.get_oracle_config()

        with OracleConnector(oracle_config) as conn:
            crawler = OracleCrawler(conn)
            schemas = oracle_config.get('schemas', [])
            sample_size = self.config_loader.get('validation.sample_size', 1000)

            self.oracle_schemas = crawler.crawl_multiple_schemas(schemas, sample_size)

        logger.info(f"Crawled {len(self.oracle_schemas)} Oracle schemas")

    def crawl_snowflake_metadata(self) -> None:
        """Crawl Snowflake database metadata."""
        snowflake_config = self.config_loader.get_snowflake_config()

        with SnowflakeConnector(snowflake_config) as conn:
            crawler = SnowflakeCrawler(conn)
            database = snowflake_config.get('database')
            schemas = snowflake_config.get('schemas', ['PUBLIC'])
            sample_size = self.config_loader.get('validation.sample_size', 1000)

            self.snowflake_schemas = crawler.crawl_multiple_schemas(database, schemas, sample_size)

        logger.info(f"Crawled {len(self.snowflake_schemas)} Snowflake schemas")

    def parse_informatica_mappings(self) -> None:
        """Parse Informatica XML files."""
        informatica_config = self.config_loader.get_informatica_config()
        xml_directory = informatica_config.get('xml_directory')
        file_pattern = informatica_config.get('file_pattern', '*.xml')

        self.informatica_mappings = parse_multiple_xml_files(xml_directory, file_pattern)

        logger.info(f"Parsed {len(self.informatica_mappings)} Informatica mappings")

    def generate_table_mappings(self) -> None:
        """Generate table and column mappings."""
        mapping_config = self.config_loader.get_mapping_config()

        # Initialize fuzzy matcher
        fuzzy_matcher = FuzzyMatcher(
            threshold=mapping_config.get('fuzzy_threshold', 0.85),
            ignore_prefixes=mapping_config.get('ignore_prefixes', []),
            ignore_suffixes=mapping_config.get('ignore_suffixes', [])
        )

        # Build table lists
        oracle_tables = []
        for schema in self.oracle_schemas:
            for table in schema.tables:
                oracle_tables.append({
                    'schema': schema.schema_name,
                    'table_name': table.table_name,
                    'columns': [{'name': c.name, 'data_type': c.data_type} for c in table.columns],
                    'primary_keys': table.primary_keys,
                    'metadata': table
                })

        snowflake_tables = []
        for schema in self.snowflake_schemas:
            for table in schema.tables:
                snowflake_tables.append({
                    'database': schema.database,
                    'schema': schema.schema_name,
                    'table_name': table.table_name,
                    'columns': [{'name': c.name, 'data_type': c.data_type} for c in table.columns],
                    'primary_keys': table.primary_keys,
                    'metadata': table
                })

        # Match tables
        for oracle_table in oracle_tables:
            # Find best match in Snowflake
            snowflake_table_names = [t['table_name'] for t in snowflake_tables]
            match_result = fuzzy_matcher.find_best_match(
                oracle_table['table_name'],
                snowflake_table_names
            )

            if match_result:
                matched_name, score, match_type = match_result

                # Find the full Snowflake table object
                snowflake_table = next(
                    (t for t in snowflake_tables if t['table_name'] == matched_name),
                    None
                )

                if snowflake_table:
                    mapping = {
                        'oracle_schema': oracle_table['schema'],
                        'oracle_table': oracle_table['table_name'],
                        'snowflake_database': snowflake_table['database'],
                        'snowflake_schema': snowflake_table['schema'],
                        'snowflake_table': snowflake_table['table_name'],
                        'match_type': match_type,
                        'match_score': score
                    }
                    self.table_mappings.append(mapping)

        logger.info(f"Generated {len(self.table_mappings)} table mappings")

    def generate_stored_procedures(self) -> None:
        """Generate Snowflake stored procedures."""
        logger.info("Generating Snowflake stored procedures")

        if not self.informatica_mappings:
            logger.warning("No Informatica mappings available for procedure generation")
            return

        gen_config = self.config_loader.get_generation_config()
        output_dir = gen_config.get('output_directory', 'output/stored_procedures')
        schema = self.config_loader.get_snowflake_config().get('schema', 'PUBLIC')

        generator = StoredProcedureGenerator(output_dir, schema)

        for mapping in self.informatica_mappings:
            try:
                # Find corresponding Snowflake table metadata
                target_metadata = None
                if mapping.targets:
                    target_name = mapping.targets[0].name
                    for schema_meta in self.snowflake_schemas:
                        for table in schema_meta.tables:
                            if table.table_name == target_name:
                                target_metadata = table
                                break

                generator.generate_from_mapping(mapping, target_metadata)
            except Exception as e:
                logger.error(f"Failed to generate procedure for {mapping.name}: {e}")
                continue

        # Generate deployment script
        generator.generate_deployment_script()
        generator.generate_procedure_documentation()

        logger.info(f"Generated {len(generator.get_generated_procedures())} stored procedures")

    def run_validation(self) -> None:
        """Run validation checks."""
        logger.info("Running validation checks")

        oracle_config = self.config_loader.get_oracle_config()
        snowflake_config = self.config_loader.get_snowflake_config()
        val_config = self.config_loader.get_validation_config()

        try:
            with OracleConnector(oracle_config) as oracle_conn:
                with SnowflakeConnector(snowflake_config) as snowflake_conn:
                    validator = DataValidator(oracle_conn, snowflake_conn)

                    # Validate each mapped table
                    for mapping in self.table_mappings:
                        oracle_schema = mapping['oracle_schema']
                        oracle_table = mapping['oracle_table']
                        snowflake_table_path = mapping['snowflake_table_path']

                        if not snowflake_table_path:
                            continue

                        # Parse Snowflake table path
                        parts = snowflake_table_path.split('.')
                        sf_database = parts[0]
                        sf_schema = parts[1]
                        sf_table = parts[2]

                        # Run validations
                        if val_config.get('row_count_check', True):
                            validator.validate_row_count(
                                oracle_schema,
                                oracle_table,
                                sf_database,
                                sf_schema,
                                sf_table
                            )

                        if val_config.get('data_comparison', True):
                            validator.validate_sample_data(
                                oracle_schema,
                                oracle_table,
                                sf_database,
                                sf_schema,
                                sf_table,
                                val_config.get('sample_size', 1000)
                            )

                    self.validation_results = validator.get_validation_summary()
                    logger.info(f"Validation complete: {self.validation_results['success_rate']:.1f}% passed")

        except Exception as e:
            logger.error(f"Validation failed: {e}")

    def generate_reports(self) -> None:
        """Generate all reports."""
        # Migration summary
        total_oracle_tables = sum(len(s.tables) for s in self.oracle_schemas)
        unmapped_tables = []  # TODO: Calculate unmapped tables

        self.report_gen.generate_migration_summary(
            total_tables=total_oracle_tables,
            mapped_tables=len(self.table_mappings),
            unmapped_tables=unmapped_tables,
            procedures_generated=0,
            validation_results={}
        )

        # Mapping documentation
        if self.table_mappings:
            self.report_gen.generate_mapping_documentation(
                table_mappings=self.table_mappings,
                column_mappings=[]
            )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get migration summary.

        Returns:
            Summary dictionary
        """
        total_oracle_tables = sum(len(s.tables) for s in self.oracle_schemas)

        return {
            'oracle_schemas': len(self.oracle_schemas),
            'snowflake_schemas': len(self.snowflake_schemas),
            'total_tables': total_oracle_tables,
            'mapped_tables': len(self.table_mappings),
            'informatica_mappings': len(self.informatica_mappings),
            'procedures_generated': 0,
            'validation_status': 'Not Run'
        }


@click.group()
def cli():
    """Data Warehouse Migration Utility CLI."""
    pass


@cli.command()
@click.option('--config', '-c', required=True, help='Path to configuration file')
@click.option('--mode', '-m', type=click.Choice(['full', 'crawl', 'parse', 'map', 'generate', 'validate']), default='full')
@click.option('--database', '-d', type=click.Choice(['oracle', 'snowflake', 'both']), default='both')
def run(config: str, mode: str, database: str):
    """Run migration workflow."""
    orchestrator = MigrationOrchestrator(config)

    if mode == 'full':
        summary = orchestrator.run_full_migration()
        click.echo("\n=== Migration Summary ===")
        click.echo(f"Oracle Schemas: {summary['oracle_schemas']}")
        click.echo(f"Snowflake Schemas: {summary['snowflake_schemas']}")
        click.echo(f"Mapped Tables: {summary['mapped_tables']}/{summary['total_tables']}")

    elif mode == 'crawl':
        if database in ['oracle', 'both']:
            orchestrator.crawl_oracle_metadata()
        if database in ['snowflake', 'both']:
            orchestrator.crawl_snowflake_metadata()
        click.echo(f"Crawling completed for {database}")

    elif mode == 'parse':
        orchestrator.parse_informatica_mappings()
        click.echo(f"Parsed {len(orchestrator.informatica_mappings)} mappings")

    elif mode == 'map':
        orchestrator.crawl_oracle_metadata()
        orchestrator.crawl_snowflake_metadata()
        orchestrator.generate_table_mappings()
        orchestrator.generate_reports()
        click.echo(f"Generated {len(orchestrator.table_mappings)} mappings")


@cli.command()
def version():
    """Show version information."""
    click.echo("Data Warehouse Migration Utility v1.0.0")


if __name__ == '__main__':
    cli()
