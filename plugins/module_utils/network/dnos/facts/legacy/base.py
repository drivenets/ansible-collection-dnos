# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type


import platform
import re

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import (
    get_capabilities,
    run_commands,
)


class FactsBase(object):
    COMMANDS = list()

    def __init__(self, module):
        self.module = module
        self.facts = dict()
        self.warnings = list()
        self.responses = None

    def populate(self):
        self.responses = run_commands(self.module, commands=self.COMMANDS, check_rc=False)

    def run(self, cmd):
        return run_commands(self.module, commands=cmd, check_rc=False)


class Default(FactsBase):
    COMMANDS = ["show system | no-more"]

    def populate(self):
        super(Default, self).populate()
        self.facts.update(self.platform_facts())
        data = self.responses[0]
        self.facts.update(self.parse_system_info(data))

    def parse_system_info(self, data):
        facts = {}

        # Parse basic system info
        system_name_match = re.search(r"System Name: (.+?),\s*System-Id: (.+)", data)
        if system_name_match:
            facts["hostname"] = system_name_match.group(1).strip()
            facts["system_id"] = system_name_match.group(2).strip()

        # Parse system type and family
        system_type_match = re.search(r"System Type: (.+?),\s*Family: (.+)", data)
        if system_type_match:
            facts["system_type"] = system_type_match.group(1).strip()
            facts["family"] = system_type_match.group(2).strip()

        # Parse enterprise ID
        enterprise_id_match = re.search(r"Enterprise-Id: (\d+)", data)
        if enterprise_id_match:
            facts["enterprise_id"] = int(enterprise_id_match.group(1))

        # Parse description
        desc_match = re.search(r"Description: (.+)", data)
        if desc_match:
            facts["description"] = desc_match.group(1).strip()

        # Parse version info
        version_match = re.search(r"Version: DNOS \[(.+?)\] build \[(.+?)\]", data)
        if version_match:
            facts["version"] = version_match.group(1)
            facts["build"] = version_match.group(2)

        # Parse environment info
        env_match = re.search(
            r"Environment:\s+Location: (.+?)\s+Floor: (.+?)\s+Rack: (.+?)\s+", data, re.DOTALL
        )
        if env_match:
            facts["environment"] = {
                "location": env_match.group(1).strip(),
                "floor": env_match.group(2).strip(),
                "rack": env_match.group(3).strip(),
            }

        # Parse uptime info
        uptime_match = re.search(r"System Uptime: (.+)", data)
        if uptime_match:
            facts["uptime"] = uptime_match.group(1).strip()

        # Parse system status
        status_match = re.search(r"System status: (.+)", data)
        if status_match:
            facts["status"] = status_match.group(1).strip()

        # Parse contact info
        contact_match = re.search(r"Contact: (.+)", data)
        if contact_match:
            facts["contact"] = contact_match.group(1).strip()

        # Parse components table
        components = []
        table_lines = re.findall(
            r"\|\s+(\w+)\s+\|\s+(\d+)\s+\|\s+(\w*)\s+\|\s+(\S+.*?)\s+\|\s+(\S+.*?)\s+\|\s+(\S+.*?)\s+\|\s+(\S+.*?)\s+\|\s+(\S*)\s+\|",
            data,
        )
        for line in table_lines:
            component = {
                "type": line[0].strip(),
                "id": line[1].strip(),
                "admin": line[2].strip(),
                "operational": line[3].strip(),
                "model": line[4].strip(),
                "uptime": line[5].strip(),
                "description": line[6].strip(),
                "serial_number": line[7].strip(),
            }
            components.append(component)
        facts["components"] = components

        return facts

    def platform_facts(self):
        platform_facts = {}

        resp = get_capabilities(self.module)
        device_info = resp["device_info"]

        platform_facts["system"] = device_info["network_os"]

        # Map standard ansible network OS facts
        fact_map = {
            "serialnum": "network_os_serial",
            "model": "network_os_model",
            "version": "network_os_version",
            "hostname": "network_os_hostname",
            "image": "network_os_image",
        }

        for fact, info_key in fact_map.items():
            val = device_info.get(info_key)
            if val:
                platform_facts[fact] = val

        platform_facts["api"] = resp["network_api"]
        platform_facts["python_version"] = platform.python_version()

        return platform_facts


class Hardware(FactsBase):
    COMMANDS = ["show system hardware | no-more"]

    def populate(self):
        super(Hardware, self).populate()
        data = self.responses[0]

        # Initialize hardware facts dictionary
        hardware_facts = {}

        # Parse basic hardware info
        hardware_facts.update(self.parse_basic_info(data))

        # Parse CPU information
        hardware_facts.update(self.parse_cpu_info(data))

        # Parse memory information
        hardware_facts.update(self.parse_memory_info(data))

        # Parse disk information
        hardware_facts.update(self.parse_disk_info(data))

        # Parse BIOS and firmware versions
        hardware_facts.update(self.parse_firmware_info(data))

        # Parse power supply information
        hardware_facts.update(self.parse_psu_info(data))

        # Parse temperature information
        hardware_facts.update(self.parse_temperature_info(data))

        # Parse fan information
        hardware_facts.update(self.parse_fan_info(data))

        self.facts.update(hardware_facts)

    def parse_basic_info(self, data):
        facts = {}

        # Parse model and hardware info
        model_match = re.search(r"Model: (.+)", data)
        if model_match:
            facts["model"] = model_match.group(1).strip()

        hw_model_match = re.search(r"Hardware Model: (.+?) \(configured: (.+?)\)", data)
        if hw_model_match:
            facts["hardware_model"] = hw_model_match.group(1).strip()
            facts["configured_model"] = hw_model_match.group(2).strip()

        # Parse serial number and MAC
        serial_match = re.search(r"Serial Number: (.+)", data)
        if serial_match:
            facts["serial_number"] = serial_match.group(1).strip()

        mac_match = re.search(r"Chassis MAC: (.+)", data)
        if mac_match:
            facts["chassis_mac"] = mac_match.group(1).strip()

        # Parse OS and ONIE version
        os_match = re.search(r"Host Operating System: (.+)", data)
        if os_match:
            facts["host_os"] = os_match.group(1).strip()

        onie_match = re.search(r"ONIE version: (.+)", data)
        if onie_match:
            facts["onie_version"] = onie_match.group(1).strip()

        return facts

    def parse_cpu_info(self, data):
        facts = {"cpu": {}}

        # Parse CPU model and threads
        cpu_model_match = re.search(r"CPU Model\s+\|\s+(.+?)\s+\|", data)
        if cpu_model_match:
            facts["cpu"]["model"] = cpu_model_match.group(1).strip()

        threads_match = re.search(r"Hyper-Threads\s+\|\s+(.+?)\s+\|", data)
        if threads_match:
            facts["cpu"]["threads"] = threads_match.group(1).strip()

        # Parse CPU usage
        cpu_usage = []
        cpu_usage_matches = re.findall(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|", data)
        for cpu_id, usage in cpu_usage_matches:
            if int(cpu_id) < 16:  # Only process CPU cores, not other numeric tables
                cpu_usage.append({"id": cpu_id, "usage": int(usage)})
        facts["cpu"]["usage"] = cpu_usage

        # Parse CPU load averages
        load_1min = re.search(r"Last 1 minute CPU load average: (\d+)", data)
        load_5min = re.search(r"Last 5 minute CPU load average: (\d+)", data)
        if load_1min and load_5min:
            facts["cpu"]["load_average"] = {
                "1min": int(load_1min.group(1)),
                "5min": int(load_5min.group(1)),
            }

        return facts

    def parse_memory_info(self, data):
        facts = {"memory": {}}

        # Parse memory usage table
        memory_match = re.search(
            r"\|\s*Physical\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
            data,
        )
        if memory_match:
            facts["memory"].update(
                {
                    "total": memory_match.group(1).strip(),
                    "used": memory_match.group(2).strip(),
                    "free": memory_match.group(3).strip(),
                    "shared": memory_match.group(4).strip(),
                    "buffers": memory_match.group(5).strip(),
                    "cached": memory_match.group(6).strip(),
                }
            )

        # Parse memory channel status
        channel_matches = re.findall(r"Memory channel (\d+) failure prediction test: (\w+)", data)
        facts["memory"]["channels"] = [
            {"id": ch_id, "status": status} for ch_id, status in channel_matches
        ]

        return facts

    def parse_disk_info(self, data):
        facts = {"disk": {}}

        # Find disk information section - be more flexible with whitespace and section endings
        disk_info_match = re.search(
            r"Disk Information:\s*(.*?)(?=\nDisk Usage:|\nBIOS Version:|\n\w+.*?:|\Z)",
            data,
            re.DOTALL,
        )
        if disk_info_match:
            disk_info_section = disk_info_match.group(1)
            disk_info = {}

            # Parse disk info table - look for pipe-separated values
            info_lines = disk_info_section.split("\n")
            for line in info_lines:
                if "|" in line and not line.strip().startswith("|---") and "Item" not in line:
                    # Split the line into columns and strip whitespace
                    columns = [col.strip() for col in line.split("|")]
                    # Remove empty first/last columns that come from splitting
                    columns = [col for col in columns if col]
                    if len(columns) >= 2:
                        key = columns[0].strip()
                        value = columns[1].strip()
                        if key and value and not key.startswith("-"):
                            disk_info[key.lower().replace(" ", "_")] = value

            if disk_info:  # Only add if we found some data
                facts["disk"]["info"] = disk_info

        # Find disk usage section - be more flexible with section boundaries
        disk_usage_match = re.search(
            r"Disk Usage:\s*(.*?)(?=\nBIOS Version:|\nPCIe Packet Processor Version:|\n\w+.*?:|\Z)",
            data,
            re.DOTALL,
        )
        if disk_usage_match:
            disk_usage_section = disk_usage_match.group(1)
            usage_list = []

            # Parse disk usage table - look for lines with filesystem data
            usage_lines = disk_usage_section.split("\n")
            for line in usage_lines:
                if (
                    "|" in line
                    and not line.strip().startswith("|---")
                    and "File System" not in line
                    and line.strip().startswith("|")
                ):  # Ensure it's a table row

                    # Split the line into columns and strip whitespace
                    columns = [col.strip() for col in line.split("|")]
                    # Remove empty first/last columns that come from splitting
                    columns = [col for col in columns if col]

                    if len(columns) >= 6:
                        filesystem = columns[0].strip()
                        # Only process lines that look like filesystem entries
                        if (
                            filesystem
                            and not filesystem.startswith("-")
                            and filesystem != "File System"
                            and ("/" in filesystem or filesystem.startswith("efivarfs"))
                        ):
                            usage_list.append(
                                {
                                    "filesystem": filesystem,
                                    "size": columns[1].strip(),
                                    "used": columns[2].strip(),
                                    "avail": columns[3].strip(),
                                    "use_percent": columns[4].strip(),
                                    "mounted_on": columns[5].strip(),
                                }
                            )

            if usage_list:  # Only add if we found some data
                facts["disk"]["usage"] = usage_list

        return facts

    def parse_firmware_info(self, data):
        facts = {"firmware": {}}

        # Parse BIOS version
        bios_match = re.search(r"BIOS Version:\s+(.+?)(?=\s+BIOS Mode:)", data, re.DOTALL)
        if bios_match:
            facts["firmware"]["bios_version"] = bios_match.group(1).strip()

        # Parse PCIe Packet Processor versions
        pcie_versions = []
        pcie_matches = re.findall(r"\|\s*(\w+\-\d+)\s*\|\s*(\w+)\s*\|\s*(\d+\.\d+)\s*\|", data)
        for module, hw_rev, version in pcie_matches:
            if module.startswith("BCM"):  # Only process BCM entries
                pcie_versions.append({"module": module, "hw_revision": hw_rev, "version": version})
        facts["firmware"]["pcie_processors"] = pcie_versions

        # Parse CPLD versions
        cpld_versions = []
        cpld_matches = re.findall(r"\|\s*(CPU CPLD|MB CPLD\d+)\s*\|\s*(v[\d\.]+)\s*\|", data)
        for module, version in cpld_matches:
            cpld_versions.append({"module": module, "version": version})
        facts["firmware"]["cpld"] = cpld_versions

        return facts

    def parse_psu_info(self, data):
        facts = {"power_supply": {}}

        # Parse PSU redundancy mode
        redundancy_match = re.search(r"Redundancy mode: (.+)", data)
        if redundancy_match:
            facts["power_supply"]["redundancy_mode"] = redundancy_match.group(1).strip()

        # Parse PSU table
        psu_info = []
        psu_matches = re.findall(
            r"\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*([^|]+)\|\s*([^|]*)\|",
            data,
        )
        for psu_id, present, status, serial, revision, psu_type, uptime in psu_matches:
            if present == "YES":  # Only process PSU entries
                psu_info.append(
                    {
                        "id": psu_id,
                        "status": status,
                        "serial": serial.strip(),
                        "revision": revision.strip(),
                        "type": psu_type.strip(),
                        "uptime": uptime.strip(),
                    }
                )
        facts["power_supply"]["units"] = psu_info

        return facts

    def parse_temperature_info(self, data):
        facts = {"temperature": {}}

        # Parse temperature alarm status
        temp_alarm_match = re.search(r"Temperature alarm raised: (\w+)", data)
        if temp_alarm_match:
            facts["temperature"]["alarm_raised"] = temp_alarm_match.group(1).strip() == "True"

        # Parse temperature sensors table
        sensors = []
        sensor_matches = re.findall(
            r"\|\s*(\S[^|]+?)\s*\|\s*(\d+\.?\d*)\s*\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\|",
            data,
        )
        for name, temp, status, high_warn, high_crit, threshold in sensor_matches:
            if name.strip() and not name.startswith("Fan"):  # Only process temperature entries
                sensors.append(
                    {
                        "name": name.strip(),
                        "temperature": float(temp),
                        "status": status.strip(),
                        "high_warning": int(high_warn),
                        "high_critical": int(high_crit),
                        "threshold": threshold.strip(),
                    }
                )
        facts["temperature"]["sensors"] = sensors

        return facts

    def parse_fan_info(self, data):
        facts = {"fans": {}}

        # Parse fan redundancy mode
        redundancy_match = re.search(r"Fans:\s*Redundancy mode: (.+)", data)
        if redundancy_match:
            facts["fans"]["redundancy_mode"] = redundancy_match.group(1).strip()

        # Parse fans table
        fans = []
        fan_matches = re.findall(
            r"\|\s*([^|]+?)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]*)\|",
            data,
        )
        for fan_id, present, status, serial, speed, max_rpm, rpm_percent, uptime in fan_matches:
            if "FAN" in fan_id:  # Only process fan entries
                fans.append(
                    {
                        "id": fan_id.strip(),
                        "present": present == "YES",
                        "status": status.strip(),
                        "serial": serial.strip(),
                        "speed_rpm": int(speed),
                        "max_rpm": int(max_rpm),
                        "rpm_percent": int(rpm_percent),
                        "uptime": uptime.strip(),
                    }
                )
        facts["fans"]["units"] = fans

        return facts


class Config(FactsBase):
    COMMANDS = ["show config | no-more"]

    def populate(self):
        super(Config, self).populate()
        data = self.responses[0]
        self.facts["config"] = data


class Interfaces(FactsBase):
    INTERFACE_MAP = {
        "admin": "admin_state",
        "operational": "operstatus",
        "mtu": "mtu",
        "bundle_id": "bundle_id",
        "vlan": "vlan",
        "network_service": "network_service",
    }

    COMMANDS = [
        "show interfaces | no-more",
        "show lldp neighbors | no-more",
    ]

    def populate(self):
        super(Interfaces, self).populate()

        self.facts["all_ipv4_addresses"] = list()
        self.facts["all_ipv6_addresses"] = list()
        self.facts["neighbors"] = {}

        data = self.responses[0]
        if data:
            self.facts["interfaces"] = self.parse_interfaces(data)

        # Parse LLDP neighbors if available
        if len(self.responses) > 1:
            lldp_data = self.responses[1]
            if lldp_data:
                self.facts["neighbors"] = self.parse_neighbors(lldp_data)

    def parse_interfaces(self, data):
        facts = {}

        # Skip the legend and header lines
        interface_lines = data.split("\n")
        table_start = False

        for line in interface_lines:
            if "|" not in line:
                continue
            if "Interface" in line and "Admin" in line:
                table_start = True
                continue
            if not table_start:
                continue
            if "+--" in line:
                continue

            # Split the line into columns and strip whitespace
            columns = [col.strip() for col in line.split("|")[1:-1]]
            if len(columns) < 8:
                continue

            interface_name = columns[0].strip()
            if not interface_name:
                continue

            interface = {
                "admin_state": columns[1],
                "operstatus": columns[2],
                "mtu": int(columns[6]) if columns[6].isdigit() else 0,
                "network_service": columns[7],
                "bundle_id": columns[8] if columns[8] else None,
                "vlan": columns[5] if columns[5] else None,
            }

            # Handle IPv4 address
            ipv4_addr = columns[3].strip()
            if ipv4_addr:
                addr, masklen = ipv4_addr.split("/")
                interface["ipv4"] = {"address": addr, "masklen": int(masklen)}
                self.add_ip_address(addr, "ipv4")

            # Handle IPv6 address
            ipv6_addr = columns[4].strip()
            if ipv6_addr:
                addr, masklen = ipv6_addr.split("/")
                interface["ipv6"] = {"address": addr, "masklen": int(masklen)}
                self.add_ip_address(addr, "ipv6")

            facts[interface_name] = interface

        return facts

    def parse_neighbors(self, data):
        facts = {}

        # Skip header lines
        neighbor_lines = data.split("\n")
        table_start = False

        for line in neighbor_lines:
            if "|" not in line:
                continue
            if "Interface" in line and "Neighbor System Name" in line:
                table_start = True
                continue
            if not table_start:
                continue
            if "+--" in line:
                continue

            # Split the line into columns and strip whitespace
            columns = [col.strip() for col in line.split("|")[1:-1]]
            if len(columns) < 4:
                continue

            local_interface = columns[0].strip()
            if not local_interface:
                continue

            if local_interface not in facts:
                facts[local_interface] = []

            # Handle empty TTL values
            ttl_value = columns[3].strip()
            ttl = int(ttl_value) if ttl_value else None

            neighbor = {"host": columns[1], "port": columns[2], "ttl": ttl}
            facts[local_interface].append(neighbor)

        return facts

    def add_ip_address(self, address, family):
        """Add an IP address to the global address list."""
        if family == "ipv4":
            self.facts["all_ipv4_addresses"].append(address)
        else:
            self.facts["all_ipv6_addresses"].append(address)
