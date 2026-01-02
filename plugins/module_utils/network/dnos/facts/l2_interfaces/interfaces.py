# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
Interfaces facts gathering for DNOS.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.argspec.interfaces.interfaces import (
    InterfacesArgs,
)


class L2InterfacesFacts(object):
    """The dnos interfaces facts class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec
        self.facts = {}

    def get_config(self, connection):
        return connection.get("show interfaces |incl (L2)| no-more")

    def populate(self):
        """Populate the facts for Interfaces network resource
        This method is called by the facts gathering system
        """
        # Import get_connection function
        from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import (
            get_connection,
        )

        # Get connection from module
        connection = get_connection(self._module)

        # Get interfaces data
        data = self.get_config(connection)

        # Parse interfaces from data using same logic as base.py
        interfaces_data = self.parse_interfaces(data)

        # Store facts in the expected format
        self.facts["interfaces"] = interfaces_data

    def parse_interfaces(self, data):
        """Parse interfaces data using same logic as base.py"""
        facts = {}

        # Skip the legend and header lines
        interface_lines = data.split("\n")
        for line in interface_lines:
            if "|" not in line:
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

            # Handle IPv6 address
            ipv6_addr = columns[4].strip()
            if ipv6_addr:
                addr, masklen = ipv6_addr.split("/")
                interface["ipv6"] = {"address": addr, "masklen": int(masklen)}

            facts[interface_name] = interface

        return facts

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Interfaces network resource
        :param connection: the connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        if not data:
            data = self.get_config(connection)

        # Parse interfaces from data
        interfaces_data = self.parse_interfaces(data)

        facts.update({"interfaces": interfaces_data})
        facts.update({"ansible_network_resources": {"l2_interfaces": interfaces_data}})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
