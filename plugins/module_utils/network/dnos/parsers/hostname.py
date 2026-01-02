# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The hostname parser for DNOS.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import re

from typing import Dict, Optional


class HostnameParser:
    """Parser for DNOS hostname configuration."""

    def __init__(self, output: str = ""):
        """
        Initialize the parser.
        Args:
            output: The output from 'show system name' command
        """
        self.output = output

    def parse_hostname(self, output: str = None) -> Dict[str, Optional[str]]:
        """
        Parse hostname from device output.
        Based on RST documentation, the output format is:
        System Name: dnRouter
        Returns:
            dict: Parsed hostname configuration
        """
        parsed = {}
        # Use provided output or instance output
        if output is not None:
            parse_text = output
        else:
            parse_text = self.output
        if not parse_text:
            return parsed
        # Match pattern: System Name: <hostname>
        match = re.search(r"System Name:\s+(\S+)", parse_text, re.MULTILINE)
        if match:
            parsed["hostname"] = match.group(1)
        return parsed

    def parse_running_config(self, config: str) -> Dict[str, Optional[str]]:
        """
        Parse hostname from running configuration.
        In DNOS configuration, hostname appears as:
        system
          name <hostname>
        Args:
            config: Running configuration text
        Returns:
            dict: Parsed hostname configuration
        """
        parsed = {}
        if not config:
            return parsed
        # Look for system name configuration
        # Handle both inline and multiline formats
        patterns = [
            r"system\s+name\s+(\S+)",  # Inline format
            r"system\s*\n\s*name\s+(\S+)",  # Multiline format
        ]
        for pattern in patterns:
            match = re.search(pattern, config, re.MULTILINE | re.DOTALL)
            if match:
                parsed["hostname"] = match.group(1)
                break
        return parsed
