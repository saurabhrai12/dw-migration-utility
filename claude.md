# Data Warehouse Migration Utility - Requirements Document

## Project Overview

Migration utility to facilitate transition from Oracle/Informatica-based data warehouse to Snowflake, utilizing stored procedures for transformations while maintaining target table compatibility with downstream systems.

---

## Executive Summary

**Source Environment:**
- Database: Oracle
- ETL Tool: Informatica PowerCenter
- Transformation Logic: Informatica XML mappings

**Target Environment:**
- Database: Snowflake
- Transformation Logic: Snowflake Stored Procedures (SQL/JavaScript)
- Target Schema: Maintained as-is to minimize downstream impact

**Key Challenge:**
- Source table/column names may differ between Oracle and Snowflake
- Need to map Informatica transformations to Snowflake stored procedures
- Maintain data lineage and transformation logic integrity

---

## Core Requirements

### 1. Database Crawling & Metadata Extraction

#### 1.1 Oracle Database Crawler
**Objectives:**
- Connect to Oracle database securely
- Extract complete schema metadata
- Capture sample data for validation

**Required Metadata:**
```
- Schema names
- Table names
- Column definitions (name, data type, length, precision, scale)
- Primary keys
- Foreign keys
- Indexes
- Constraints (NOT NULL, CHECK, UNIQUE)
- Table row counts
- Sample data (configurable rows per table)
- Table/column comments
- Partitioning information
```

**Output Format:**
- JSON metadata file per schema
- CSV exports of sample data
- Data profiling statistics (NULL counts, distinct values, min/max)

#### 1.2 Snowflake Database Crawler
**Objectives:**
- Connect to Snowflake account
- Extract metadata from target/source tables
- Identify available tables for mapping

**Required Metadata:**
```
- Database names
- Schema names
- Table names
- Column definitions
- Clustering keys
- Stage information
- Sample data
- Table statistics (row count, size)
```

**Output Format:**
- JSON metadata file per schema
- CSV sample data exports
- Comparison-ready structure matching Oracle output

### 2. Informatica XML Parser

#### 2.1 XML Structure Analysis
**Parse Informatica Mapping XML to Extract:**

```xml
Key Elements to Parse:
├── Source Definitions
│   ├── Source table names (Oracle)
│   ├── Source columns
│   └── Database connections
│
├── Target Definitions
│   ├── Target table names
│   ├── Target columns
│   └── Load types (INSERT, UPDATE, DELETE)
│
├── Transformations
│   ├── Expression transformations (calculations, data type conversions)
│   ├── Aggregator transformations (GROUP BY, SUM, COUNT, etc.)
│   ├── Filter transformations (WHERE conditions)
│   ├── Joiner transformations (INNER, LEFT, RIGHT, FULL)
│   ├── Lookup transformations (reference data)
│   ├── Router transformations (conditional routing)
│   ├── Sorter transformations (ORDER BY)
│   ├── Union transformations
│   └── Sequence generators
│
├── Mapping Logic
│   ├── Data flow between transformations
│   ├── Port mappings (column-to-column)
│   ├── Expressions and formulas
│   └── Conditional logic
│
└── Session Configuration
    ├── Commit intervals
    ├── Error handling
    └── Performance tuning parameters
```

#### 2.2 Transformation Mapping
**Map Informatica Components to Snowflake SQL:**

| Informatica Transformation | Snowflake Equivalent |
|---------------------------|---------------------|
| Expression | CASE, CAST, Functions |
| Aggregator | GROUP BY, Aggregate Functions |
| Filter | WHERE clause |
| Joiner | JOIN (INNER, LEFT, RIGHT, FULL) |
| Lookup | LEFT JOIN or MERGE |
| Router | CASE WHEN with multiple INSERT |
| Sorter | ORDER BY |
| Union | UNION/UNION ALL |
| Rank | ROW_NUMBER(), RANK(), DENSE_RANK() |
| Update Strategy | MERGE statement |

#### 2.3 Output Requirements
**Generate:**
- Mapping documentation (Markdown/HTML)
- Source-to-target lineage
- Transformation logic summary
- Data flow diagrams (text-based)

### 3. Schema & Column Name Mapping

#### 3.1 Intelligent Mapping Engine
**Challenges:**
- Oracle source table: `STG_CUSTOMER_DATA`
- Snowflake source table: `CUSTOMER_STAGING`
- Target table (same in both): `DIM_CUSTOMER`

**Mapping Strategies:**

1. **Exact Name Match**
   - Direct comparison (case-insensitive)

2. **Fuzzy Matching**
   - Levenshtein distance
   - Phonetic matching (Soundex)
   - Token-based similarity

3. **Pattern Recognition**
   - Common prefixes/suffixes (STG_, _TMP, _HIST)
   - Abbreviation expansion (CUST → CUSTOMER)
   - Separator normalization (_ vs camelCase)

4. **Metadata-Based Matching**
   - Column count similarity
   - Data type pattern matching
   - Primary key alignment
   - Sample data correlation

5. **Manual Override**
   - Configuration file for explicit mappings
   - User interface for review/approval

**Configuration Format:**
```json
{
  "manual_mappings": {
    "oracle_schema.oracle_table": "snowflake_db.snowflake_schema.snowflake_table",
    "STG_CUSTOMER_DATA": "RAW.STAGING.CUSTOMER_DATA"
  },
  "column_mappings": {
    "oracle_schema.oracle_table": {
      "OLD_COL_NAME": "NEW_COL_NAME",
      "CUST_ID": "CUSTOMER_ID"
    }
  },
  "matching_rules": {
    "fuzzy_threshold": 0.85,
    "ignore_prefixes": ["STG_", "TMP_", "HIST_"],
    "ignore_suffixes": ["_BACKUP", "_OLD"]
  }
}
```

### 4. Stored Procedure Generation

#### 4.1 Procedure Structure
**Generated Snowflake Stored Procedure Template:**

```sql
CREATE OR REPLACE PROCEDURE {schema}.SP_{target_table}_LOAD(
    p_load_date DATE,
    p_batch_id VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    v_start_time TIMESTAMP;
    v_rows_inserted INTEGER;
    v_rows_updated INTEGER;
    v_rows_deleted INTEGER;
    v_error_message VARCHAR;
BEGIN
    v_start_time := CURRENT_TIMESTAMP();
    
    -- Log start
    INSERT INTO ETL_METADATA.PROCESS_LOG (...)
    VALUES (...);
    
    -- Transformation logic (generated from Informatica)
    BEGIN TRANSACTION;
    
    -- Main MERGE/INSERT logic
    MERGE INTO {target_schema}.{target_table} tgt
    USING (
        -- SELECT with transformations
        SELECT
            -- Mapped columns with transformations
        FROM {source_schema}.{source_table} src
        -- JOINs, WHERE, GROUP BY from Informatica
    ) src
    ON tgt.{primary_key} = src.{primary_key}
    WHEN MATCHED THEN UPDATE SET ...
    WHEN NOT MATCHED THEN INSERT ...;
    
    GET DIAGNOSTICS v_rows_inserted = ROW_COUNT;
    
    COMMIT;
    
    -- Log completion
    INSERT INTO ETL_METADATA.PROCESS_LOG (...)
    VALUES (...);
    
    RETURN 'SUCCESS: ' || v_rows_inserted || ' rows processed';
    
EXCEPTION
    WHEN OTHER THEN
        v_error_message := SQLERRM;
        ROLLBACK;
        -- Log error
        RETURN 'ERROR: ' || v_error_message;
END;
$$;
```

#### 4.2 Transformation Logic Translation

**Expression Transformation:**
```
Informatica: IIF(ISNULL(SALARY), 0, SALARY * 1.10)
Snowflake:   COALESCE(SALARY, 0) * 1.10
```

**Aggregator Transformation:**
```
Informatica: GROUP BY DEPT_ID, SUM(SALARY)
Snowflake:   GROUP BY DEPT_ID HAVING SUM(SALARY) ...
```

**Lookup Transformation:**
```
Informatica: LKP:PRODUCT_DIM(PRODUCT_ID)
Snowflake:   LEFT JOIN DIM_PRODUCT p ON src.PRODUCT_ID = p.PRODUCT_ID
```

#### 4.3 Error Handling & Logging
**Include in Each Procedure:**
- Try-catch blocks
- Transaction management
- Audit trail insertion
- Row count validation
- Data quality checks
- Performance metrics logging

### 5. Utility Components Architecture

```
dw_migration_utility/
│
├── config/
│   ├── oracle_connection.json
│   ├── snowflake_connection.json
│   ├── mapping_rules.json
│   └── transformation_patterns.json
│
├── crawlers/
│   ├── __init__.py
│   ├── oracle_crawler.py          # Oracle metadata extraction
│   ├── snowflake_crawler.py       # Snowflake metadata extraction
│   └── metadata_models.py         # Data models for metadata
│
├── parsers/
│   ├── __init__.py
│   ├── informatica_xml_parser.py  # Parse Informatica XML
│   ├── transformation_mapper.py   # Map transformations
│   └── lineage_tracker.py         # Track data lineage
│
├── mappers/
│   ├── __init__.py
│   ├── schema_mapper.py           # Schema/table mapping logic
│   ├── column_mapper.py           # Column-level mapping
│   ├── fuzzy_matcher.py           # Fuzzy matching algorithms
│   └── manual_mapper.py           # Handle manual overrides
│
├── generators/
│   ├── __init__.py
│   ├── stored_proc_generator.py   # Generate Snowflake SPs
│   ├── sql_translator.py          # Translate SQL/expressions
│   └── template_engine.py         # SP template management
│
├── validators/
│   ├── __init__.py
│   ├── data_validator.py          # Compare source vs target
│   ├── count_validator.py         # Row count validation
│   └── quality_checker.py         # Data quality checks
│
├── utils/
│   ├── __init__.py
│   ├── db_connector.py            # Database connections
│   ├── logger.py                  # Logging utility
│   ├── config_loader.py           # Configuration management
│   └── report_generator.py        # Generate migration reports
│
├── output/
│   ├── metadata/                  # JSON metadata files
│   ├── stored_procedures/         # Generated SP SQL files
│   ├── mapping_docs/              # Mapping documentation
│   ├── validation_reports/        # Validation results
│   └── logs/                      # Execution logs
│
├── tests/
│   ├── test_crawlers.py
│   ├── test_parsers.py
│   ├── test_mappers.py
│   └── test_generators.py
│
├── main.py                        # Main execution script
├── requirements.txt               # Python dependencies
└── README.md                      # Documentation
```

### 6. Execution Workflow

```
Step 1: Configuration
├── Set up database connections
├── Load mapping rules
└── Configure output directories

Step 2: Metadata Extraction
├── Crawl Oracle database
│   ├── Extract all schemas
│   ├── Extract table metadata
│   └── Collect sample data
├── Crawl Snowflake database
│   ├── Extract all databases/schemas
│   ├── Extract table metadata
│   └── Collect sample data
└── Generate metadata JSON files

Step 3: Informatica Parsing
├── Load Informatica XML files
├── Parse source definitions
├── Parse target definitions
├── Parse transformation logic
└── Generate lineage documentation

Step 4: Mapping Generation
├── Match Oracle → Snowflake source tables
│   ├── Apply exact matching
│   ├── Apply fuzzy matching
│   └── Flag unmapped tables
├── Match columns within tables
├── Apply manual overrides
└── Generate mapping report

Step 5: Stored Procedure Generation
├── For each Informatica mapping:
│   ├── Identify new Snowflake source table
│   ├── Translate transformation logic
│   ├── Generate MERGE/INSERT SQL
│   ├── Add error handling
│   ├── Add logging
│   └── Create SP file
└── Generate deployment script

Step 6: Validation
├── Deploy stored procedures (optional)
├── Execute validation queries
├── Compare row counts
├── Sample data comparison
└── Generate validation report

Step 7: Documentation
├── Generate migration summary
├── Create lineage diagrams
├── Document unmapped objects
└── Create runbook for deployment
```

### 7. Key Features

#### 7.1 Command-Line Interface
```bash
# Full migration workflow
python main.py --mode full --config config/migration_config.json

# Individual steps
python main.py --mode crawl --database oracle
python main.py --mode crawl --database snowflake
python main.py --mode parse --informatica-xml path/to/xml
python main.py --mode map --auto-match --fuzzy-threshold 0.85
python main.py --mode generate --output output/stored_procedures/
python main.py --mode validate --source oracle --target snowflake

# Interactive mode
python main.py --interactive
```

#### 7.2 Configuration Management
**migration_config.json:**
```json
{
  "oracle": {
    "host": "oracle-prod.company.com",
    "port": 1521,
    "service_name": "DWPROD",
    "username": "${ORACLE_USER}",
    "password": "${ORACLE_PASSWORD}",
    "schemas": ["DW_STAGE", "DW_CORE", "DW_MARTS"]
  },
  "snowflake": {
    "account": "company.us-east-1",
    "warehouse": "MIGRATION_WH",
    "database": "DW_PROD",
    "schema": "PUBLIC",
    "username": "${SNOWFLAKE_USER}",
    "password": "${SNOWFLAKE_PASSWORD}",
    "role": "SYSADMIN"
  },
  "informatica": {
    "xml_directory": "/path/to/informatica/exports",
    "file_pattern": "*.xml"
  },
  "mapping": {
    "auto_match": true,
    "fuzzy_threshold": 0.85,
    "manual_mapping_file": "config/manual_mappings.json",
    "ignore_prefixes": ["STG_", "TMP_"],
    "ignore_suffixes": ["_BACKUP", "_OLD"]
  },
  "generation": {
    "output_directory": "output/stored_procedures",
    "include_logging": true,
    "include_error_handling": true,
    "transaction_mode": "auto",
    "naming_convention": "SP_{TABLE}_LOAD"
  },
  "validation": {
    "sample_size": 1000,
    "row_count_check": true,
    "data_comparison": true,
    "null_check": true
  }
}
```

#### 7.3 Sample Data Collection
**Configurable sampling strategies:**
- Random sampling (n rows)
- Top N rows
- Stratified sampling (by date/category)
- Statistical profiling (min, max, distinct count, null count)

#### 7.4 Reporting & Documentation
**Generated Reports:**
1. **Migration Summary Report**
   - Total tables processed
   - Successful mappings
   - Failed mappings
   - Manual intervention required

2. **Mapping Documentation**
   - Source → Target table mapping
   - Column-level lineage
   - Transformation logic summary

3. **Validation Report**
   - Row count comparison
   - Data quality metrics
   - Failed validations
   - Recommendations

4. **Stored Procedure Documentation**
   - Procedure name
   - Input parameters
   - Transformation logic
   - Dependencies
   - Execution order

### 8. Technical Specifications

#### 8.1 Required Python Libraries
```
# Database connectivity
cx_Oracle==8.3.0
snowflake-connector-python==3.0.0
snowflake-sqlalchemy==1.4.0

# Data processing
pandas==2.0.0
numpy==1.24.0

# XML parsing
lxml==4.9.0
xmltodict==0.13.0

# String matching
fuzzywuzzy==0.18.0
python-Levenshtein==0.21.0

# Configuration
pyyaml==6.0
python-dotenv==1.0.0

# Reporting
jinja2==3.1.2
markdown==3.4.0

# Logging
loguru==0.7.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
```

#### 8.2 Performance Considerations
- Parallel processing for multiple tables
- Batch processing for large datasets
- Connection pooling
- Configurable memory limits
- Progress indicators for long operations

#### 8.3 Security Requirements
- Encrypted credential storage
- Environment variable support
- No hardcoded passwords
- Audit logging
- Role-based access control awareness

### 9. Deliverables

1. **Python Utility Package**
   - Fully functional migration utility
   - Comprehensive error handling
   - Unit tests (>80% coverage)

2. **Documentation**
   - User guide
   - API documentation
   - Configuration guide
   - Troubleshooting guide

3. **Sample Outputs**
   - Example stored procedures
   - Sample mapping reports
   - Validation report templates

4. **Deployment Scripts**
   - SQL scripts for Snowflake setup
   - Bash/PowerShell deployment scripts
   - Docker containerization (optional)

### 10. Success Criteria

- ✅ Successfully crawl and extract metadata from Oracle and Snowflake
- ✅ Parse Informatica XML and extract all transformation logic
- ✅ Achieve >90% automatic mapping rate for tables
- ✅ Generate syntactically correct Snowflake stored procedures
- ✅ Validate data accuracy within acceptable tolerance (99.9%)
- ✅ Complete migration documentation with full lineage
- ✅ Execution time: <10 minutes for 100 tables
- ✅ Zero data loss during migration

### 11. Future Enhancements

- Web-based UI for mapping management
- Real-time migration monitoring dashboard
- Support for incremental updates
- Integration with data catalog tools
- CI/CD pipeline integration
- Support for additional sources (SQL Server, Teradata)
- Machine learning for improved mapping accuracy
- Version control integration for stored procedures

---

## Quick Start Example

```python
from dw_migration_utility import MigrationOrchestrator

# Initialize
orchestrator = MigrationOrchestrator(config_file='config/migration_config.json')

# Run full migration
orchestrator.run_full_migration(
    crawl_oracle=True,
    crawl_snowflake=True,
    parse_informatica=True,
    generate_mappings=True,
    generate_procedures=True,
    validate=True
)

# Get results
summary = orchestrator.get_summary()
print(f"Tables mapped: {summary['mapped_tables']}/{summary['total_tables']}")
print(f"Procedures generated: {summary['procedures_generated']}")
print(f"Validation status: {summary['validation_status']}")
```

---

## Contact & Support

For questions or issues with this utility, please contact the data engineering team.

**Document Version:** 1.0  
**Last Updated:** 2025-11-16  
**Author:** Migration Team
