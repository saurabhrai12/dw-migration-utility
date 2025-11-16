"""
Snowflake stored procedure generator from Informatica mappings.
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Template
from loguru import logger

from .sql_translator import SQLTranslator
from ..parsers.informatica_xml_parser import InformaticaMapping
from ..crawlers.metadata_models import TableMetadata, ColumnMetadata


class StoredProcedureGenerator:
    """Generate Snowflake stored procedures from Informatica mappings."""

    # Stored Procedure template
    SP_TEMPLATE = """-- Auto-generated Stored Procedure
-- Source: {{ source_mapping }}
-- Generated: {{ generated_date }}
-- Description: {{ description }}

CREATE OR REPLACE PROCEDURE {{ schema }}.{{ procedure_name }}(
    P_LOAD_DATE DATE DEFAULT CURRENT_DATE(),
    P_BATCH_ID VARCHAR DEFAULT 'BATCH_' || TO_CHAR(CURRENT_TIMESTAMP(), 'YYYYMMDDHH24MISS'),
    P_DEBUG_MODE BOOLEAN DEFAULT FALSE
)
RETURNS OBJECT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    V_START_TIME TIMESTAMP_NTZ := CURRENT_TIMESTAMP();
    V_END_TIME TIMESTAMP_NTZ;
    V_ROWS_INSERTED INTEGER := 0;
    V_ROWS_UPDATED INTEGER := 0;
    V_ROWS_DELETED INTEGER := 0;
    V_ERROR_MESSAGE VARCHAR;
    V_EXECUTION_STATUS VARCHAR := 'SUCCESS';
BEGIN

    -- Logging: Start of procedure
    IF P_DEBUG_MODE THEN
        SELECT SYSTEM$LOG_INFO('Starting procedure: {{ procedure_name }}') INTO V_ERROR_MESSAGE;
    END IF;

    -- Insert start log
    INSERT INTO ETL_METADATA.PROCESS_LOG (
        PROCESS_NAME,
        EXECUTION_START_TIME,
        BATCH_ID,
        STATUS,
        SOURCE_SYSTEM,
        TARGET_SYSTEM,
        LOAD_DATE
    ) VALUES (
        '{{ procedure_name }}',
        V_START_TIME,
        P_BATCH_ID,
        'RUNNING',
        '{{ source_system }}',
        '{{ target_system }}',
        P_LOAD_DATE
    );

    BEGIN

        -- Main MERGE/INSERT Logic
        -- ============================================
{{ merge_logic | indent(8) }}
        -- ============================================

        -- Get row counts
        GET DIAGNOSTICS V_ROWS_INSERTED = ROW_COUNT;

        -- Data quality checks
{{ quality_checks | indent(8) }}

    EXCEPTION
        WHEN OTHER THEN
            V_EXECUTION_STATUS := 'FAILED';
            V_ERROR_MESSAGE := SQLERRM();
            IF P_DEBUG_MODE THEN
                SELECT SYSTEM$LOG_ERROR('Error in {{ procedure_name }}: ' || V_ERROR_MESSAGE) INTO V_ERROR_MESSAGE;
            END IF;
    END;

    -- Logging: End of procedure
    V_END_TIME := CURRENT_TIMESTAMP();

    UPDATE ETL_METADATA.PROCESS_LOG
    SET
        EXECUTION_END_TIME = V_END_TIME,
        STATUS = V_EXECUTION_STATUS,
        ROWS_PROCESSED = V_ROWS_INSERTED,
        ROWS_UPDATED = V_ROWS_UPDATED,
        ROWS_DELETED = V_ROWS_DELETED,
        ERROR_MESSAGE = V_ERROR_MESSAGE,
        EXECUTION_DURATION_SECONDS = DATEDIFF(SECOND, V_START_TIME, V_END_TIME)
    WHERE BATCH_ID = P_BATCH_ID
      AND PROCESS_NAME = '{{ procedure_name }}';

    -- Return status object
    RETURN OBJECT_CONSTRUCT(
        'STATUS', V_EXECUTION_STATUS,
        'ROWS_INSERTED', V_ROWS_INSERTED,
        'ROWS_UPDATED', V_ROWS_UPDATED,
        'ROWS_DELETED', V_ROWS_DELETED,
        'ERROR_MESSAGE', V_ERROR_MESSAGE,
        'EXECUTION_TIME_SECONDS', DATEDIFF(SECOND, V_START_TIME, V_END_TIME),
        'BATCH_ID', P_BATCH_ID
    );

END;
$$;
"""

    MERGE_TEMPLATE = """MERGE INTO {{ target_schema }}.{{ target_table }} TGT
USING (
    SELECT
{{ select_columns | indent(12) }}
    FROM {{ source_schema }}.{{ source_table }} SRC
{{ join_clauses | indent(4) }}
{{ where_clause | indent(4) }}
{{ group_by_clause | indent(4) }}
) SRC
ON {{ merge_condition }}
WHEN MATCHED THEN
    UPDATE SET
{{ update_columns | indent(8) }}
WHEN NOT MATCHED THEN
    INSERT (
{{ insert_columns | indent(8) }}
    )
    VALUES (
{{ insert_values | indent(8) }}
    );"""

    def __init__(self, output_dir: str = "output/stored_procedures", schema: str = "PUBLIC"):
        """
        Initialize stored procedure generator.

        Args:
            output_dir: Directory to save generated procedures
            schema: Target Snowflake schema
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.schema = schema
        self.sql_translator = SQLTranslator()
        self.generated_procedures = []

    def generate_from_mapping(
        self,
        informatica_mapping: InformaticaMapping,
        target_table_metadata: TableMetadata = None
    ) -> str:
        """
        Generate stored procedure from Informatica mapping.

        Args:
            informatica_mapping: InformaticaMapping object
            target_table_metadata: Optional target table metadata

        Returns:
            Path to generated procedure file
        """
        logger.info(f"Generating stored procedure for mapping: {informatica_mapping.name}")

        # Determine target table
        if informatica_mapping.targets:
            target = informatica_mapping.targets[0]
            target_table = target.name
            target_schema = self.schema
        else:
            logger.warning("No target found in mapping")
            return None

        # Determine source table
        if informatica_mapping.sources:
            source = informatica_mapping.sources[0]
            source_table = source.name
            source_schema = self.schema
        else:
            logger.warning("No source found in mapping")
            return None

        # Generate procedure name
        procedure_name = f"SP_{target_table}_LOAD"

        # Extract transformations and expressions
        select_columns, join_clauses, where_clause, group_by = self._extract_query_components(
            informatica_mapping
        )

        # Build merge logic
        merge_logic = self._build_merge_logic(
            source_schema,
            source_table,
            target_schema,
            target_table,
            select_columns,
            join_clauses,
            where_clause,
            group_by,
            informatica_mapping,
            target_table_metadata
        )

        # Build quality checks
        quality_checks = self._build_quality_checks(
            target_schema,
            target_table,
            target_table_metadata
        )

        # Render template
        template = Template(self.SP_TEMPLATE)
        proc_sql = template.render(
            procedure_name=procedure_name,
            schema=target_schema,
            description=informatica_mapping.description or f"Load {target_table}",
            source_mapping=informatica_mapping.name,
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            source_system='Oracle',
            target_system='Snowflake',
            merge_logic=merge_logic,
            quality_checks=quality_checks
        )

        # Save to file
        output_file = self.output_dir / f"{procedure_name}.sql"
        with open(output_file, 'w') as f:
            f.write(proc_sql)

        logger.info(f"Generated procedure: {output_file}")
        self.generated_procedures.append({
            'name': procedure_name,
            'file': str(output_file),
            'mapping': informatica_mapping.name,
            'target': f"{target_schema}.{target_table}"
        })

        return str(output_file)

    def _extract_query_components(
        self,
        mapping: InformaticaMapping
    ) -> tuple:
        """
        Extract SELECT columns, JOINs, WHERE, and GROUP BY from mapping.

        Args:
            mapping: InformaticaMapping object

        Returns:
            Tuple of (select_columns, join_clauses, where_clause, group_by)
        """
        select_columns = []
        join_clauses = []
        where_clause = ""
        group_by = ""

        # Extract columns from transformations
        for trans in mapping.transformations:
            if trans.type.upper() in ['EXPRESSION', 'EXPRESSION TRANSFORMER']:
                for port in trans.ports:
                    if port.get('port_type') == 'OUTPUT':
                        expr = self.sql_translator.translate_expression(
                            port.get('expression', port['name'])
                        )
                        if expr:
                            select_columns.append(f"{expr} AS {port['name']}")
                        else:
                            select_columns.append(f"{port['name']}")

            elif trans.type.upper() == 'FILTER':
                # Extract filter condition
                for prop, value in trans.properties.items():
                    if prop.upper() == 'FILTER_CONDITION':
                        where_clause = self.sql_translator.translate_expression(value)

            elif trans.type.upper() in ['JOINER', 'JOIN']:
                # Extract join condition from connectors
                join_sql = self._extract_join_logic(mapping, trans.name)
                if join_sql:
                    join_clauses.append(join_sql)

            elif trans.type.upper() == 'AGGREGATOR':
                # Extract group by columns
                for port in trans.ports:
                    if port.get('port_type') == 'GROUP':
                        group_by += f", {port['name']}" if group_by else port['name']

        # Default to source columns if no expressions found
        if not select_columns and mapping.sources:
            source = mapping.sources[0]
            for col in source.columns:
                select_columns.append(col['name'])

        return select_columns, join_clauses, where_clause, group_by

    def _extract_join_logic(self, mapping: InformaticaMapping, join_name: str) -> str:
        """Extract JOIN logic from mapping."""
        # Find join transformation
        join_trans = next((t for t in mapping.transformations if t.name == join_name), None)

        if not join_trans:
            return None

        join_type = join_trans.properties.get('JoinType', 'INNER').upper()
        join_condition = join_trans.properties.get('JoinCondition', '')

        if join_condition:
            return f"{join_type} JOIN (...) ON {join_condition}"

        return None

    def _build_merge_logic(
        self,
        source_schema: str,
        source_table: str,
        target_schema: str,
        target_table: str,
        select_columns: List[str],
        join_clauses: List[str],
        where_clause: str,
        group_by: str,
        mapping: InformaticaMapping,
        target_metadata: TableMetadata = None
    ) -> str:
        """Build MERGE statement."""
        # Get merge key from target metadata or first primary key
        merge_key = "ID"
        if target_metadata and target_metadata.primary_keys:
            merge_key = target_metadata.primary_keys[0]

        select_cols_str = ",\n".join(select_columns) if select_columns else "*"
        join_str = "\n".join(join_clauses) if join_clauses else ""
        where_str = f"WHERE {where_clause}" if where_clause else ""
        group_by_str = f"GROUP BY {group_by}" if group_by else ""

        # Build update set clause
        update_cols = []
        for col in select_columns:
            col_name = col.split(' AS ')[-1].strip() if ' AS ' in col else col.split()[-1]
            if col_name != merge_key:
                update_cols.append(f"{col_name} = SRC.{col_name}")

        update_str = ",\n".join(update_cols) if update_cols else ""

        # Build insert columns
        insert_cols = []
        for col in select_columns:
            col_name = col.split(' AS ')[-1].strip() if ' AS ' in col else col.split()[-1]
            insert_cols.append(col_name)

        insert_cols_str = ",\n".join(insert_cols)
        insert_vals_str = ",\n".join([f"SRC.{col}" for col in insert_cols])

        merge_template = Template(self.MERGE_TEMPLATE)
        merge_sql = merge_template.render(
            target_schema=target_schema,
            target_table=target_table,
            source_schema=source_schema,
            source_table=source_table,
            select_columns=select_cols_str,
            join_clauses=join_str,
            where_clause=where_str,
            group_by_clause=group_by_str,
            merge_condition=f"TGT.{merge_key} = SRC.{merge_key}",
            update_columns=update_str,
            insert_columns=insert_cols_str,
            insert_values=insert_vals_str
        )

        return merge_sql

    def _build_quality_checks(
        self,
        target_schema: str,
        target_table: str,
        target_metadata: TableMetadata = None
    ) -> str:
        """Build data quality checks."""
        quality_checks = f"""-- Validate NOT NULL columns
        SELECT COUNT(*) INTO V_ERROR_MESSAGE
        FROM {target_schema}.{target_table}
        WHERE 1=1"""

        if target_metadata:
            for col in target_metadata.columns:
                if not col.nullable:
                    quality_checks += f"\n        AND {col.name} IS NOT NULL"

        quality_checks += f"""
        GROUP BY 1
        HAVING COUNT(*) = 0;"""

        return quality_checks

    def generate_deployment_script(self) -> str:
        """
        Generate a deployment script for all procedures.

        Returns:
            Path to deployment script
        """
        logger.info("Generating deployment script")

        deployment_script = "-- Snowflake Migration - Stored Procedure Deployment Script\n"
        deployment_script += f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        deployment_script += f"-- Total Procedures: {len(self.generated_procedures)}\n\n"

        deployment_script += "USE ROLE SYSADMIN;\n\n"

        for proc_info in self.generated_procedures:
            deployment_script += f"-- Deploy: {proc_info['name']}\n"
            with open(proc_info['file'], 'r') as f:
                deployment_script += f.read()
            deployment_script += "\n\n"

        # Add execution script
        deployment_script += "-- Execute Procedures\n"
        deployment_script += "-- " + "=" * 50 + "\n\n"

        for proc_info in self.generated_procedures:
            deployment_script += f"CALL {proc_info['target'].split('.')[0]}.{proc_info['name']}(\n"
            deployment_script += "    P_LOAD_DATE => CURRENT_DATE(),\n"
            deployment_script += "    P_DEBUG_MODE => TRUE\n"
            deployment_script += ");\n\n"

        # Save deployment script
        output_file = self.output_dir / "00_DEPLOYMENT.sql"
        with open(output_file, 'w') as f:
            f.write(deployment_script)

        logger.info(f"Deployment script generated: {output_file}")
        return str(output_file)

    def get_generated_procedures(self) -> List[Dict]:
        """Get list of generated procedures."""
        return self.generated_procedures

    def generate_procedure_documentation(self) -> str:
        """
        Generate documentation for all procedures.

        Returns:
            Path to documentation file
        """
        logger.info("Generating procedure documentation")

        doc = "# Stored Procedure Documentation\n\n"
        doc += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for proc_info in self.generated_procedures:
            doc += f"## {proc_info['name']}\n\n"
            doc += f"**Target Table:** {proc_info['target']}\n"
            doc += f"**Source Mapping:** {proc_info['mapping']}\n"
            doc += f"**File:** {Path(proc_info['file']).name}\n\n"

            doc += "### Parameters\n"
            doc += "- `P_LOAD_DATE` (DATE): Load date for the data (default: CURRENT_DATE)\n"
            doc += "- `P_BATCH_ID` (VARCHAR): Batch identifier (default: auto-generated)\n"
            doc += "- `P_DEBUG_MODE` (BOOLEAN): Enable debug logging (default: FALSE)\n\n"

            doc += "### Returns\n"
            doc += "OBJECT containing:\n"
            doc += "- `STATUS`: Execution status (SUCCESS/FAILED)\n"
            doc += "- `ROWS_INSERTED`: Number of rows inserted\n"
            doc += "- `ROWS_UPDATED`: Number of rows updated\n"
            doc += "- `ROWS_DELETED`: Number of rows deleted\n"
            doc += "- `ERROR_MESSAGE`: Error message if failed\n"
            doc += "- `EXECUTION_TIME_SECONDS`: Total execution time\n"
            doc += "- `BATCH_ID`: Batch identifier\n\n"

            doc += "### Usage\n"
            doc += "```sql\n"
            doc += f"CALL {proc_info['target'].split('.')[0]}.{proc_info['name']}(\n"
            doc += "    P_LOAD_DATE => '2025-11-16'::DATE,\n"
            doc += "    P_DEBUG_MODE => TRUE\n"
            doc += ");\n"
            doc += "```\n\n"

        # Save documentation
        output_file = self.output_dir / "PROCEDURES.md"
        with open(output_file, 'w') as f:
            f.write(doc)

        logger.info(f"Procedure documentation generated: {output_file}")
        return str(output_file)
