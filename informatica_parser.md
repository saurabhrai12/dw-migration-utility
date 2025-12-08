# Data Warehouse Documentation Generator

## Project Overview

Build a Python utility to analyze and document an existing Oracle/Informatica-based data warehouse. The utility will parse Informatica mapping and workflow XML files along with Oracle database objects to generate comprehensive documentation of source-to-target data flows, transformation logic, and business rules.

---

## Objectives

1. Parse Informatica PowerCenter XML files (mappings and workflows)
2. Extract Oracle database metadata (stored procedures, views, packages, tables)
3. Generate comprehensive documentation showing:
   - Source → Target table mappings
   - Column-level transformations and expressions
   - Lookup logic and reference data
   - Aggregations, filters, and joins
   - Data lineage from source to target
4. Output documentation in multiple formats (Markdown, HTML, JSON)

---

## Project Structure

```
dw_documentation/
├── main.py                      # CLI entry point
├── config/
│   └── config.yaml              # Configuration file
├── parsers/
│   ├── __init__.py
│   ├── informatica_mapping.py   # Parse Informatica mapping XML
│   ├── informatica_workflow.py  # Parse Informatica workflow XML
│   └── xml_utils.py             # Common XML utilities
├── extractors/
│   ├── __init__.py
│   ├── oracle_extractor.py      # Extract Oracle metadata
│   ├── procedure_parser.py      # Parse PL/SQL procedures
│   └── view_parser.py           # Parse Oracle views
├── models/
│   ├── __init__.py
│   ├── mapping.py               # Data models for mappings
│   ├── transformation.py        # Transformation models
│   └── lineage.py               # Lineage tracking models
├── generators/
│   ├── __init__.py
│   ├── markdown_generator.py    # Generate Markdown docs
│   ├── html_generator.py        # Generate HTML docs
│   ├── json_exporter.py         # Export to JSON
│   └── diagram_generator.py     # Generate data flow diagrams
├── templates/
│   ├── mapping_template.md
│   ├── lineage_template.md
│   └── data_dictionary.md
├── output/                      # Generated documentation
├── requirements.txt
└── README.md
```

---

## Core Requirements

### 1. Informatica Mapping XML Parser

#### 1.1 Input
- Informatica PowerCenter mapping XML files (`.xml`)
- Location: Configurable directory path

#### 1.2 XML Elements to Parse

**REPOSITORY > FOLDER > MAPPING**
```xml
<MAPPING NAME="m_load_customer" DESCRIPTION="Load customer dimension">
```

**SOURCE (Source Definition)**
```xml
<SOURCE NAME="CUSTOMER_STG" DBDNAME="ORACLE" OWNERNAME="STG_SCHEMA">
    <SOURCEFIELD NAME="CUST_ID" DATATYPE="number" PRECISION="10"/>
    <SOURCEFIELD NAME="CUST_NAME" DATATYPE="string" PRECISION="100"/>
</SOURCE>
```
Extract:
- Source table name, schema, database type
- All source columns with data types, precision, scale
- Primary keys if defined

**TARGET (Target Definition)**
```xml
<TARGET NAME="DIM_CUSTOMER" DATABASETYPE="Oracle" OWNERNAME="DW_SCHEMA">
    <TARGETFIELD NAME="CUSTOMER_KEY" DATATYPE="number" KEYTYPE="PRIMARY KEY"/>
    <TARGETFIELD NAME="CUSTOMER_ID" DATATYPE="number"/>
</TARGET>
```
Extract:
- Target table name, schema, database type
- All target columns with data types
- Primary/foreign key definitions

**TRANSFORMATION (All Types)**

Parse ALL transformation types:

```xml
<!-- Source Qualifier -->
<TRANSFORMATION NAME="SQ_CUSTOMER" TYPE="Source Qualifier">
    <TRANSFORMFIELD NAME="CUST_ID" PORTTYPE="INPUT/OUTPUT"/>
    <TABLEATTRIBUTE NAME="Sql Query" VALUE="SELECT * FROM CUSTOMER WHERE STATUS='A'"/>
</TRANSFORMATION>

<!-- Expression -->
<TRANSFORMATION NAME="EXP_CALC" TYPE="Expression">
    <TRANSFORMFIELD NAME="OUT_FULL_NAME" EXPRESSION="UPPER(FIRST_NAME) || ' ' || UPPER(LAST_NAME)"/>
    <TRANSFORMFIELD NAME="OUT_STATUS_DESC" EXPRESSION="IIF(STATUS='A','Active','Inactive')"/>
</TRANSFORMATION>

<!-- Lookup -->
<TRANSFORMATION NAME="LKP_REGION" TYPE="Lookup Procedure">
    <TRANSFORMFIELD NAME="REGION_NAME" PORTTYPE="OUTPUT"/>
    <TABLEATTRIBUTE NAME="Lookup Sql Override" VALUE="SELECT REGION_ID, REGION_NAME FROM DIM_REGION"/>
    <TABLEATTRIBUTE NAME="Lookup condition" VALUE="REGION_ID = IN_REGION_ID"/>
</TRANSFORMATION>

<!-- Filter -->
<TRANSFORMATION NAME="FIL_ACTIVE" TYPE="Filter">
    <TABLEATTRIBUTE NAME="Filter Condition" VALUE="STATUS_FLAG = 'Y' AND EFF_DATE <= SYSDATE"/>
</TRANSFORMATION>

<!-- Aggregator -->
<TRANSFORMATION NAME="AGG_SALES" TYPE="Aggregator">
    <TRANSFORMFIELD NAME="CUST_ID" PORTTYPE="INPUT/OUTPUT" EXPRESSIONTYPE="GROUPBY"/>
    <TRANSFORMFIELD NAME="TOTAL_SALES" EXPRESSION="SUM(SALE_AMT)" PORTTYPE="OUTPUT"/>
</TRANSFORMFIELD>

<!-- Joiner -->
<TRANSFORMATION NAME="JNR_CUST_ADDR" TYPE="Joiner">
    <TABLEATTRIBUTE NAME="Join Condition" VALUE="CUST_ID = CUST_ID1"/>
    <TABLEATTRIBUTE NAME="Join Type" VALUE="Normal Join"/>
</TRANSFORMATION>

<!-- Router -->
<TRANSFORMATION NAME="RTR_BY_REGION" TYPE="Router">
    <GROUP NAME="NORTH" EXPRESSION="REGION='NORTH'"/>
    <GROUP NAME="SOUTH" EXPRESSION="REGION='SOUTH'"/>
</TRANSFORMATION>

<!-- Sequence Generator -->
<TRANSFORMATION NAME="SEQ_CUST_KEY" TYPE="Sequence Generator">
    <TABLEATTRIBUTE NAME="Start Value" VALUE="1"/>
    <TABLEATTRIBUTE NAME="Increment By" VALUE="1"/>
</TRANSFORMATION>

<!-- Update Strategy -->
<TRANSFORMATION NAME="UPD_CUSTOMER" TYPE="Update Strategy">
    <TABLEATTRIBUTE NAME="Update Strategy Expression" VALUE="IIF(ISNULL(EXISTING_KEY), DD_INSERT, DD_UPDATE)"/>
</TRANSFORMATION>

<!-- Stored Procedure -->
<TRANSFORMATION NAME="SP_VALIDATE" TYPE="Stored Procedure">
    <TABLEATTRIBUTE NAME="Stored Procedure Name" VALUE="PKG_VALIDATION.VALIDATE_CUSTOMER"/>
</TRANSFORMATION>
```

**CONNECTOR (Data Flow)**
```xml
<CONNECTOR FROMINSTANCE="SQ_CUSTOMER" FROMFIELD="CUST_ID" 
           TOINSTANCE="EXP_CALC" TOFIELD="IN_CUST_ID"/>
```
Extract:
- Complete data flow from source to target
- Port-to-port connections
- Build lineage graph

**MAPPLET (Reusable Transformations)**
```xml
<MAPPLET NAME="mplt_date_dimension">
    <TRANSFORMATION.../>
</MAPPLET>
```

#### 1.3 Output Data Structure

```python
@dataclass
class InformaticaMapping:
    name: str
    description: str
    folder: str
    sources: List[SourceDefinition]
    targets: List[TargetDefinition]
    transformations: List[Transformation]
    connectors: List[Connector]
    mapplets: List[str]  # Referenced mapplet names

@dataclass
class SourceDefinition:
    name: str
    schema: str
    database_type: str
    fields: List[FieldDefinition]
    sql_override: Optional[str]

@dataclass
class TargetDefinition:
    name: str
    schema: str
    database_type: str
    fields: List[FieldDefinition]
    target_load_type: str  # Insert/Update/Delete

@dataclass
class Transformation:
    name: str
    type: str  # Expression, Lookup, Filter, Aggregator, etc.
    fields: List[TransformField]
    properties: Dict[str, str]  # Type-specific properties
    expressions: Dict[str, str]  # Field -> Expression mapping
    conditions: List[str]  # Filter/Join conditions

@dataclass
class TransformField:
    name: str
    datatype: str
    port_type: str  # INPUT, OUTPUT, INPUT/OUTPUT
    expression: Optional[str]
    default_value: Optional[str]

@dataclass
class Connector:
    from_instance: str
    from_field: str
    to_instance: str
    to_field: str
```

---

### 2. Informatica Workflow XML Parser

#### 2.1 Input
- Informatica workflow XML files (`.xml`)

#### 2.2 XML Elements to Parse

**WORKFLOW**
```xml
<WORKFLOW NAME="wf_daily_customer_load" DESCRIPTION="Daily customer dimension load">
```

**SESSION**
```xml
<SESSION NAME="s_m_load_customer" MAPPINGNAME="m_load_customer">
    <SESSIONEXTENSION NAME="Relational Writer">
        <CONNECTIONREFERENCE CONNECTIONNAME="ORACLE_DW"/>
    </SESSIONEXTENSION>
    <ATTRIBUTE NAME="Parameter Filename" VALUE="$PMRootDir/param/customer.par"/>
</SESSION>
```
Extract:
- Session to mapping association
- Connection references
- Parameter files
- Session properties (commit interval, error handling)

**TASK (Commands, Emails, etc.)**
```xml
<TASK NAME="CMD_PRE_LOAD" TYPE="Command">
    <ATTRIBUTE NAME="Command" VALUE="sh $PMRootDir/scripts/pre_load.sh"/>
</TASK>
```

**WORKLET (Sub-workflows)**
```xml
<WORKLET NAME="wklt_error_handling">
```

**TASKINSTANCE and LINK (Execution Order)**
```xml
<TASKINSTANCE NAME="Start" TASKTYPE="Start"/>
<TASKINSTANCE NAME="s_m_load_customer" TASKTYPE="Session"/>
<LINK FROMTASK="Start" TOTASK="s_m_load_customer" CONDITION=""/>
<LINK FROMTASK="s_m_load_customer" TOTASK="s_m_load_orders" CONDITION="$s_m_load_customer.Status = SUCCEEDED"/>
```

#### 2.3 Output Data Structure

```python
@dataclass
class InformaticaWorkflow:
    name: str
    description: str
    folder: str
    sessions: List[WorkflowSession]
    tasks: List[WorkflowTask]
    execution_order: List[TaskLink]  # DAG of task execution

@dataclass
class WorkflowSession:
    name: str
    mapping_name: str
    source_connection: str
    target_connection: str
    parameter_file: Optional[str]
    properties: Dict[str, str]

@dataclass
class TaskLink:
    from_task: str
    to_task: str
    condition: str
    link_type: str  # Success, Failure, Conditional
```

---

### 3. Oracle Database Extractor

#### 3.1 Connection
- Use `oracledb` (formerly cx_Oracle) for database connection
- Support connection via TNS, Easy Connect, or connection string
- Handle connection pooling for large extractions

#### 3.2 Objects to Extract

**Tables and Columns**
```sql
-- Tables
SELECT owner, table_name, num_rows, last_analyzed
FROM all_tables WHERE owner IN (:schemas);

-- Columns
SELECT owner, table_name, column_name, data_type, 
       data_length, data_precision, data_scale, nullable
FROM all_tab_columns WHERE owner IN (:schemas);

-- Primary Keys
SELECT acc.owner, acc.table_name, acc.column_name, ac.constraint_name
FROM all_cons_columns acc
JOIN all_constraints ac ON acc.constraint_name = ac.constraint_name
WHERE ac.constraint_type = 'P' AND acc.owner IN (:schemas);

-- Foreign Keys
SELECT ac.owner, ac.table_name, ac.constraint_name,
       acc.column_name, ac.r_constraint_name,
       rc.table_name as ref_table
FROM all_constraints ac
JOIN all_cons_columns acc ON ac.constraint_name = acc.constraint_name
JOIN all_constraints rc ON ac.r_constraint_name = rc.constraint_name
WHERE ac.constraint_type = 'R' AND ac.owner IN (:schemas);
```

**Stored Procedures and Packages**
```sql
-- Procedures/Functions/Packages
SELECT owner, object_name, object_type, created, last_ddl_time
FROM all_objects 
WHERE object_type IN ('PROCEDURE', 'FUNCTION', 'PACKAGE', 'PACKAGE BODY')
AND owner IN (:schemas);

-- Source Code
SELECT owner, name, type, line, text
FROM all_source
WHERE owner IN (:schemas)
ORDER BY owner, name, type, line;
```

**Views**
```sql
-- Views
SELECT owner, view_name, text_length
FROM all_views WHERE owner IN (:schemas);

-- View Source
SELECT owner, view_name, text
FROM all_views WHERE owner IN (:schemas);
```

**Synonyms**
```sql
SELECT owner, synonym_name, table_owner, table_name, db_link
FROM all_synonyms WHERE owner IN (:schemas);
```

#### 3.3 PL/SQL Parser

Parse stored procedure/function source code to extract:

```python
@dataclass
class OracleProcedure:
    owner: str
    name: str
    type: str  # PROCEDURE, FUNCTION, PACKAGE
    parameters: List[ProcedureParameter]
    local_variables: List[Variable]
    sql_statements: List[SQLStatement]
    called_procedures: List[str]
    tables_referenced: List[TableReference]
    source_code: str

@dataclass
class ProcedureParameter:
    name: str
    direction: str  # IN, OUT, IN OUT
    data_type: str
    default_value: Optional[str]

@dataclass
class SQLStatement:
    statement_type: str  # SELECT, INSERT, UPDATE, DELETE, MERGE
    target_table: Optional[str]
    source_tables: List[str]
    where_clause: Optional[str]
    join_conditions: List[str]

@dataclass
class TableReference:
    schema: str
    table_name: str
    alias: Optional[str]
    operation: str  # SELECT, INSERT, UPDATE, DELETE
```

**Parsing Requirements:**
- Extract INSERT/UPDATE/DELETE/MERGE statements
- Identify source tables in SELECT and subqueries
- Parse CURSOR definitions and their queries
- Extract MERGE statement source and target
- Handle dynamic SQL (EXECUTE IMMEDIATE) - flag for manual review
- Identify called procedures/functions

#### 3.4 View Parser

```python
@dataclass
class OracleView:
    owner: str
    name: str
    source_tables: List[TableReference]
    columns: List[ViewColumn]
    where_clause: Optional[str]
    joins: List[JoinDefinition]
    source_sql: str

@dataclass
class ViewColumn:
    name: str
    expression: str  # Could be column name or calculation
    source_table: Optional[str]
    source_column: Optional[str]
```

---

### 4. Data Lineage Builder

#### 4.1 Lineage Model

```python
@dataclass
class ColumnLineage:
    target_table: str
    target_column: str
    source_table: str
    source_column: str
    transformation_chain: List[TransformationStep]
    expression: Optional[str]

@dataclass
class TransformationStep:
    step_order: int
    transformation_name: str
    transformation_type: str
    input_fields: List[str]
    output_field: str
    expression: Optional[str]

@dataclass
class TableLineage:
    target_table: str
    source_tables: List[str]
    mapping_name: str
    workflow_name: Optional[str]
    load_type: str  # Full, Incremental
    filter_conditions: List[str]
```

#### 4.2 Lineage Traversal

Build a graph traversing:
1. Informatica CONNECTOR elements (port-to-port flow)
2. Transformation expressions (input → output)
3. Lookup source tables
4. Oracle procedure SQL statements

---

### 5. Documentation Generator

#### 5.1 Markdown Output

**Per-Mapping Documentation:**
```markdown
# Mapping: m_load_customer

## Overview
| Property | Value |
|----------|-------|
| Folder | CUSTOMER_LOAD |
| Description | Load customer dimension from staging |
| Workflow | wf_daily_customer_load |

## Source Tables
| Table | Schema | Database | Row Filter |
|-------|--------|----------|------------|
| CUSTOMER_STG | STG | Oracle | STATUS = 'A' |

## Target Tables
| Table | Schema | Load Type |
|-------|--------|-----------|
| DIM_CUSTOMER | DW | Upsert |

## Transformations

### Expression: EXP_CUSTOMER_CALC
| Output Port | Expression | Description |
|-------------|------------|-------------|
| OUT_FULL_NAME | UPPER(FIRST_NAME) \|\| ' ' \|\| UPPER(LAST_NAME) | Concatenate name |
| OUT_STATUS | IIF(STATUS='A', 'Active', 'Inactive') | Decode status |

### Lookup: LKP_REGION
| Lookup Table | Condition | Return Ports |
|--------------|-----------|--------------|
| DIM_REGION | REGION_ID = IN_REGION_ID | REGION_NAME |

### Filter: FIL_VALID_RECORDS
**Condition:** `VALID_FLAG = 'Y' AND EFF_DATE <= SYSDATE`

## Column Lineage
| Target Column | Source | Transformation |
|---------------|--------|----------------|
| CUSTOMER_KEY | SEQ_CUST_KEY.NEXTVAL | Sequence Generator |
| CUSTOMER_NAME | CUSTOMER_STG.FIRST_NAME, LAST_NAME | EXP: UPPER concatenation |
| REGION_NAME | DIM_REGION.REGION_NAME | Lookup on REGION_ID |

## Data Flow Diagram
```
[CUSTOMER_STG] → [SQ_CUSTOMER] → [EXP_CUSTOMER_CALC] → [LKP_REGION] → [FIL_VALID] → [DIM_CUSTOMER]
```
```

**Data Dictionary:**
```markdown
# Data Dictionary: DIM_CUSTOMER

## Table Information
| Property | Value |
|----------|-------|
| Schema | DW_SCHEMA |
| Type | Dimension |
| Load Frequency | Daily |
| Source System | CRM |

## Columns
| Column | Data Type | Nullable | Description | Source |
|--------|-----------|----------|-------------|--------|
| CUSTOMER_KEY | NUMBER(10) | NOT NULL | Surrogate Key | Sequence |
| CUSTOMER_ID | NUMBER(10) | NOT NULL | Natural Key | CRM.CUSTOMER.ID |
| CUSTOMER_NAME | VARCHAR2(200) | NOT NULL | Full Name | Derived |
```

**Master Lineage Report:**
```markdown
# Source to Target Lineage Matrix

## Summary
- Total Mappings: 45
- Total Source Tables: 23
- Total Target Tables: 18
- Total Transformations: 156

## Lineage by Target Table

### DIM_CUSTOMER
| Source Table | Mapping | Columns Mapped |
|--------------|---------|----------------|
| CUSTOMER_STG | m_load_customer | 15 |
| CUSTOMER_ADDR | m_load_customer | 5 |

### FACT_SALES
| Source Table | Mapping | Columns Mapped |
|--------------|---------|----------------|
| SALES_TRANS | m_load_sales | 12 |
| DIM_PRODUCT | m_load_sales (lookup) | 3 |
```

#### 5.2 HTML Output
- Generate navigable HTML with cross-references
- Include collapsible sections for large mappings
- Add search functionality
- Generate interactive lineage diagrams (using Mermaid.js or D3.js)

#### 5.3 JSON Export
```json
{
  "mappings": [
    {
      "name": "m_load_customer",
      "folder": "CUSTOMER_LOAD",
      "sources": [...],
      "targets": [...],
      "transformations": [...],
      "lineage": [...]
    }
  ],
  "oracle_objects": {
    "procedures": [...],
    "views": [...],
    "tables": [...]
  },
  "lineage_graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

---

### 6. Configuration

**config.yaml:**
```yaml
# Informatica Configuration
informatica:
  mapping_directory: "/path/to/informatica/mappings"
  workflow_directory: "/path/to/informatica/workflows"
  file_patterns:
    mappings: "*.xml"
    workflows: "wf_*.xml"
  exclude_folders:
    - "Archive"
    - "Test"

# Oracle Configuration
oracle:
  connection:
    method: "tns"  # tns, easy_connect, connection_string
    tns_name: "DWPROD"
    # OR
    # host: "oracle-server.company.com"
    # port: 1521
    # service_name: "DWPROD"
  credentials:
    username: "${ORACLE_USER}"  # Environment variable
    password: "${ORACLE_PASSWORD}"
  schemas:
    - "STG_SCHEMA"
    - "DW_SCHEMA"
    - "ETL_SCHEMA"
  exclude_objects:
    - pattern: "*_BAK"
    - pattern: "*_OLD"
    - pattern: "TMP_*"

# Output Configuration
output:
  directory: "./output"
  formats:
    - markdown
    - html
    - json
  include_source_code: true
  include_sample_data: false
  diagram_format: "mermaid"  # mermaid, graphviz

# Logging
logging:
  level: "INFO"
  file: "documentation.log"
```

---

### 7. CLI Interface

```bash
# Full documentation generation
python main.py generate --config config.yaml

# Parse only Informatica XMLs
python main.py parse-informatica --mapping-dir /path/to/mappings --output ./output

# Extract only Oracle metadata
python main.py extract-oracle --config config.yaml --schemas DW_SCHEMA,STG_SCHEMA

# Generate lineage for specific mapping
python main.py lineage --mapping m_load_customer --output lineage_report.md

# Generate data dictionary
python main.py data-dictionary --config config.yaml --output data_dict.md

# Export to JSON
python main.py export --format json --output dw_metadata.json

# Interactive mode
python main.py interactive
```

**CLI Arguments:**
```python
@click.group()
def cli():
    """Data Warehouse Documentation Generator"""
    pass

@cli.command()
@click.option('--config', '-c', required=True, help='Configuration file path')
@click.option('--output', '-o', default='./output', help='Output directory')
@click.option('--format', '-f', multiple=True, default=['markdown'], 
              type=click.Choice(['markdown', 'html', 'json']))
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generate(config, output, format, verbose):
    """Generate complete documentation"""
    pass
```

---

### 8. Technical Specifications

#### 8.1 Dependencies

```
# requirements.txt
oracledb>=2.0.0          # Oracle database connectivity
lxml>=4.9.0              # XML parsing
pyyaml>=6.0              # Configuration
click>=8.0.0             # CLI framework
jinja2>=3.0.0            # Template engine
networkx>=3.0            # Graph operations for lineage
sqlparse>=0.4.0          # SQL parsing
graphviz>=0.20           # Diagram generation (optional)
rich>=13.0.0             # Console output formatting
pandas>=2.0.0            # Data manipulation
tqdm>=4.65.0             # Progress bars
```

#### 8.2 Error Handling

- Log all parsing errors with file/line context
- Continue processing on non-fatal errors
- Generate error report with unparsed elements
- Handle malformed XML gracefully
- Timeout on long-running Oracle queries

#### 8.3 Performance

- Use connection pooling for Oracle
- Stream large XML files (don't load entirely in memory)
- Parallel processing for multiple files
- Cache Oracle metadata queries
- Progress indicators for long operations

---

### 9. Sample Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Documentation Generation Flow                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Config    │───▶│   Parse     │───▶│   Extract   │───▶│   Build     │  │
│  │   Loader    │    │ Informatica │    │   Oracle    │    │  Lineage    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        │                   │                   │                   │        │
│        ▼                   ▼                   ▼                   ▼        │
│  • Load YAML         • Mapping XML      • Tables/Cols      • Connect       │
│  • Validate          • Workflow XML     • Procedures       • Source→Target │
│  • Env vars          • Extract all      • Views            • Expressions   │
│                                         • Packages                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │                         Generate Documentation                       │   │
│  │                                                                      │   │
│  │   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐    │   │
│  │   │  Mapping  │   │   Data    │   │  Lineage  │   │ Workflow  │    │   │
│  │   │   Docs    │   │Dictionary │   │  Reports  │   │   Docs    │    │   │
│  │   └───────────┘   └───────────┘   └───────────┘   └───────────┘    │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                              OUTPUT FORMATS                                 │
│                     ┌──────────┬──────────┬──────────┐                     │
│                     │ Markdown │   HTML   │   JSON   │                     │
│                     └──────────┴──────────┴──────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 10. Validation Checklist

After generating documentation, validate:

- [ ] All mappings parsed without errors
- [ ] All source/target tables identified
- [ ] All transformations captured with expressions
- [ ] Lineage traces complete (source to target)
- [ ] Oracle procedures extracted with SQL statements
- [ ] Cross-references work in HTML output
- [ ] No orphaned tables (sources without targets)
- [ ] All lookup tables documented
- [ ] Workflow execution order captured

---

### 11. Deliverables

1. **Per-Mapping Documentation** - One file per Informatica mapping
2. **Workflow Documentation** - Execution order and dependencies
3. **Data Dictionary** - Complete table/column reference
4. **Lineage Matrix** - Source to target mapping grid
5. **Transformation Catalog** - All expressions and business rules
6. **Oracle Object Reference** - Procedures, views, packages
7. **Summary Dashboard** - High-level metrics and statistics
8. **JSON Export** - Machine-readable metadata for other tools

---

## Quick Start

```bash
# 1. Clone and setup
cd dw_documentation
pip install -r requirements.txt

# 2. Configure
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your paths and credentials

# 3. Set Oracle credentials
export ORACLE_USER=your_username
export ORACLE_PASSWORD=your_password

# 4. Run documentation generation
python main.py generate --config config/config.yaml --output ./output

# 5. View results
open output/index.html
```

---

## Part 2: Snowflake Migration & Stored Procedure Generation

### 12. Migration Overview

The utility will also generate Snowflake stored procedures that replicate Informatica transformation logic. Key principles:

- **Target tables remain unchanged** - Same schema, table names, column names, data types (for downstream compatibility)
- **Source tables are mapped** - Oracle sources → Snowflake sources (different names/schemas possible)
- **Transformation logic converted** - Informatica expressions → Snowflake SQL/JavaScript

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Migration Flow                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ORACLE/INFORMATICA (Current)              SNOWFLAKE (Target)              │
│   ─────────────────────────────             ────────────────────            │
│                                                                             │
│   ┌─────────────┐                           ┌─────────────┐                 │
│   │ STG.CUST_   │    Source Mapping         │ RAW.CUSTOMER│                 │
│   │ STAGING     │ ──────────────────────▶   │ _LANDING    │                 │
│   └─────────────┘    (Names Change)         └─────────────┘                 │
│         │                                          │                        │
│         ▼                                          ▼                        │
│   ┌─────────────┐                           ┌─────────────┐                 │
│   │ Informatica │    Logic Converted        │ Snowflake   │                 │
│   │ Mapping     │ ──────────────────────▶   │ Stored Proc │                 │
│   └─────────────┘                           └─────────────┘                 │
│         │                                          │                        │
│         ▼                                          ▼                        │
│   ┌─────────────┐                           ┌─────────────┐                 │
│   │ DW.DIM_     │    Target Unchanged       │ DW.DIM_     │                 │
│   │ CUSTOMER    │ ═════════════════════▶    │ CUSTOMER    │                 │
│   └─────────────┘    (Same Structure)       └─────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 13. Source Mapping Configuration

#### 13.1 Mapping File Structure

**source_mapping.yaml:**
```yaml
# Global Settings
mapping_version: "1.0"
created_date: "2025-01-15"
author: "Migration Team"

# Default schema mappings (fallback if table not explicitly mapped)
default_schema_mapping:
  oracle_to_snowflake:
    "STG_SCHEMA": "RAW"
    "ODS_SCHEMA": "STAGING"
    "DW_SCHEMA": "DW"

# Explicit table mappings (Oracle Source → Snowflake Source)
table_mappings:
  - oracle:
      schema: "STG_SCHEMA"
      table: "CUSTOMER_STG"
    snowflake:
      database: "LANDING_DB"
      schema: "RAW"
      table: "CUSTOMER_LANDING"
    column_mappings:
      - oracle_column: "CUST_ID"
        snowflake_column: "CUSTOMER_ID"
      - oracle_column: "CUST_NM"
        snowflake_column: "CUSTOMER_NAME"
      - oracle_column: "CUST_ADDR1"
        snowflake_column: "ADDRESS_LINE_1"
      # Columns not listed = same name assumed

  - oracle:
      schema: "STG_SCHEMA"
      table: "ORDER_STG"
    snowflake:
      database: "LANDING_DB"
      schema: "RAW"
      table: "ORDERS_STREAM"
    column_mappings:
      - oracle_column: "ORD_ID"
        snowflake_column: "ORDER_ID"
      - oracle_column: "ORD_DT"
        snowflake_column: "ORDER_DATE"
        type_conversion: "TO_DATE"  # Optional type handling

  - oracle:
      schema: "STG_SCHEMA"
      table: "PRODUCT_STG"
    snowflake:
      database: "LANDING_DB"
      schema: "RAW"
      table: "PRODUCT_FEED"
    # No column_mappings = all columns have same names

# Lookup table mappings (reference tables)
lookup_mappings:
  - oracle:
      schema: "DW_SCHEMA"
      table: "DIM_REGION"
    snowflake:
      database: "DW_DB"
      schema: "DW"
      table: "DIM_REGION"  # Same name, different location

  - oracle:
      schema: "REF_SCHEMA"
      table: "CODE_LOOKUP"
    snowflake:
      database: "REF_DB"
      schema: "REFERENCE"
      table: "CODE_REFERENCE"

# Target tables (remain unchanged - document only)
target_tables:
  - schema: "DW"
    table: "DIM_CUSTOMER"
    load_strategy: "MERGE"  # MERGE, INSERT, TRUNCATE_INSERT
  - schema: "DW"
    table: "DIM_PRODUCT"
    load_strategy: "MERGE"
  - schema: "DW"
    table: "FACT_SALES"
    load_strategy: "INSERT"
```

#### 13.2 Auto-Mapping Discovery

When explicit mappings aren't provided, use intelligent matching:

```python
@dataclass
class SourceMappingEngine:
    """Engine to map Oracle sources to Snowflake sources"""
    
    def auto_discover_mappings(
        self,
        oracle_metadata: Dict,
        snowflake_metadata: Dict,
        fuzzy_threshold: float = 0.85
    ) -> List[TableMapping]:
        """
        Auto-discover mappings using:
        1. Exact name match (case-insensitive)
        2. Fuzzy name matching (Levenshtein distance)
        3. Column signature matching (same columns = likely same table)
        4. Naming pattern recognition (remove prefixes/suffixes)
        """
        pass

    def apply_naming_patterns(self, oracle_name: str) -> List[str]:
        """
        Generate potential Snowflake names from Oracle name
        Examples:
          CUSTOMER_STG → [CUSTOMER_LANDING, CUSTOMER_RAW, CUSTOMER]
          STG_ORDERS → [ORDERS_LANDING, RAW_ORDERS, ORDERS]
          T_PRODUCT_HIST → [PRODUCT_HISTORY, PRODUCT_HIST]
        """
        pass
```

#### 13.3 Mapping Data Models

```python
@dataclass
class SourceMapping:
    """Complete source mapping configuration"""
    table_mappings: List[TableMapping]
    lookup_mappings: List[TableMapping]
    default_schema_map: Dict[str, str]
    column_type_conversions: Dict[str, str]

@dataclass
class TableMapping:
    oracle_schema: str
    oracle_table: str
    snowflake_database: str
    snowflake_schema: str
    snowflake_table: str
    column_mappings: List[ColumnMapping]
    is_auto_mapped: bool = False
    confidence_score: float = 1.0

@dataclass
class ColumnMapping:
    oracle_column: str
    snowflake_column: str
    type_conversion: Optional[str] = None
    default_value: Optional[str] = None
    is_nullable_change: bool = False
```

---

### 14. Snowflake Stored Procedure Generator

#### 14.1 Procedure Structure

Each Informatica mapping generates a Snowflake stored procedure:

```sql
CREATE OR REPLACE PROCEDURE DW.SP_LOAD_DIM_CUSTOMER(
    P_BATCH_ID VARCHAR DEFAULT NULL,
    P_LOAD_DATE DATE DEFAULT CURRENT_DATE()
)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    v_row_count INTEGER := 0;
    v_start_time TIMESTAMP_NTZ := CURRENT_TIMESTAMP();
    v_error_message VARCHAR;
    v_result VARIANT;
BEGIN
    -- ============================================================
    -- Procedure: SP_LOAD_DIM_CUSTOMER
    -- Source Mapping: m_load_customer (Informatica)
    -- Description: Load customer dimension from staging
    -- Target Table: DW.DIM_CUSTOMER
    -- Source Tables: RAW.CUSTOMER_LANDING, DW.DIM_REGION
    -- Generated: 2025-01-15
    -- ============================================================

    -- Log start
    INSERT INTO DW.ETL_LOG (PROC_NAME, BATCH_ID, STATUS, START_TIME)
    VALUES ('SP_LOAD_DIM_CUSTOMER', :P_BATCH_ID, 'RUNNING', :v_start_time);

    -- Main transformation logic (converted from Informatica)
    MERGE INTO DW.DIM_CUSTOMER AS TGT
    USING (
        -- Source Qualifier equivalent
        WITH SQ_CUSTOMER AS (
            SELECT 
                CUSTOMER_ID,           -- Mapped from: CUST_ID
                CUSTOMER_NAME,         -- Mapped from: CUST_NM
                ADDRESS_LINE_1,        -- Mapped from: CUST_ADDR1
                REGION_ID,
                STATUS_CODE,
                EFFECTIVE_DATE
            FROM RAW.CUSTOMER_LANDING  -- Mapped from: STG_SCHEMA.CUSTOMER_STG
            WHERE STATUS_CODE = 'A'    -- Filter from SQ SQL Override
        ),
        
        -- Expression transformation: EXP_CUSTOMER_CALC
        EXP_CUSTOMER AS (
            SELECT
                CUSTOMER_ID,
                UPPER(CUSTOMER_NAME) AS CUSTOMER_NAME_UPPER,
                ADDRESS_LINE_1,
                REGION_ID,
                -- IIF(STATUS='A','Active','Inactive') converted:
                CASE WHEN STATUS_CODE = 'A' THEN 'Active' ELSE 'Inactive' END AS STATUS_DESC,
                EFFECTIVE_DATE,
                CURRENT_TIMESTAMP() AS DW_INSERT_DATE
            FROM SQ_CUSTOMER
        ),
        
        -- Lookup transformation: LKP_REGION
        LKP_REGION AS (
            SELECT
                e.*,
                r.REGION_NAME,
                r.REGION_CODE
            FROM EXP_CUSTOMER e
            LEFT JOIN DW.DIM_REGION r  -- Lookup table
                ON e.REGION_ID = r.REGION_ID
        ),
        
        -- Filter transformation: FIL_VALID_RECORDS
        FINAL_SELECT AS (
            SELECT *
            FROM LKP_REGION
            WHERE EFFECTIVE_DATE <= CURRENT_DATE()  -- Filter condition
        )
        
        SELECT
            -- Sequence equivalent
            DW.SEQ_CUSTOMER_KEY.NEXTVAL AS CUSTOMER_KEY,
            CUSTOMER_ID,
            CUSTOMER_NAME_UPPER AS CUSTOMER_NAME,
            ADDRESS_LINE_1,
            STATUS_DESC,
            REGION_NAME,
            REGION_CODE,
            DW_INSERT_DATE,
            CURRENT_TIMESTAMP() AS DW_UPDATE_DATE
        FROM FINAL_SELECT
        
    ) AS SRC
    ON TGT.CUSTOMER_ID = SRC.CUSTOMER_ID
    
    -- Update Strategy: DD_UPDATE
    WHEN MATCHED THEN UPDATE SET
        TGT.CUSTOMER_NAME = SRC.CUSTOMER_NAME,
        TGT.ADDRESS_LINE_1 = SRC.ADDRESS_LINE_1,
        TGT.STATUS_DESC = SRC.STATUS_DESC,
        TGT.REGION_NAME = SRC.REGION_NAME,
        TGT.REGION_CODE = SRC.REGION_CODE,
        TGT.DW_UPDATE_DATE = SRC.DW_UPDATE_DATE
    
    -- Update Strategy: DD_INSERT
    WHEN NOT MATCHED THEN INSERT (
        CUSTOMER_KEY,
        CUSTOMER_ID,
        CUSTOMER_NAME,
        ADDRESS_LINE_1,
        STATUS_DESC,
        REGION_NAME,
        REGION_CODE,
        DW_INSERT_DATE,
        DW_UPDATE_DATE
    ) VALUES (
        SRC.CUSTOMER_KEY,
        SRC.CUSTOMER_ID,
        SRC.CUSTOMER_NAME,
        SRC.ADDRESS_LINE_1,
        SRC.STATUS_DESC,
        SRC.REGION_NAME,
        SRC.REGION_CODE,
        SRC.DW_INSERT_DATE,
        SRC.DW_UPDATE_DATE
    );

    -- Get row count
    v_row_count := SQLROWCOUNT;

    -- Log success
    UPDATE DW.ETL_LOG 
    SET STATUS = 'SUCCESS', 
        END_TIME = CURRENT_TIMESTAMP(),
        ROWS_PROCESSED = :v_row_count
    WHERE PROC_NAME = 'SP_LOAD_DIM_CUSTOMER' 
      AND BATCH_ID = :P_BATCH_ID;

    v_result := OBJECT_CONSTRUCT(
        'status', 'SUCCESS',
        'rows_processed', v_row_count,
        'execution_time_seconds', TIMESTAMPDIFF(SECOND, v_start_time, CURRENT_TIMESTAMP())
    );
    
    RETURN v_result;

EXCEPTION
    WHEN OTHER THEN
        v_error_message := SQLERRM;
        
        UPDATE DW.ETL_LOG 
        SET STATUS = 'FAILED', 
            END_TIME = CURRENT_TIMESTAMP(),
            ERROR_MESSAGE = :v_error_message
        WHERE PROC_NAME = 'SP_LOAD_DIM_CUSTOMER' 
          AND BATCH_ID = :P_BATCH_ID;
        
        RAISE;
END;
$$;
```

#### 14.2 Informatica to Snowflake Expression Conversion

**Expression Translation Rules:**

| Informatica Function | Snowflake Equivalent | Notes |
|---------------------|---------------------|-------|
| `IIF(cond, true, false)` | `CASE WHEN cond THEN true ELSE false END` | Or `IFF()` |
| `DECODE(col, v1, r1, v2, r2, default)` | `DECODE(col, v1, r1, v2, r2, default)` | Same syntax |
| `NVL(col, default)` | `NVL(col, default)` or `COALESCE()` | Same |
| `NVL2(col, not_null, null)` | `NVL2(col, not_null, null)` | Same |
| `LTRIM(str)` | `LTRIM(str)` | Same |
| `RTRIM(str)` | `RTRIM(str)` | Same |
| `LPAD(str, len, pad)` | `LPAD(str, len, pad)` | Same |
| `RPAD(str, len, pad)` | `RPAD(str, len, pad)` | Same |
| `SUBSTR(str, start, len)` | `SUBSTR(str, start, len)` | Same |
| `INSTR(str, search)` | `POSITION(search IN str)` or `CHARINDEX()` | Different |
| `LENGTH(str)` | `LENGTH(str)` | Same |
| `UPPER(str)` | `UPPER(str)` | Same |
| `LOWER(str)` | `LOWER(str)` | Same |
| `INITCAP(str)` | `INITCAP(str)` | Same |
| `CONCAT(s1, s2)` | `CONCAT(s1, s2)` or `s1 \|\| s2` | Same |
| `\|\|` (concat operator) | `\|\|` | Same |
| `TO_CHAR(date, fmt)` | `TO_CHAR(date, fmt)` | Format differences |
| `TO_DATE(str, fmt)` | `TO_DATE(str, fmt)` | Format differences |
| `TO_NUMBER(str)` | `TO_NUMBER(str)` | Same |
| `TRUNC(date)` | `DATE_TRUNC('DAY', date)` | Different syntax |
| `TRUNC(num, dec)` | `TRUNC(num, dec)` | Same |
| `ROUND(num, dec)` | `ROUND(num, dec)` | Same |
| `ADD_TO_DATE(date, 'DD', n)` | `DATEADD(DAY, n, date)` | Different |
| `DATE_DIFF(date1, date2, 'DD')` | `DATEDIFF(DAY, date2, date1)` | Different |
| `SYSDATE` | `CURRENT_DATE()` | Different |
| `SYSTIMESTAMP` | `CURRENT_TIMESTAMP()` | Different |
| `GET_DATE_PART(date, 'MM')` | `DATE_PART(MONTH, date)` | Different |
| `IS_DATE(str, fmt)` | `TRY_TO_DATE(str, fmt) IS NOT NULL` | Different |
| `IS_NUMBER(str)` | `TRY_TO_NUMBER(str) IS NOT NULL` | Different |
| `ISNULL(col)` | `col IS NULL` | Different |
| `REG_EXTRACT(str, pattern, grp)` | `REGEXP_SUBSTR(str, pattern, 1, 1, 'e', grp)` | Different |
| `REG_MATCH(str, pattern)` | `REGEXP_LIKE(str, pattern)` | Different |
| `REG_REPLACE(str, pat, rep)` | `REGEXP_REPLACE(str, pat, rep)` | Same |
| `REPLACECHR(flag, str, old, new)` | `REPLACE(str, old, new)` | Simplified |
| `REPLACESTR(flag, str, old, new)` | `REPLACE(str, old, new)` | Same |
| `ERROR('message')` | Custom error handling | Use RAISE |
| `ABORT('message')` | `RAISE` statement | Different |
| `LOOKUP(...)` | `LEFT JOIN` | Restructure |
| `SETCOUNTVARIABLE(...)` | Snowflake variable | Different |
| `MD5(str)` | `MD5(str)` | Same |
| `SHA1(str)` | `SHA1(str)` | Same |
| `AES_ENCRYPT(str, key)` | `ENCRYPT(str, key)` | Different |

**Date Format Conversion:**

| Informatica Format | Snowflake Format |
|-------------------|------------------|
| `MM/DD/YYYY` | `MM/DD/YYYY` |
| `YYYY-MM-DD` | `YYYY-MM-DD` |
| `DD-MON-YYYY` | `DD-MON-YYYY` |
| `HH24:MI:SS` | `HH24:MI:SS` |
| `YYYYMMDD` | `YYYYMMDD` |
| `J` (Julian) | Custom conversion needed |

#### 14.3 Expression Parser & Converter

```python
class InformaticaExpressionConverter:
    """Convert Informatica expressions to Snowflake SQL"""
    
    # Function mappings
    FUNCTION_MAP = {
        'IIF': 'iff_to_case',
        'ADD_TO_DATE': 'convert_add_to_date',
        'DATE_DIFF': 'convert_date_diff',
        'SYSDATE': lambda: 'CURRENT_DATE()',
        'SYSTIMESTAMP': lambda: 'CURRENT_TIMESTAMP()',
        'ISNULL': 'convert_isnull',
        'INSTR': 'convert_instr',
        'TRUNC': 'convert_trunc',
        'GET_DATE_PART': 'convert_get_date_part',
        'IS_DATE': 'convert_is_date',
        'IS_NUMBER': 'convert_is_number',
        'REG_EXTRACT': 'convert_reg_extract',
        'REG_MATCH': 'convert_reg_match',
        'REPLACECHR': 'convert_replacechr',
        'ERROR': 'convert_error',
        'ABORT': 'convert_abort',
    }
    
    def convert(self, informatica_expr: str, field_mappings: Dict[str, str]) -> str:
        """
        Convert Informatica expression to Snowflake SQL
        
        Args:
            informatica_expr: Original Informatica expression
            field_mappings: Dict mapping Informatica field names to Snowflake columns
            
        Returns:
            Snowflake SQL expression
        """
        pass
    
    def iff_to_case(self, condition: str, true_val: str, false_val: str) -> str:
        """Convert IIF to CASE WHEN or IFF"""
        # Simple cases use IFF
        if self._is_simple_condition(condition):
            return f"IFF({condition}, {true_val}, {false_val})"
        # Complex nested IIFs become CASE
        return f"CASE WHEN {condition} THEN {true_val} ELSE {false_val} END"
    
    def convert_add_to_date(self, date_col: str, interval_type: str, value: str) -> str:
        """Convert ADD_TO_DATE to DATEADD"""
        interval_map = {'DD': 'DAY', 'MM': 'MONTH', 'YY': 'YEAR', 'HH': 'HOUR'}
        sf_interval = interval_map.get(interval_type.strip("'"), interval_type)
        return f"DATEADD({sf_interval}, {value}, {date_col})"
    
    def replace_field_names(self, expr: str, field_mappings: Dict[str, str]) -> str:
        """Replace Informatica field names with Snowflake column names"""
        pass
```

#### 14.4 Transformation Type Handlers

**Source Qualifier → CTE with SELECT:**
```python
def convert_source_qualifier(self, sq: Transformation, source_mapping: TableMapping) -> str:
    """Convert Source Qualifier to CTE"""
    sf_table = f"{source_mapping.snowflake_database}.{source_mapping.snowflake_schema}.{source_mapping.snowflake_table}"
    
    # Handle SQL Override
    if sq.properties.get('Sql Query'):
        sql = self.convert_sql_override(sq.properties['Sql Query'], source_mapping)
    else:
        columns = self.map_columns(sq.fields, source_mapping.column_mappings)
        sql = f"SELECT {columns} FROM {sf_table}"
    
    # Add filter if present
    if sq.properties.get('Source Filter'):
        filter_clause = self.convert_expression(sq.properties['Source Filter'])
        sql += f" WHERE {filter_clause}"
    
    return f"{sq.name} AS (\n    {sql}\n)"
```

**Expression → CTE with calculated columns:**
```python
def convert_expression_transform(self, exp: Transformation, source_cte: str) -> str:
    """Convert Expression transformation to CTE"""
    select_parts = []
    
    for field in exp.fields:
        if field.expression:
            converted_expr = self.convert_expression(field.expression)
            select_parts.append(f"{converted_expr} AS {field.name}")
        elif field.port_type in ('INPUT/OUTPUT', 'OUTPUT'):
            select_parts.append(field.name)
    
    return f"{exp.name} AS (\n    SELECT\n        {',\n        '.join(select_parts)}\n    FROM {source_cte}\n)"
```

**Lookup → LEFT JOIN:**
```python
def convert_lookup(self, lkp: Transformation, source_cte: str, lookup_mapping: TableMapping) -> str:
    """Convert Lookup transformation to LEFT JOIN CTE"""
    lkp_table = f"{lookup_mapping.snowflake_database}.{lookup_mapping.snowflake_schema}.{lookup_mapping.snowflake_table}"
    
    # Get lookup condition
    condition = self.convert_expression(lkp.properties.get('Lookup condition', ''))
    
    # Get return columns
    return_cols = [f.name for f in lkp.fields if f.port_type == 'OUTPUT']
    
    return f"""
{lkp.name} AS (
    SELECT
        s.*,
        {', '.join([f'l.{col}' for col in return_cols])}
    FROM {source_cte} s
    LEFT JOIN {lkp_table} l
        ON {condition}
)"""
```

**Filter → CTE with WHERE:**
```python
def convert_filter(self, fil: Transformation, source_cte: str) -> str:
    """Convert Filter transformation to CTE with WHERE clause"""
    condition = self.convert_expression(fil.properties.get('Filter Condition', '1=1'))
    
    return f"{fil.name} AS (\n    SELECT *\n    FROM {source_cte}\n    WHERE {condition}\n)"
```

**Aggregator → CTE with GROUP BY:**
```python
def convert_aggregator(self, agg: Transformation, source_cte: str) -> str:
    """Convert Aggregator transformation to CTE with GROUP BY"""
    group_by_cols = []
    select_parts = []
    
    for field in agg.fields:
        if field.properties.get('EXPRESSIONTYPE') == 'GROUPBY':
            group_by_cols.append(field.name)
            select_parts.append(field.name)
        elif field.expression:
            converted = self.convert_expression(field.expression)
            select_parts.append(f"{converted} AS {field.name}")
    
    return f"""
{agg.name} AS (
    SELECT
        {',\n        '.join(select_parts)}
    FROM {source_cte}
    GROUP BY {', '.join(group_by_cols)}
)"""
```

**Joiner → CTE with JOIN:**
```python
def convert_joiner(self, jnr: Transformation, master_cte: str, detail_cte: str) -> str:
    """Convert Joiner transformation to CTE with JOIN"""
    join_type_map = {
        'Normal Join': 'INNER JOIN',
        'Master Outer Join': 'LEFT JOIN',
        'Detail Outer Join': 'RIGHT JOIN',
        'Full Outer Join': 'FULL OUTER JOIN'
    }
    
    join_type = join_type_map.get(jnr.properties.get('Join Type', 'Normal Join'), 'INNER JOIN')
    condition = self.convert_expression(jnr.properties.get('Join Condition', ''))
    
    return f"""
{jnr.name} AS (
    SELECT m.*, d.*
    FROM {master_cte} m
    {join_type} {detail_cte} d
        ON {condition}
)"""
```

**Router → Multiple CTEs with filters:**
```python
def convert_router(self, rtr: Transformation, source_cte: str) -> List[str]:
    """Convert Router to multiple filtered CTEs"""
    ctes = []
    
    for group in rtr.groups:
        condition = self.convert_expression(group.expression)
        cte_name = f"{rtr.name}_{group.name}"
        ctes.append(f"{cte_name} AS (\n    SELECT *\n    FROM {source_cte}\n    WHERE {condition}\n)")
    
    # Default group (rows not matching any condition)
    if rtr.has_default_group:
        all_conditions = ' AND '.join([f"NOT ({g.expression})" for g in rtr.groups])
        ctes.append(f"{rtr.name}_DEFAULT AS (\n    SELECT *\n    FROM {source_cte}\n    WHERE {all_conditions}\n)")
    
    return ctes
```

**Update Strategy → MERGE statement:**
```python
def convert_update_strategy(self, upd: Transformation, source_cte: str, target_table: str) -> str:
    """Convert Update Strategy to MERGE statement"""
    strategy_expr = upd.properties.get('Update Strategy Expression', 'DD_INSERT')
    
    # Parse strategy to determine MERGE behavior
    # DD_INSERT = 0, DD_UPDATE = 1, DD_DELETE = 2, DD_REJECT = 3
    
    if 'DD_UPDATE' in strategy_expr and 'DD_INSERT' in strategy_expr:
        return self._generate_merge_upsert(source_cte, target_table, upd)
    elif 'DD_INSERT' in strategy_expr:
        return self._generate_insert(source_cte, target_table, upd)
    elif 'DD_UPDATE' in strategy_expr:
        return self._generate_update(source_cte, target_table, upd)
    elif 'DD_DELETE' in strategy_expr:
        return self._generate_delete(source_cte, target_table, upd)
```

**Sequence Generator → Snowflake Sequence:**
```python
def convert_sequence(self, seq: Transformation) -> str:
    """Generate Snowflake sequence reference"""
    seq_name = f"SEQ_{seq.name.replace('SEQ_', '')}"
    return f"{seq_name}.NEXTVAL"

def generate_sequence_ddl(self, seq: Transformation, schema: str) -> str:
    """Generate CREATE SEQUENCE DDL"""
    start_val = seq.properties.get('Start Value', '1')
    increment = seq.properties.get('Increment By', '1')
    
    return f"""
CREATE SEQUENCE IF NOT EXISTS {schema}.{seq.name}
    START WITH {start_val}
    INCREMENT BY {increment};
"""
```

---

### 15. Stored Procedure Generator Architecture

#### 15.1 Generator Class

```python
class SnowflakeProcedureGenerator:
    """Generate Snowflake stored procedures from Informatica mappings"""
    
    def __init__(
        self,
        source_mapping: SourceMapping,
        expression_converter: InformaticaExpressionConverter,
        config: GeneratorConfig
    ):
        self.source_mapping = source_mapping
        self.expr_converter = expression_converter
        self.config = config
    
    def generate_procedure(self, mapping: InformaticaMapping) -> StoredProcedure:
        """Generate complete stored procedure from Informatica mapping"""
        
        # 1. Build transformation DAG from connectors
        transform_dag = self._build_transformation_dag(mapping.connectors)
        
        # 2. Topologically sort transformations
        ordered_transforms = self._topological_sort(transform_dag)
        
        # 3. Generate CTEs for each transformation
        ctes = []
        for transform in ordered_transforms:
            cte = self._generate_cte(transform, mapping)
            ctes.append(cte)
        
        # 4. Generate final SELECT/MERGE/INSERT
        final_sql = self._generate_final_statement(mapping, ctes[-1])
        
        # 5. Wrap in procedure template
        procedure = self._wrap_in_procedure(
            mapping_name=mapping.name,
            ctes=ctes,
            final_sql=final_sql,
            target_table=mapping.targets[0]
        )
        
        return procedure
    
    def _build_transformation_dag(self, connectors: List[Connector]) -> Dict:
        """Build directed acyclic graph of transformations"""
        pass
    
    def _topological_sort(self, dag: Dict) -> List[Transformation]:
        """Sort transformations in execution order"""
        pass
    
    def _generate_cte(self, transform: Transformation, mapping: InformaticaMapping) -> str:
        """Generate CTE for specific transformation type"""
        converters = {
            'Source Qualifier': self._convert_source_qualifier,
            'Expression': self._convert_expression,
            'Lookup Procedure': self._convert_lookup,
            'Filter': self._convert_filter,
            'Aggregator': self._convert_aggregator,
            'Joiner': self._convert_joiner,
            'Router': self._convert_router,
            'Sorter': self._convert_sorter,
            'Rank': self._convert_rank,
            'Sequence Generator': self._convert_sequence,
            'Update Strategy': self._convert_update_strategy,
            'Normalizer': self._convert_normalizer,
            'Union': self._convert_union,
        }
        
        converter = converters.get(transform.type)
        if converter:
            return converter(transform, mapping)
        else:
            # Unknown transformation - generate comment for manual review
            return f"-- TODO: Manual conversion needed for {transform.type}: {transform.name}"
```

#### 15.2 Procedure Template

```python
PROCEDURE_TEMPLATE = '''
CREATE OR REPLACE PROCEDURE {schema}.{procedure_name}(
    P_BATCH_ID VARCHAR DEFAULT NULL,
    P_LOAD_DATE DATE DEFAULT CURRENT_DATE(),
    P_DEBUG_MODE BOOLEAN DEFAULT FALSE
)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    v_row_count INTEGER := 0;
    v_start_time TIMESTAMP_NTZ := CURRENT_TIMESTAMP();
    v_error_message VARCHAR;
    v_step VARCHAR := 'INIT';
    v_result VARIANT;
BEGIN
    -- ============================================================
    -- Procedure: {procedure_name}
    -- Source Mapping: {mapping_name}
    -- Description: {description}
    -- Target Table: {target_table}
    -- Source Tables: {source_tables}
    -- Generated: {generated_date}
    -- Generator Version: {generator_version}
    -- ============================================================

    -- Initialize logging
    v_step := 'LOG_START';
    INSERT INTO {log_schema}.ETL_EXECUTION_LOG (
        PROCEDURE_NAME, BATCH_ID, STATUS, START_TIME, STEP
    ) VALUES (
        '{procedure_name}', :P_BATCH_ID, 'RUNNING', :v_start_time, 'START'
    );

    -- Begin transformation logic
    v_step := 'TRANSFORM';
    
{transformation_sql}

    -- Get affected row count
    v_row_count := SQLROWCOUNT;

    -- Log success
    v_step := 'LOG_SUCCESS';
    UPDATE {log_schema}.ETL_EXECUTION_LOG 
    SET STATUS = 'SUCCESS', 
        END_TIME = CURRENT_TIMESTAMP(),
        ROWS_PROCESSED = :v_row_count,
        STEP = 'COMPLETE'
    WHERE PROCEDURE_NAME = '{procedure_name}' 
      AND BATCH_ID = :P_BATCH_ID
      AND STATUS = 'RUNNING';

    -- Return result
    v_result := OBJECT_CONSTRUCT(
        'status', 'SUCCESS',
        'procedure', '{procedure_name}',
        'mapping', '{mapping_name}',
        'rows_processed', v_row_count,
        'execution_time_seconds', TIMESTAMPDIFF(SECOND, v_start_time, CURRENT_TIMESTAMP()),
        'batch_id', P_BATCH_ID
    );
    
    RETURN v_result;

EXCEPTION
    WHEN OTHER THEN
        v_error_message := SQLERRM || ' at step: ' || v_step;
        
        -- Log failure
        UPDATE {log_schema}.ETL_EXECUTION_LOG 
        SET STATUS = 'FAILED', 
            END_TIME = CURRENT_TIMESTAMP(),
            ERROR_MESSAGE = :v_error_message,
            STEP = :v_step
        WHERE PROCEDURE_NAME = '{procedure_name}' 
          AND BATCH_ID = :P_BATCH_ID
          AND STATUS = 'RUNNING';
        
        -- Re-raise with context
        RAISE;
END;
$$;

-- Grant execute permission
GRANT USAGE ON PROCEDURE {schema}.{procedure_name}(VARCHAR, DATE, BOOLEAN) TO ROLE {execute_role};

-- Add comment
COMMENT ON PROCEDURE {schema}.{procedure_name}(VARCHAR, DATE, BOOLEAN) IS 
    'Migrated from Informatica mapping: {mapping_name}. Generated on {generated_date}';
'''
```

---

### 16. Supporting DDL Generation

#### 16.1 Sequence DDL

```sql
-- Generated sequences for surrogate keys
CREATE SEQUENCE IF NOT EXISTS DW.SEQ_CUSTOMER_KEY START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE IF NOT EXISTS DW.SEQ_PRODUCT_KEY START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE IF NOT EXISTS DW.SEQ_ORDER_KEY START WITH 1 INCREMENT BY 1;
```

#### 16.2 ETL Logging Tables

```sql
-- ETL Execution Log
CREATE TABLE IF NOT EXISTS DW.ETL_EXECUTION_LOG (
    LOG_ID NUMBER AUTOINCREMENT PRIMARY KEY,
    PROCEDURE_NAME VARCHAR(200) NOT NULL,
    BATCH_ID VARCHAR(100),
    STATUS VARCHAR(20) NOT NULL,
    START_TIME TIMESTAMP_NTZ NOT NULL,
    END_TIME TIMESTAMP_NTZ,
    ROWS_PROCESSED NUMBER,
    ERROR_MESSAGE VARCHAR(4000),
    STEP VARCHAR(100),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ETL Batch Control
CREATE TABLE IF NOT EXISTS DW.ETL_BATCH_CONTROL (
    BATCH_ID VARCHAR(100) PRIMARY KEY,
    BATCH_DATE DATE NOT NULL,
    STATUS VARCHAR(20) NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    COMPLETED_AT TIMESTAMP_NTZ
);
```

#### 16.3 Master Orchestration Procedure

```sql
-- Master procedure to run all loads in order
CREATE OR REPLACE PROCEDURE DW.SP_RUN_DAILY_ETL(
    P_BATCH_DATE DATE DEFAULT CURRENT_DATE()
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    v_batch_id VARCHAR;
    v_result VARIANT;
    v_proc_result VARIANT;
BEGIN
    -- Generate batch ID
    v_batch_id := 'BATCH_' || TO_CHAR(P_BATCH_DATE, 'YYYYMMDD') || '_' || TO_CHAR(CURRENT_TIMESTAMP(), 'HH24MISS');
    
    -- Register batch
    INSERT INTO DW.ETL_BATCH_CONTROL (BATCH_ID, BATCH_DATE, STATUS)
    VALUES (:v_batch_id, :P_BATCH_DATE, 'RUNNING');
    
    -- Execute procedures in dependency order
    -- (Generated from Informatica workflow)
    
    -- Step 1: Dimension loads
    CALL DW.SP_LOAD_DIM_DATE(:v_batch_id, :P_BATCH_DATE);
    CALL DW.SP_LOAD_DIM_CUSTOMER(:v_batch_id, :P_BATCH_DATE);
    CALL DW.SP_LOAD_DIM_PRODUCT(:v_batch_id, :P_BATCH_DATE);
    CALL DW.SP_LOAD_DIM_REGION(:v_batch_id, :P_BATCH_DATE);
    
    -- Step 2: Fact loads
    CALL DW.SP_LOAD_FACT_SALES(:v_batch_id, :P_BATCH_DATE);
    CALL DW.SP_LOAD_FACT_INVENTORY(:v_batch_id, :P_BATCH_DATE);
    
    -- Mark batch complete
    UPDATE DW.ETL_BATCH_CONTROL 
    SET STATUS = 'COMPLETED', COMPLETED_AT = CURRENT_TIMESTAMP()
    WHERE BATCH_ID = :v_batch_id;
    
    RETURN OBJECT_CONSTRUCT('status', 'SUCCESS', 'batch_id', v_batch_id);
    
EXCEPTION
    WHEN OTHER THEN
        UPDATE DW.ETL_BATCH_CONTROL 
        SET STATUS = 'FAILED', COMPLETED_AT = CURRENT_TIMESTAMP()
        WHERE BATCH_ID = :v_batch_id;
        RAISE;
END;
$$;
```

---

### 17. Enhanced Project Structure

```
dw_documentation/
├── main.py
├── config/
│   ├── config.yaml
│   └── source_mapping.yaml          # NEW: Source mapping config
├── parsers/
│   ├── __init__.py
│   ├── informatica_mapping.py
│   ├── informatica_workflow.py
│   └── xml_utils.py
├── extractors/
│   ├── __init__.py
│   ├── oracle_extractor.py
│   ├── snowflake_extractor.py       # NEW: Snowflake metadata
│   ├── procedure_parser.py
│   └── view_parser.py
├── converters/                       # NEW: Conversion module
│   ├── __init__.py
│   ├── expression_converter.py      # Informatica → Snowflake expressions
│   ├── transformation_converter.py  # Transform types → CTEs
│   └── datatype_converter.py        # Oracle → Snowflake types
├── generators/
│   ├── __init__.py
│   ├── markdown_generator.py
│   ├── html_generator.py
│   ├── json_exporter.py
│   ├── diagram_generator.py
│   ├── procedure_generator.py       # NEW: Snowflake SP generator
│   └── ddl_generator.py             # NEW: Supporting DDL
├── mappers/                          # NEW: Source mapping
│   ├── __init__.py
│   ├── source_mapper.py             # Oracle → Snowflake source mapping
│   ├── column_mapper.py             # Column name mapping
│   └── auto_mapper.py               # Fuzzy matching auto-mapper
├── models/
│   ├── __init__.py
│   ├── mapping.py
│   ├── transformation.py
│   ├── lineage.py
│   ├── source_mapping.py            # NEW: Source mapping models
│   └── procedure.py                 # NEW: Procedure models
├── templates/
│   ├── mapping_template.md
│   ├── lineage_template.md
│   ├── data_dictionary.md
│   ├── procedure_template.sql       # NEW: SP template
│   └── ddl_template.sql             # NEW: DDL templates
├── output/
│   ├── documentation/
│   ├── procedures/                  # NEW: Generated SPs
│   └── ddl/                         # NEW: Supporting DDL
├── requirements.txt
└── README.md
```

---

### 18. Enhanced CLI Commands

```bash
# Full migration (documentation + stored procedures)
python main.py migrate --config config.yaml --source-mapping source_mapping.yaml

# Generate only stored procedures
python main.py generate-procedures \
    --mapping-dir /path/to/informatica \
    --source-mapping source_mapping.yaml \
    --output ./output/procedures

# Generate procedures for specific mapping
python main.py generate-procedure \
    --mapping m_load_customer \
    --source-mapping source_mapping.yaml \
    --output ./output/procedures/sp_load_customer.sql

# Auto-discover source mappings
python main.py auto-map \
    --oracle-config oracle.yaml \
    --snowflake-config snowflake.yaml \
    --output source_mapping.yaml \
    --threshold 0.85

# Validate generated procedures (syntax check)
python main.py validate-procedures \
    --procedure-dir ./output/procedures \
    --snowflake-config snowflake.yaml

# Generate supporting DDL (sequences, log tables)
python main.py generate-ddl \
    --config config.yaml \
    --output ./output/ddl

# Generate master orchestration procedure
python main.py generate-orchestration \
    --workflow-dir /path/to/workflows \
    --output ./output/procedures/sp_master_etl.sql

# Dry run - show what would be generated without creating files
python main.py migrate --config config.yaml --dry-run

# Compare Informatica logic vs generated procedure
python main.py compare \
    --mapping m_load_customer \
    --procedure ./output/procedures/sp_load_customer.sql
```

---

### 19. Validation & Testing

#### 19.1 Procedure Validation

```python
class ProcedureValidator:
    """Validate generated Snowflake procedures"""
    
    def validate_syntax(self, procedure_sql: str) -> ValidationResult:
        """Check SQL syntax using Snowflake's parser"""
        pass
    
    def validate_objects_exist(self, procedure: StoredProcedure, snowflake_conn) -> ValidationResult:
        """Verify all referenced tables/sequences exist"""
        pass
    
    def validate_column_mappings(self, procedure: StoredProcedure, source_mapping: SourceMapping) -> ValidationResult:
        """Ensure all column mappings are applied correctly"""
        pass
    
    def compare_with_informatica(self, procedure: StoredProcedure, mapping: InformaticaMapping) -> ComparisonResult:
        """Compare procedure logic with original Informatica mapping"""
        pass
```

#### 19.2 Data Validation Queries

```sql
-- Generate validation queries to compare Oracle vs Snowflake results
-- Row count comparison
SELECT 'ORACLE' AS SOURCE, COUNT(*) AS ROW_COUNT FROM ORACLE_TABLE
UNION ALL
SELECT 'SNOWFLAKE' AS SOURCE, COUNT(*) AS ROW_COUNT FROM SNOWFLAKE_TABLE;

-- Aggregate comparison
SELECT 
    SUM(AMOUNT) AS TOTAL_AMOUNT,
    COUNT(DISTINCT CUSTOMER_ID) AS UNIQUE_CUSTOMERS
FROM TARGET_TABLE;

-- Sample data comparison
SELECT * FROM TARGET_TABLE 
WHERE CUSTOMER_ID IN (SELECT CUSTOMER_ID FROM TARGET_TABLE SAMPLE (100 ROWS));
```

---

### 20. Deliverables Summary

| Output | Description | Location |
|--------|-------------|----------|
| **Mapping Documentation** | Per-mapping Markdown/HTML docs | `output/documentation/mappings/` |
| **Data Dictionary** | Table/column reference | `output/documentation/data_dictionary.md` |
| **Lineage Reports** | Source-to-target lineage | `output/documentation/lineage/` |
| **Stored Procedures** | Snowflake SPs from mappings | `output/procedures/` |
| **Sequence DDL** | CREATE SEQUENCE statements | `output/ddl/sequences.sql` |
| **Log Table DDL** | ETL logging tables | `output/ddl/log_tables.sql` |
| **Orchestration SP** | Master ETL procedure | `output/procedures/sp_master_etl.sql` |
| **Source Mapping Report** | Oracle → Snowflake mapping | `output/documentation/source_mapping.md` |
| **Validation Queries** | Data comparison SQL | `output/validation/` |
| **JSON Export** | Machine-readable metadata | `output/export/dw_metadata.json` |

---

## Notes

- Informatica XML structure may vary by PowerCenter version (9.x, 10.x)
- Handle encoding issues in XML files (UTF-8, ISO-8859-1)
- Some complex expressions may need manual review
- Dynamic SQL in procedures flagged for manual documentation
- Consider incremental runs for large repositories
- Test generated procedures in DEV environment before deploying
- Review converted expressions for edge cases
- Maintain mapping version history for audit
