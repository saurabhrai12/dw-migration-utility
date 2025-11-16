# Quick Start Guide

Get started with the Data Warehouse Migration Utility in minutes.

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.8 or higher installed
- [ ] Oracle database access credentials
- [ ] Snowflake account and credentials
- [ ] Informatica XML export files (optional for initial testing)

## Installation Steps

### 1. Set Up Python Environment

```bash
# Navigate to project directory
cd dw_migration_utility

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Oracle Client (for Oracle connectivity)

**macOS:**
```bash
# Download Oracle Instant Client
# https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html

# Extract and set library path
export DYLD_LIBRARY_PATH=/path/to/instantclient_19_8:$DYLD_LIBRARY_PATH
```

**Linux:**
```bash
# Download Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/...

# Extract and set library path
export LD_LIBRARY_PATH=/path/to/instantclient_19_8:$LD_LIBRARY_PATH
```

**Windows:**
```cmd
# Download and extract Oracle Instant Client
# Add the path to your system PATH environment variable
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

Update `.env`:
```bash
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
```

### 5. Configure Migration Settings

```bash
# Edit the configuration file
nano config/migration_config.json
```

Update these key fields:
```json
{
  "oracle": {
    "host": "your-oracle-host.com",
    "port": 1521,
    "service_name": "YOUR_SERVICE",
    "schemas": ["SCHEMA1", "SCHEMA2"]
  },
  "snowflake": {
    "account": "your-account.region",
    "warehouse": "YOUR_WAREHOUSE",
    "database": "YOUR_DATABASE",
    "schemas": ["PUBLIC", "STAGING"]
  }
}
```

## Your First Migration

### Test Database Connectivity

```bash
# Test Oracle connection
python -c "
from utils.config_loader import ConfigLoader
from utils.db_connector import OracleConnector

config = ConfigLoader('config/migration_config.json')
oracle_config = config.get_oracle_config()

with OracleConnector(oracle_config) as conn:
    result = conn.execute_query('SELECT 1 FROM DUAL')
    print('Oracle connection successful!')
"

# Test Snowflake connection
python -c "
from utils.config_loader import ConfigLoader
from utils.db_connector import SnowflakeConnector

config = ConfigLoader('config/migration_config.json')
sf_config = config.get_snowflake_config()

with SnowflakeConnector(sf_config) as conn:
    result = conn.execute_query('SELECT 1')
    print('Snowflake connection successful!')
"
```

### Run Metadata Crawl Only (Safe Test)

```bash
# Crawl Oracle metadata (read-only operation)
python main.py run \
  --config config/migration_config.json \
  --mode crawl \
  --database oracle

# Check output
ls -la output/metadata/oracle_*.json
```

### Run Complete Migration Workflow

```bash
# Run full migration
python main.py run \
  --config config/migration_config.json \
  --mode full
```

### Review Results

```bash
# Check generated reports
ls -la output/mapping_docs/

# View migration summary
cat output/mapping_docs/migration_summary_*.md

# Check logs
tail -f output/logs/migration_*.log
```

## Common Tasks

### Crawl Both Databases

```bash
python main.py run \
  --config config/migration_config.json \
  --mode crawl \
  --database both
```

### Generate Table Mappings Only

```bash
python main.py run \
  --config config/migration_config.json \
  --mode map
```

### Parse Informatica XML Files

First, place your Informatica XML files in the directory specified in config:

```bash
mkdir -p /path/to/informatica/exports
# Copy XML files there

# Parse the files
python main.py run \
  --config config/migration_config.json \
  --mode parse
```

## Understanding the Output

After running the migration, you'll find:

```
output/
├── metadata/
│   ├── oracle_SCHEMA1_metadata.json       # Oracle schema metadata
│   ├── snowflake_DATABASE_SCHEMA_metadata.json  # Snowflake metadata
│   ├── *_sample.csv                       # Sample data extracts
│   └── *_profile.json                     # Data profiling stats
│
├── mapping_docs/
│   ├── migration_summary_TIMESTAMP.md     # Overall summary
│   ├── mapping_documentation_TIMESTAMP.md # Table/column mappings
│   └── *.html                             # HTML versions of reports
│
├── validation_reports/
│   └── validation_report_TIMESTAMP.md     # Validation results
│
└── logs/
    ├── migration_DATE.log                 # All logs
    └── errors_DATE.log                    # Error logs only
```

## Using Python API

Create a custom script:

```python
# my_migration.py
from main import MigrationOrchestrator

# Initialize orchestrator
orchestrator = MigrationOrchestrator('config/migration_config.json')

# Crawl metadata
orchestrator.crawl_oracle_metadata()
orchestrator.crawl_snowflake_metadata()

# Generate mappings
orchestrator.generate_table_mappings()

# Get summary
summary = orchestrator.get_summary()
print(f"Mapped {summary['mapped_tables']} out of {summary['total_tables']} tables")
```

Run it:
```bash
python my_migration.py
```

## Customizing Mappings

### Add Manual Table Mappings

Edit `config/manual_mappings.json`:

```json
{
  "manual_mappings": {
    "ORACLE_SCHEMA.OLD_TABLE_NAME": "SNOWFLAKE_DB.SCHEMA.NEW_TABLE_NAME"
  }
}
```

### Adjust Fuzzy Matching Threshold

Edit `config/migration_config.json`:

```json
{
  "mapping": {
    "fuzzy_threshold": 0.75,  // Lower = more lenient matching
    "ignore_prefixes": ["STG_", "TMP_", "MY_PREFIX_"],
    "ignore_suffixes": ["_OLD", "_BACKUP", "_MY_SUFFIX"]
  }
}
```

## Troubleshooting

### Oracle Connection Failed

```bash
# Check Oracle client installation
python -c "import cx_Oracle; print(cx_Oracle.version)"

# Verify TNS connectivity
tnsping YOUR_SERVICE_NAME
```

### Snowflake Connection Failed

```bash
# Test with simple connection
python -c "
import snowflake.connector
conn = snowflake.connector.connect(
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT'
)
print('Connected!')
"
```

### Low Mapping Success

1. Check the logs: `tail -100 output/logs/migration_*.log`
2. Lower fuzzy threshold in config
3. Add table prefixes/suffixes to ignore lists
4. Use manual mappings for problematic tables

### Permission Errors

Ensure your database users have:
- Oracle: SELECT on ALL_TABLES, ALL_TAB_COLUMNS, etc.
- Snowflake: USAGE on warehouse/database, SELECT on INFORMATION_SCHEMA

## Next Steps

1. **Review the mappings**: Check `output/mapping_docs/mapping_documentation_*.md`
2. **Validate unmapped tables**: Review migration summary for manual mapping needs
3. **Generate stored procedures**: Implement the SQL translation logic (TODO in project)
4. **Test in dev environment**: Deploy and test generated procedures
5. **Run validation**: Compare data between Oracle and Snowflake

## Getting Help

- Check logs in `output/logs/`
- Review the full [README.md](README.md)
- Examine configuration in `config/migration_config.json`
- Contact the data engineering team

## Advanced Usage

### Parallel Processing (Future Enhancement)

```python
from concurrent.futures import ThreadPoolExecutor

orchestrator = MigrationOrchestrator('config/migration_config.json')

# Process schemas in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for schema in schemas:
        future = executor.submit(orchestrator.crawl_schema, schema)
        futures.append(future)
```

### Custom Transformation Logic

Extend the `InformaticaXMLParser` to handle custom transformations:

```python
from parsers.informatica_xml_parser import InformaticaXMLParser

class CustomParser(InformaticaXMLParser):
    def _extract_custom_transformation(self, xml_data):
        # Your custom logic here
        pass
```

---

**You're now ready to migrate your data warehouse!** 🚀
