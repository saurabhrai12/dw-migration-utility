"""
Fuzzy matching algorithms for schema and column mapping.
"""
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from loguru import logger


class FuzzyMatcher:
    """Fuzzy matching for table and column names."""

    def __init__(
        self,
        threshold: float = 0.85,
        ignore_prefixes: List[str] = None,
        ignore_suffixes: List[str] = None
    ):
        """
        Initialize fuzzy matcher.

        Args:
            threshold: Minimum similarity score (0-1)
            ignore_prefixes: List of prefixes to ignore in matching
            ignore_suffixes: List of suffixes to ignore in matching
        """
        self.threshold = threshold * 100  # fuzzywuzzy uses 0-100 scale
        self.ignore_prefixes = ignore_prefixes or ['STG_', 'TMP_', 'HIST_', 'TEMP_']
        self.ignore_suffixes = ignore_suffixes or ['_BACKUP', '_OLD', '_BAK', '_TMP']

    def normalize_name(self, name: str) -> str:
        """
        Normalize a table/column name for matching.

        Args:
            name: Name to normalize

        Returns:
            Normalized name
        """
        normalized = name.upper().strip()

        # Remove prefixes
        for prefix in self.ignore_prefixes:
            if normalized.startswith(prefix.upper()):
                normalized = normalized[len(prefix):]
                break

        # Remove suffixes
        for suffix in self.ignore_suffixes:
            if normalized.endswith(suffix.upper()):
                normalized = normalized[:-len(suffix)]
                break

        return normalized

    def find_best_match(
        self,
        source_name: str,
        target_names: List[str],
        use_normalization: bool = True
    ) -> Optional[Tuple[str, float, str]]:
        """
        Find best match for a source name in target names.

        Args:
            source_name: Name to match
            target_names: List of potential matches
            use_normalization: Whether to normalize names before matching

        Returns:
            Tuple of (matched_name, score, match_type) or None
        """
        if not target_names:
            return None

        # Try exact match first
        for target in target_names:
            if source_name.upper() == target.upper():
                logger.debug(f"Exact match found: {source_name} -> {target}")
                return (target, 1.0, 'exact')

        # Try normalized exact match
        if use_normalization:
            normalized_source = self.normalize_name(source_name)
            for target in target_names:
                if normalized_source == self.normalize_name(target):
                    logger.debug(f"Normalized exact match: {source_name} -> {target}")
                    return (target, 0.95, 'normalized_exact')

        # Try fuzzy matching
        if use_normalization:
            search_name = self.normalize_name(source_name)
            search_targets = {self.normalize_name(t): t for t in target_names}
            match_result = process.extractOne(search_name, search_targets.keys(), scorer=fuzz.ratio)
        else:
            search_targets = {t: t for t in target_names}
            match_result = process.extractOne(source_name, target_names, scorer=fuzz.ratio)

        if match_result and match_result[1] >= self.threshold:
            if use_normalization:
                matched_name = search_targets[match_result[0]]
            else:
                matched_name = match_result[0]

            score = match_result[1] / 100.0
            logger.debug(f"Fuzzy match: {source_name} -> {matched_name} (score: {score:.2f})")
            return (matched_name, score, 'fuzzy')

        logger.debug(f"No match found for: {source_name}")
        return None

    def find_multiple_matches(
        self,
        source_name: str,
        target_names: List[str],
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find top N matches for a source name.

        Args:
            source_name: Name to match
            target_names: List of potential matches
            top_n: Number of top matches to return

        Returns:
            List of tuples (matched_name, score)
        """
        normalized_source = self.normalize_name(source_name)
        search_targets = {self.normalize_name(t): t for t in target_names}

        matches = process.extract(
            normalized_source,
            search_targets.keys(),
            scorer=fuzz.ratio,
            limit=top_n
        )

        results = []
        for match in matches:
            if match[1] >= self.threshold:
                original_name = search_targets[match[0]]
                score = match[1] / 100.0
                results.append((original_name, score))

        return results

    def match_by_token_similarity(
        self,
        source_name: str,
        target_names: List[str]
    ) -> Optional[Tuple[str, float]]:
        """
        Match using token-based similarity (good for abbreviations).

        Args:
            source_name: Name to match
            target_names: List of potential matches

        Returns:
            Tuple of (matched_name, score) or None
        """
        # Tokenize source name
        source_tokens = self._tokenize(source_name)

        best_match = None
        best_score = 0

        for target in target_names:
            target_tokens = self._tokenize(target)

            # Calculate token set ratio
            score = fuzz.token_set_ratio(
                ' '.join(source_tokens),
                ' '.join(target_tokens)
            ) / 100.0

            if score > best_score and score >= (self.threshold / 100.0):
                best_score = score
                best_match = target

        if best_match:
            logger.debug(f"Token match: {source_name} -> {best_match} (score: {best_score:.2f})")
            return (best_match, best_score)

        return None

    def _tokenize(self, name: str) -> List[str]:
        """
        Tokenize a name by splitting on underscores and camelCase.

        Args:
            name: Name to tokenize

        Returns:
            List of tokens
        """
        # Split on underscores
        tokens = name.split('_')

        # Split camelCase
        expanded_tokens = []
        for token in tokens:
            # Insert space before uppercase letters
            spaced = re.sub(r'([A-Z])', r' \1', token).strip()
            expanded_tokens.extend(spaced.split())

        # Filter out empty tokens and normalize
        return [t.upper() for t in expanded_tokens if t]

    def match_columns_by_metadata(
        self,
        source_columns: List[Dict],
        target_columns: List[Dict]
    ) -> Dict[str, str]:
        """
        Match columns using metadata (data type, position, etc.).

        Args:
            source_columns: List of source column dictionaries
            target_columns: List of target column dictionaries

        Returns:
            Dictionary mapping source column names to target column names
        """
        mappings = {}

        for src_col in source_columns:
            src_name = src_col['name']
            src_type = src_col.get('data_type', '')

            best_match = None
            best_score = 0

            for tgt_col in target_columns:
                tgt_name = tgt_col['name']
                tgt_type = tgt_col.get('data_type', '')

                # Name similarity
                name_score = fuzz.ratio(
                    self.normalize_name(src_name),
                    self.normalize_name(tgt_name)
                ) / 100.0

                # Data type similarity boost
                type_boost = 0.1 if self._types_compatible(src_type, tgt_type) else 0

                # Combined score
                total_score = name_score + type_boost

                if total_score > best_score:
                    best_score = total_score
                    best_match = tgt_name

            if best_score >= (self.threshold / 100.0):
                mappings[src_name] = best_match
                logger.debug(f"Column match: {src_name} -> {best_match} (score: {best_score:.2f})")

        return mappings

    def _types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two data types are compatible."""
        type1_upper = type1.upper()
        type2_upper = type2.upper()

        # Numeric types
        numeric_types = ['NUMBER', 'INTEGER', 'INT', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE']
        if any(t in type1_upper for t in numeric_types) and any(t in type2_upper for t in numeric_types):
            return True

        # String types
        string_types = ['VARCHAR', 'CHAR', 'TEXT', 'STRING']
        if any(t in type1_upper for t in string_types) and any(t in type2_upper for t in string_types):
            return True

        # Date types
        date_types = ['DATE', 'TIMESTAMP', 'DATETIME']
        if any(t in type1_upper for t in date_types) and any(t in type2_upper for t in date_types):
            return True

        # Exact match
        return type1_upper == type2_upper

    def calculate_table_similarity(
        self,
        source_table: Dict,
        target_table: Dict
    ) -> float:
        """
        Calculate overall similarity between two tables.

        Args:
            source_table: Source table metadata
            target_table: Target table metadata

        Returns:
            Similarity score (0-1)
        """
        scores = []

        # Name similarity (40% weight)
        name_score = fuzz.ratio(
            self.normalize_name(source_table['table_name']),
            self.normalize_name(target_table['table_name'])
        ) / 100.0
        scores.append(name_score * 0.4)

        # Column count similarity (20% weight)
        src_col_count = len(source_table.get('columns', []))
        tgt_col_count = len(target_table.get('columns', []))
        if src_col_count > 0 and tgt_col_count > 0:
            col_count_score = 1.0 - abs(src_col_count - tgt_col_count) / max(src_col_count, tgt_col_count)
            scores.append(col_count_score * 0.2)

        # Primary key similarity (20% weight)
        src_pks = set(source_table.get('primary_keys', []))
        tgt_pks = set(target_table.get('primary_keys', []))
        if src_pks and tgt_pks:
            pk_intersection = len(src_pks.intersection(tgt_pks))
            pk_union = len(src_pks.union(tgt_pks))
            pk_score = pk_intersection / pk_union if pk_union > 0 else 0
            scores.append(pk_score * 0.2)

        # Column name overlap (20% weight)
        src_col_names = {self.normalize_name(c['name']) for c in source_table.get('columns', [])}
        tgt_col_names = {self.normalize_name(c['name']) for c in target_table.get('columns', [])}
        if src_col_names and tgt_col_names:
            col_intersection = len(src_col_names.intersection(tgt_col_names))
            col_union = len(src_col_names.union(tgt_col_names))
            col_score = col_intersection / col_union if col_union > 0 else 0
            scores.append(col_score * 0.2)

        return sum(scores)
