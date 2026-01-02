# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
System information parser for DNOS.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import re

from typing import Any, Dict, List

from .base_parser import BaseDNOSParser


class SystemParser(BaseDNOSParser):
    """Parser for DNOS system information and configuration."""

    def parse(self) -> Dict[str, Any]:
        """
        Parse system information from various show commands.
        Returns:
            dict: Comprehensive system information
        """
        if not self.output:
            return {}
        parsed = {
            "version": self.parse_version(),
            "hardware": self.parse_hardware(),
            "uptime": self.parse_uptime(),
            "processes": self.parse_processes(),
            "memory": self.parse_memory(),
            "environment": self.parse_environment(),
            "configuration": self.parse_configuration(),
        }
        # Remove empty sections
        return {k: v for k, v in parsed.items() if v}

    def parse_version(self) -> Dict[str, str]:
        """Parse version information from 'show version' output."""
        patterns = {
            "software_version": r"Software Version[:\s]+([^\n\r]+)",
            "build_date": r"Build Date[:\s]+([^\n\r]+)",
            "build_version": r"Build Version[:\s]+([^\n\r]+)",
            "system_image": r"System Image[:\s]+([^\n\r]+)",
            "kernel_version": r"Kernel Version[:\s]+([^\n\r]+)",
            "compiler": r"Compiled with[:\s]+([^\n\r]+)",
            "copyright": r"Copyright[:\s]+([^\n\r]+)",
        }
        version_info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, self.output, re.IGNORECASE)
            if match:
                version_info[key] = match.group(1).strip()
        return version_info

    def parse_hardware(self) -> Dict[str, Any]:
        """Parse hardware information including chassis and modules."""
        hardware = {}
        # Chassis information
        chassis_patterns = {
            "model": r"System Model[:\s]+([^\n\r]+)",
            "serial_number": r"System Serial Number[:\s]+([^\n\r]+)",
            "part_number": r"System Part Number[:\s]+([^\n\r]+)",
            "mac_address": r"System MAC Address[:\s]+([^\n\r]+)",
            "processor": r"Processor[:\s]+([^\n\r]+)",
            "processor_speed": r"Processor Speed[:\s]+([^\n\r]+)",
            "total_memory": r"Total Memory[:\s]+([^\n\r]+)",
        }
        for key, pattern in chassis_patterns.items():
            match = re.search(pattern, self.output, re.IGNORECASE)
            if match:
                hardware[key] = match.group(1).strip()
        # Module information
        modules = self.parse_modules()
        if modules:
            hardware["modules"] = modules
        return hardware

    def parse_modules(self) -> List[Dict[str, str]]:
        """Parse module/linecard information."""
        # Look for module table in output
        module_patterns = [
            r"Module\s+Type\s+Model\s+Serial\s+Status",
            r"Slot\s+Module\s+Type\s+Model\s+Serial",
        ]
        for pattern in module_patterns:
            if re.search(pattern, self.output, re.IGNORECASE):
                headers = ["slot", "type", "model", "serial", "status"]
                return self.extract_table_data(
                    self.output, headers, start_pattern=pattern, end_pattern=r"^\s*$"
                )
        return []

    def parse_uptime(self) -> Dict[str, str]:
        """Parse system uptime information."""
        uptime_patterns = {
            "uptime": r"System uptime[:\s]+([^\n\r]+)",
            "last_reload": r"Last reload[:\s]+([^\n\r]+)",
            "reload_reason": r"Reload reason[:\s]+([^\n\r]+)",
            "current_time": r"Current time[:\s]+([^\n\r]+)",
        }
        uptime_info = {}
        for key, pattern in uptime_patterns.items():
            match = re.search(pattern, self.output, re.IGNORECASE)
            if match:
                uptime_info[key] = match.group(1).strip()
        return uptime_info

    def parse_processes(self) -> Dict[str, Any]:
        """Parse process information from 'show processes' output."""
        # CPU utilization
        cpu_pattern = r"CPU utilization[:\s]+([0-9.]+)%"
        cpu_match = re.search(cpu_pattern, self.output, re.IGNORECASE)
        processes_info = {}
        if cpu_match:
            processes_info["cpu_utilization"] = float(cpu_match.group(1))
        # Process table
        if "PID" in self.output and "COMMAND" in self.output:
            headers = ["pid", "user", "cpu", "memory", "vsz", "rss", "command"]
            process_list = self.extract_table_data(
                self.output, headers, start_pattern=r"PID.*COMMAND", end_pattern=r"^\s*$"
            )
            if process_list:
                processes_info["processes"] = process_list
        return processes_info

    def parse_memory(self) -> Dict[str, Any]:
        """Parse memory information."""
        memory_patterns = {
            "total": r"Total memory[:\s]+([0-9,]+)",
            "used": r"Used memory[:\s]+([0-9,]+)",
            "free": r"Free memory[:\s]+([0-9,]+)",
            "buffers": r"Buffers[:\s]+([0-9,]+)",
            "cached": r"Cached[:\s]+([0-9,]+)",
        }
        memory_info = {}
        for key, pattern in memory_patterns.items():
            match = re.search(pattern, self.output, re.IGNORECASE)
            if match:
                # Remove commas and convert to int
                value = match.group(1).replace(",", "")
                try:
                    memory_info[key] = int(value)
                except ValueError:
                    memory_info[key] = value
        return memory_info

    def parse_environment(self) -> Dict[str, Any]:
        """Parse environmental information (temperature, fans, power)."""
        env_info = {}
        # Temperature information
        temp_pattern = r"Temperature[:\s]+([0-9.]+)"
        temp_match = re.search(temp_pattern, self.output, re.IGNORECASE)
        if temp_match:
            env_info["temperature"] = float(temp_match.group(1))
        # Fan status
        fan_patterns = [
            r"Fan\s+(\d+)[:\s]+(\w+)",
            r"(\w+)\s+fan[:\s]+(\w+)",
        ]
        fans = []
        for pattern in fan_patterns:
            matches = re.finditer(pattern, self.output, re.IGNORECASE)
            for match in matches:
                fans.append({"id": match.group(1), "status": match.group(2)})
        if fans:
            env_info["fans"] = fans
        # Power supply status
        power_pattern = r"Power Supply\s+(\d+)[:\s]+(\w+)"
        power_matches = re.finditer(power_pattern, self.output, re.IGNORECASE)
        power_supplies = []
        for match in power_matches:
            power_supplies.append({"id": match.group(1), "status": match.group(2)})
        if power_supplies:
            env_info["power_supplies"] = power_supplies
        return env_info

    def parse_configuration(self) -> Dict[str, str]:
        """Parse configuration-related information."""
        config_patterns = {
            "config_register": r"Configuration register[:\s]+([^\n\r]+)",
            "boot_image": r"Boot image[:\s]+([^\n\r]+)",
            "config_file": r"Configuration file[:\s]+([^\n\r]+)",
            "config_last_modified": r"Configuration last modified[:\s]+([^\n\r]+)",
        }
        config_info = {}
        for key, pattern in config_patterns.items():
            match = re.search(pattern, self.output, re.IGNORECASE)
            if match:
                config_info[key] = match.group(1).strip()
        return config_info
