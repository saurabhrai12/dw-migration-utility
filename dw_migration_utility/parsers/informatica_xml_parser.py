"""
Informatica XML parser for extracting mapping and transformation logic.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import xmltodict
from loguru import logger
from dataclasses import dataclass, field, asdict


@dataclass
class SourceDefinition:
    """Source table definition."""
    name: str
    database_type: str
    database_name: Optional[str] = None
    owner: Optional[str] = None
    columns: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TargetDefinition:
    """Target table definition."""
    name: str
    database_type: str
    database_name: Optional[str] = None
    owner: Optional[str] = None
    columns: List[Dict[str, Any]] = field(default_factory=list)
    load_type: str = "INSERT"  # INSERT, UPDATE, DELETE, UPSERT


@dataclass
class Transformation:
    """Informatica transformation."""
    name: str
    type: str  # Expression, Aggregator, Filter, Joiner, Lookup, Router, Sorter, etc.
    description: Optional[str] = None
    ports: List[Dict[str, Any]] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    expressions: Dict[str, str] = field(default_factory=dict)


@dataclass
class Connector:
    """Connection between transformations."""
    from_transformation: str
    from_instance: str
    to_transformation: str
    to_instance: str
    from_field: str
    to_field: str


@dataclass
class InformaticaMapping:
    """Complete Informatica mapping."""
    name: str
    folder: Optional[str] = None
    description: Optional[str] = None
    sources: List[SourceDefinition] = field(default_factory=list)
    targets: List[TargetDefinition] = field(default_factory=list)
    transformations: List[Transformation] = field(default_factory=list)
    connectors: List[Connector] = field(default_factory=list)
    session_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'folder': self.folder,
            'description': self.description,
            'sources': [asdict(s) for s in self.sources],
            'targets': [asdict(t) for t in self.targets],
            'transformations': [asdict(tr) for tr in self.transformations],
            'connectors': [asdict(c) for c in self.connectors],
            'session_config': self.session_config
        }


class InformaticaXMLParser:
    """Parser for Informatica XML mapping files."""

    def __init__(self, xml_path: str):
        """
        Initialize parser.

        Args:
            xml_path: Path to Informatica XML file
        """
        self.xml_path = Path(xml_path)
        self.mapping = None

    def parse(self) -> InformaticaMapping:
        """
        Parse Informatica XML file.

        Returns:
            InformaticaMapping object
        """
        logger.info(f"Parsing Informatica XML: {self.xml_path}")

        try:
            with open(self.xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()

            # Parse XML to dictionary
            xml_dict = xmltodict.parse(xml_content)

            # Extract mapping information
            self.mapping = self._extract_mapping(xml_dict)

            logger.info(f"Successfully parsed mapping: {self.mapping.name}")
            return self.mapping

        except Exception as e:
            logger.error(f"Failed to parse XML file: {e}")
            raise

    def _extract_mapping(self, xml_dict: Dict) -> InformaticaMapping:
        """Extract mapping from XML dictionary."""

        # Navigate to mapping section (structure varies by Informatica version)
        mapping_data = self._find_mapping_data(xml_dict)

        if not mapping_data:
            raise ValueError("Could not find mapping data in XML")

        mapping_name = mapping_data.get('@NAME', 'Unknown')
        mapping_desc = mapping_data.get('@DESCRIPTION', '')

        mapping = InformaticaMapping(
            name=mapping_name,
            description=mapping_desc
        )

        # Extract sources
        sources = self._extract_sources(mapping_data)
        mapping.sources.extend(sources)

        # Extract targets
        targets = self._extract_targets(mapping_data)
        mapping.targets.extend(targets)

        # Extract transformations
        transformations = self._extract_transformations(mapping_data)
        mapping.transformations.extend(transformations)

        # Extract connectors
        connectors = self._extract_connectors(mapping_data)
        mapping.connectors.extend(connectors)

        return mapping

    def _find_mapping_data(self, xml_dict: Dict) -> Optional[Dict]:
        """Find mapping data in XML structure."""
        # Try common paths in Informatica XML structure
        if 'POWERMART' in xml_dict:
            powermart = xml_dict['POWERMART']
            if 'REPOSITORY' in powermart:
                repo = powermart['REPOSITORY']
                if 'FOLDER' in repo:
                    folder = repo['FOLDER']
                    if isinstance(folder, list):
                        folder = folder[0]
                    if 'MAPPING' in folder:
                        mapping = folder['MAPPING']
                        if isinstance(mapping, list):
                            return mapping[0]
                        return mapping

        return None

    def _extract_sources(self, mapping_data: Dict) -> List[SourceDefinition]:
        """Extract source definitions."""
        sources = []

        source_nodes = mapping_data.get('SOURCE', [])
        if not isinstance(source_nodes, list):
            source_nodes = [source_nodes] if source_nodes else []

        for source in source_nodes:
            source_def = SourceDefinition(
                name=source.get('@NAME', ''),
                database_type=source.get('@DATABASETYPE', 'Oracle'),
                database_name=source.get('@DBDNAME', ''),
                owner=source.get('@OWNERNAME', '')
            )

            # Extract source fields
            source_fields = source.get('SOURCEFIELD', [])
            if not isinstance(source_fields, list):
                source_fields = [source_fields] if source_fields else []

            for field in source_fields:
                col_info = {
                    'name': field.get('@NAME', ''),
                    'datatype': field.get('@DATATYPE', ''),
                    'precision': field.get('@PRECISION', ''),
                    'scale': field.get('@SCALE', ''),
                    'nullable': field.get('@NULLABLE', 'NULL') == 'NULL',
                    'key_type': field.get('@KEYTYPE', '')
                }
                source_def.columns.append(col_info)

            sources.append(source_def)

        return sources

    def _extract_targets(self, mapping_data: Dict) -> List[TargetDefinition]:
        """Extract target definitions."""
        targets = []

        target_nodes = mapping_data.get('TARGET', [])
        if not isinstance(target_nodes, list):
            target_nodes = [target_nodes] if target_nodes else []

        for target in target_nodes:
            target_def = TargetDefinition(
                name=target.get('@NAME', ''),
                database_type=target.get('@DATABASETYPE', 'Oracle'),
                database_name=target.get('@DBDNAME', ''),
                owner=target.get('@OWNERNAME', '')
            )

            # Extract target fields
            target_fields = target.get('TARGETFIELD', [])
            if not isinstance(target_fields, list):
                target_fields = [target_fields] if target_fields else []

            for field in target_fields:
                col_info = {
                    'name': field.get('@NAME', ''),
                    'datatype': field.get('@DATATYPE', ''),
                    'precision': field.get('@PRECISION', ''),
                    'scale': field.get('@SCALE', ''),
                    'nullable': field.get('@NULLABLE', 'NULL') == 'NULL',
                    'key_type': field.get('@KEYTYPE', '')
                }
                target_def.columns.append(col_info)

            targets.append(target_def)

        return targets

    def _extract_transformations(self, mapping_data: Dict) -> List[Transformation]:
        """Extract transformations."""
        transformations = []

        # Get all transformation nodes
        transform_nodes = mapping_data.get('TRANSFORMATION', [])
        if not isinstance(transform_nodes, list):
            transform_nodes = [transform_nodes] if transform_nodes else []

        for trans in transform_nodes:
            transformation = Transformation(
                name=trans.get('@NAME', ''),
                type=trans.get('@TYPE', ''),
                description=trans.get('@DESCRIPTION', '')
            )

            # Extract transformation fields/ports
            trans_fields = trans.get('TRANSFORMFIELD', [])
            if not isinstance(trans_fields, list):
                trans_fields = [trans_fields] if trans_fields else []

            for field in trans_fields:
                port_info = {
                    'name': field.get('@NAME', ''),
                    'datatype': field.get('@DATATYPE', ''),
                    'precision': field.get('@PRECISION', ''),
                    'scale': field.get('@SCALE', ''),
                    'port_type': field.get('@PORTTYPE', ''),  # INPUT, OUTPUT, VARIABLE
                    'expression': field.get('@EXPRESSION', ''),
                    'default_value': field.get('@DEFAULTVALUE', '')
                }
                transformation.ports.append(port_info)

                # Store expressions separately for easy access
                if port_info['expression']:
                    transformation.expressions[port_info['name']] = port_info['expression']

            # Extract properties
            table_attrs = trans.get('TABLEATTRIBUTE', [])
            if not isinstance(table_attrs, list):
                table_attrs = [table_attrs] if table_attrs else []

            for attr in table_attrs:
                prop_name = attr.get('@NAME', '')
                prop_value = attr.get('@VALUE', '')
                transformation.properties[prop_name] = prop_value

            transformations.append(transformation)

        return transformations

    def _extract_connectors(self, mapping_data: Dict) -> List[Connector]:
        """Extract connectors (data flow connections)."""
        connectors = []

        connector_nodes = mapping_data.get('CONNECTOR', [])
        if not isinstance(connector_nodes, list):
            connector_nodes = [connector_nodes] if connector_nodes else []

        for conn in connector_nodes:
            connector = Connector(
                from_transformation=conn.get('@FROMTRANSFORMATION', ''),
                from_instance=conn.get('@FROMINSTANCE', ''),
                to_transformation=conn.get('@TOTRANSFORMATION', ''),
                to_instance=conn.get('@TOINSTANCE', ''),
                from_field=conn.get('@FROMFIELD', ''),
                to_field=conn.get('@TOFIELD', '')
            )
            connectors.append(connector)

        return connectors

    def get_data_flow(self) -> List[Dict[str, Any]]:
        """
        Get data flow from sources to targets.

        Returns:
            List of data flow steps
        """
        if not self.mapping:
            return []

        flow = []

        # Build transformation lookup
        trans_lookup = {t.name: t for t in self.mapping.transformations}

        # Track data flow through connectors
        for conn in self.mapping.connectors:
            flow_step = {
                'from': f"{conn.from_transformation}.{conn.from_field}",
                'to': f"{conn.to_transformation}.{conn.to_field}",
                'from_type': trans_lookup.get(conn.from_transformation, {}).type if conn.from_transformation in trans_lookup else 'SOURCE',
                'to_type': trans_lookup.get(conn.to_transformation, {}).type if conn.to_transformation in trans_lookup else 'TARGET'
            }
            flow.append(flow_step)

        return flow

    def get_transformation_by_name(self, name: str) -> Optional[Transformation]:
        """Get transformation by name."""
        if not self.mapping:
            return None

        for trans in self.mapping.transformations:
            if trans.name == name:
                return trans

        return None

    def get_lineage_for_target_column(self, target_name: str, column_name: str) -> List[str]:
        """
        Trace lineage for a target column back to source.

        Args:
            target_name: Target table name
            column_name: Target column name

        Returns:
            List of transformation steps in lineage
        """
        if not self.mapping:
            return []

        lineage = []
        current_field = column_name
        current_trans = target_name

        # Trace backwards through connectors
        while True:
            found = False
            for conn in self.mapping.connectors:
                if conn.to_transformation == current_trans and conn.to_field == current_field:
                    lineage.insert(0, f"{conn.from_transformation}.{conn.from_field}")
                    current_trans = conn.from_transformation
                    current_field = conn.from_field
                    found = True
                    break

            if not found:
                break

        return lineage

    def export_to_json(self, output_path: str) -> None:
        """
        Export mapping to JSON file.

        Args:
            output_path: Output file path
        """
        if not self.mapping:
            logger.warning("No mapping to export")
            return

        import json
        with open(output_path, 'w') as f:
            json.dump(self.mapping.to_dict(), f, indent=2)

        logger.info(f"Mapping exported to: {output_path}")


def parse_multiple_xml_files(xml_directory: str, pattern: str = "*.xml") -> List[InformaticaMapping]:
    """
    Parse multiple Informatica XML files.

    Args:
        xml_directory: Directory containing XML files
        pattern: File pattern to match

    Returns:
        List of InformaticaMapping objects
    """
    mappings = []
    xml_dir = Path(xml_directory)

    if not xml_dir.exists():
        logger.error(f"Directory not found: {xml_directory}")
        return mappings

    xml_files = list(xml_dir.glob(pattern))
    logger.info(f"Found {len(xml_files)} XML files to parse")

    for xml_file in xml_files:
        try:
            parser = InformaticaXMLParser(str(xml_file))
            mapping = parser.parse()
            mappings.append(mapping)
        except Exception as e:
            logger.error(f"Failed to parse {xml_file}: {e}")
            continue

    logger.info(f"Successfully parsed {len(mappings)} mappings")
    return mappings
