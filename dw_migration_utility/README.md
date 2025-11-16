# Data Warehouse Migration Utility

Migration utility to facilitate transition from Oracle/Informatica-based data warehouse to Snowflake, utilizing stored procedures for transformations while maintaining target table compatibility with downstream systems.

## Features

- **Database Crawling**: Extract complete metadata from Oracle and Snowflake databases
- **Informatica XML Parsing**: Parse and extract transformation logic from Informatica PowerCenter XML files
- **Intelligent Mapping**: Fuzzy matching algorithms for automatic table and column mapping
- **Stored Procedure Generation**: Generate Snowflake stored procedures from Informatica transformations
- **Data Validation**: Comprehensive validation and data quality checks
- **Reporting**: Generate detailed migration reports and documentation

## Architecture

```
dw_migration_utility/
├── config/              # Configuration files
├── crawlers/            # Database metadata crawlers
├── parsers/             # Informatica XML parsers
├── mappers/             # Schema/column mapping logic
├── generators/          # Stored procedure generators
├── validators/          # Data validation tools
├── utils/               # Utility functions
├── output/              # Output directory for generated files
└── tests/               # Unit tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Oracle Client libraries (for Oracle connectivity)
- Access to Oracle and Snowflake databases
- Informatica XML export files

### Setup

1. Clone the repository or navigate to the project directory:
```bash
cd dw_migration_utility
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Oracle Instant Client (for Oracle connectivity):
   - Download from: https://www.oracle.com/database/technologies/instant-client/downloads.html
   - Follow installation instructions for your OS

5. Copy the environment template and configure credentials:
```bash
cp .env.template .env
# Edit .env with your database credentials
```

6. Configure migration settings:
```bash
# Edit config/migration_config.json with your environment details
```

## Configuration

### Environment Variables (.env)

```bash
ORACLE_USER=your_oracle_username
ORACLE_PASSWORD=your_oracle_password
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
```

### Migration Configuration (config/migration_config.json)

See [config/migration_config.json](config/migration_config.json) for a complete example.

Key sections:
- **oracle**: Oracle database connection details
- **snowflake**: Snowflake connection details
- **informatica**: Path to Informatica XML files
- **mapping**: Mapping rules and thresholds
- **generation**: Stored procedure generation settings
- **validation**: Validation parameters

### Manual Mappings (config/manual_mappings.json)

For tables that cannot be automatically mapped, define explicit mappings:

```json
{
  "manual_mappings": {
    "oracle_schema.oracle_table": "snowflake_db.snowflake_schema.snowflake_table"
  },
  "column_mappings": {
    "oracle_schema.oracle_table": {
      "OLD_COL_NAME": "NEW_COL_NAME"
    }
  }
}
```

## Usage

### Command Line Interface

Run the complete migration workflow:

```bash
python main.py run --config config/migration_config.json --mode full
```

### Individual Steps

**Crawl Oracle Database:**
```bash
python main.py run --config config/migration_config.json --mode crawl --database oracle
```

**Crawl Snowflake Database:**
```bash
python main.py run --config config/migration_config.json --mode crawl --database snowflake
```

**Parse Informatica XML Files:**
```bash
python main.py run --config config/migration_config.json --mode parse
```

**Generate Table Mappings:**
```bash
python main.py run --config config/migration_config.json --mode map
```

### Python API

```python
from dw_migration_utility.main import MigrationOrchestrator

# Initialize
orchestrator = MigrationOrchestrator(config_file='config/migration_config.json')

# Run full migration
summary = orchestrator.run_full_migration(
    crawl_oracle=True,
    crawl_snowflake=True,
    parse_informatica=True,
    generate_mappings=True,
    generate_procedures=True,
    validate=True
)

# Get results
print(f"Tables mapped: {summary['mapped_tables']}/{summary['total_tables']}")
print(f"Procedures generated: {summary['procedures_generated']}")
```

## Output

The utility generates several types of outputs in the `output/` directory:

### Metadata Files
- `output/metadata/oracle_*.json`: Oracle schema metadata
- `output/metadata/snowflake_*.json`: Snowflake schema metadata
- `output/metadata/*_sample.csv`: Sample data extracts
- `output/metadata/*_profile.json`: Data profiling statistics

### Stored Procedures
- `output/stored_procedures/SP_*.sql`: Generated Snowflake stored procedures

### Reports
- `output/mapping_docs/migration_summary_*.md`: Migration summary report
- `output/mapping_docs/mapping_documentation_*.md`: Table and column mappings
- `output/validation_reports/validation_report_*.md`: Validation results

### Logs
- `output/logs/migration_*.log`: Execution logs
- `output/logs/errors_*.log`: Error logs

## Features in Detail

### 1. Database Crawling

Extracts comprehensive metadata including:
- Schema and table structures
- Column definitions with data types
- Primary and foreign keys
- Indexes and constraints
- Row counts and table statistics
- Sample data for validation

### 2. Informatica XML Parsing

Parses Informatica PowerCenter XML files to extract:
- Source and target definitions
- Transformation logic (Expression, Aggregator, Filter, Joiner, Lookup, etc.)
- Data flow and lineage
- Session configuration

### 3. Intelligent Mapping

Uses multiple strategies to map Oracle tables to Snowflake:
- Exact name matching
- Fuzzy string matching (Levenshtein distance)
- Token-based similarity
- Metadata-based matching (column count, data types, primary keys)
- Manual override support

Configurable matching threshold (default: 85%)

### 4. Stored Procedure Generation

Generates Snowflake stored procedures that:
- Replicate Informatica transformation logic
- Include error handling and logging
- Support MERGE/INSERT/UPDATE operations
- Maintain data lineage
- Follow configurable naming conventions

### 5. Data Validation

Validates migration accuracy through:
- Row count comparison
- Sample data comparison
- NULL value checks
- Data type validation
- Primary key integrity

### 6. Reporting

Comprehensive reports including:
- Migration summary with statistics
- Table and column mapping documentation
- Data lineage documentation
- Validation results
- Unmapped tables requiring manual intervention

## Workflow

```
1. Configuration
   ├── Set up database connections
   ├── Load mapping rules
   └── Configure output directories

2. Metadata Extraction
   ├── Crawl Oracle database
   ├── Crawl Snowflake database
   └── Generate metadata JSON files

3. Informatica Parsing
   ├── Load Informatica XML files
   ├── Parse transformations
   └── Generate lineage documentation

4. Mapping Generation
   ├── Match Oracle → Snowflake tables
   ├── Match columns
   ├── Apply manual overrides
   └── Generate mapping report

5. Stored Procedure Generation
   ├── Translate transformation logic
   ├── Generate SQL procedures
   └── Create deployment scripts

6. Validation
   ├── Execute validation queries
   ├── Compare results
   └── Generate validation report

7. Documentation
   ├── Generate summary report
   ├── Create lineage documentation
   └── Document unmapped objects
```

## Troubleshooting

### Oracle Connection Issues

If you encounter Oracle connection errors:
1. Ensure Oracle Instant Client is properly installed
2. Set `LD_LIBRARY_PATH` (Linux) or `PATH` (Windows) to include Oracle client libraries
3. Verify TNS configuration if using TNS names

### Snowflake Connection Issues

Common issues:
- Check account identifier format (account.region.cloud)
- Ensure warehouse is running
- Verify user has necessary permissions
- Check for network/firewall restrictions

### Low Mapping Success Rate

To improve automatic mapping:
1. Lower fuzzy matching threshold in config
2. Add common prefixes/suffixes to ignore lists
3. Use manual mappings for complex cases
4. Review and adjust token-based matching rules

## Development

### Running Tests

```bash
pytest tests/ -v --cov=dw_migration_utility
```

### Adding New Transformations

To add support for new Informatica transformations:
1. Update `parsers/informatica_xml_parser.py` to parse the transformation
2. Add translation logic in `generators/sql_translator.py`
3. Update stored procedure templates in `generators/template_engine.py`

## Performance Considerations

- Parallel processing for multiple tables (configurable)
- Batch processing for large datasets
- Connection pooling enabled
- Configurable sample sizes for data profiling
- Progress indicators for long operations

## Security

- Credentials stored in environment variables
- No hardcoded passwords
- Encrypted connection support
- Audit logging enabled
- Role-based access control awareness

## Version

**Version:** 1.0.0
**Last Updated:** 2025-11-16
**Python:** 3.8+

## Support

For issues, questions, or contributions, please contact the data engineering team.

## License

Internal use only - Migration Team

## Future Enhancements

- Web-based UI for mapping management
- Real-time migration monitoring dashboard
- Support for incremental updates
- Integration with data catalog tools
- CI/CD pipeline integration
- Support for additional sources (SQL Server, Teradata)
- Machine learning for improved mapping accuracy
