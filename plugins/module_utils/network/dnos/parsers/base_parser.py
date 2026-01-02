# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
Base parser class for DNOS CLI output parsing.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import json
import re

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseDNOSParser(ABC):
    """
    Base parser class for DNOS CLI output parsing.
    Provides common functionality for all DNOS parsers including:
    - Standard parsing patterns
    - Error handling
    - Output normalization
    - JSON conversion utilities
    """

    def __init__(self, output: str = ""):
        """
        Initialize the parser.
        Args:
            output: Raw CLI output to parse
        """
        self.output = output.strip() if output else ""
        self.parsed_data = {}

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Parse the CLI output and return structured data.
        Returns:
            dict: Parsed configuration or operational data
        """
        pass

    def clean_output(self, text: str) -> str:
        """
        Clean CLI output by removing ANSI codes and extra whitespace.
        Args:
            text: Raw text to clean
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        text = ansi_escape.sub("", text)
        # Remove carriage returns and normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove extra whitespace while preserving structure
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines)

    def extract_table_data(
        self, text: str, headers: List[str], start_pattern: str = None, end_pattern: str = None
    ) -> List[Dict[str, str]]:
        """
        Extract tabular data from CLI output.
        Args:
            text: CLI output containing table
            headers: List of column headers
            start_pattern: Regex pattern to identify table start
            end_pattern: Regex pattern to identify table end
        Returns:
            list: List of dictionaries representing table rows
        """
        if not text or not headers:
            return []
        lines = text.split("\n")
        table_data = []
        in_table = start_pattern is None  # If no start pattern, assume we're in table
        for line in lines:
            line = line.strip()
            # Check for table start
            if start_pattern and re.search(start_pattern, line):
                in_table = True
                continue
            # Check for table end
            if end_pattern and re.search(end_pattern, line):
                in_table = False
                break
            # Skip empty lines and header separators
            if not in_table or not line or line.startswith("-") or line.startswith("="):
                continue
            # Skip header line (contains column names)
            if any(header.lower() in line.lower() for header in headers):
                continue
            # Parse data row
            row_data = self._parse_table_row(line, headers)
            if row_data:
                table_data.append(row_data)
        return table_data

    def _parse_table_row(self, line: str, headers: List[str]) -> Optional[Dict[str, str]]:
        """
        Parse a single table row based on column headers.
        Args:
            line: Table row text
            headers: Column headers
        Returns:
            dict: Parsed row data or None if parsing fails
        """
        # Split on multiple spaces (common in CLI tables)
        values = re.split(r"\s{2,}", line.strip())
        if len(values) < len(headers):
            # Try splitting on single space if multiple spaces don't work
            values = line.strip().split()
        if len(values) >= len(headers):
            return dict(zip(headers, values[: len(headers)]))
        return None

    def parse_key_value_pairs(
        self, text: str, separator: str = ":", multiline: bool = False
    ) -> Dict[str, str]:
        """
        Parse key-value pairs from CLI output.
        Args:
            text: Text containing key-value pairs
            separator: Character separating keys from values
            multiline: Whether values can span multiple lines
        Returns:
            dict: Parsed key-value pairs
        """
        if not text:
            return {}
        parsed = {}
        lines = text.split("\n")
        current_key = None
        current_value = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if separator in line:
                # Save previous key-value if exists
                if current_key and current_value:
                    parsed[current_key] = " ".join(current_value).strip()
                # Parse new key-value
                key, value = line.split(separator, 1)
                current_key = key.strip()
                current_value = [value.strip()] if value.strip() else []
            elif multiline and current_key and line:
                # Continuation of multiline value
                current_value.append(line)
        # Save final key-value
        if current_key and current_value:
            parsed[current_key] = " ".join(current_value).strip()
        return parsed

    def parse_list_items(
        self, text: str, item_pattern: str, extract_groups: bool = True
    ) -> List[Union[str, Dict[str, str]]]:
        """
        Parse list items from CLI output using regex patterns.
        Args:
            text: Text to parse
            item_pattern: Regex pattern to match list items
            extract_groups: Whether to extract named groups as dict
        Returns:
            list: Parsed list items
        """
        if not text or not item_pattern:
            return []
        items = []
        pattern = re.compile(item_pattern, re.MULTILINE)
        for match in pattern.finditer(text):
            if extract_groups and match.groupdict():
                items.append(match.groupdict())
            else:
                items.append(match.group(0))
        return items

    def convert_to_json(self, data: Any) -> str:
        """
        Convert parsed data to JSON format.
        Args:
            data: Data to convert
        Returns:
            str: JSON representation
        """
        try:
            return json.dumps(data, indent=2, sort_keys=True)
        except (TypeError, ValueError) as e:
            return json.dumps({"error": f"JSON conversion failed: {str(e)}"})

    def validate_output(self, required_patterns: List[str]) -> bool:
        """
        Validate that output contains required patterns.
        Args:
            required_patterns: List of regex patterns that must be present
        Returns:
            bool: True if all patterns found
        """
        if not self.output:
            return False
        for pattern in required_patterns:
            if not re.search(pattern, self.output, re.IGNORECASE):
                return False
        return True
