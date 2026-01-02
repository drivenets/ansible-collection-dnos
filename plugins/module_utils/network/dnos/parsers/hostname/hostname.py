# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The hostname parser for DNOS.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


class HostnameParser(object):
    """Parser for hostname configuration"""

    def __init__(self, data=""):
        self.data = data or ""

    def parse(self):
        """Parse hostname configuration"""
        # Basic hostname extraction from data
        hostname_config = {}
        if self.data:
            for line in self.data.split("\n"):
                if "hostname" in line.lower():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        hostname_config["hostname"] = parts[1]
                        break
        return hostname_config
