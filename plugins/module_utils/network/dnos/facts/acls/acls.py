# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
ACLs facts gathering for DNOS.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.argspec.acls.acls import (
    AclsArgs,
)


class AclsFacts(object):
    """The dnos acls facts class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = AclsArgs.argument_spec
        self.facts = {}

    def get_config(self, connection):
        return connection.get("show access-lists | no-more")

    def populate(self):
        """Populate the facts for ACLs network resource
        This method is called by the facts gathering system
        """
        # Import get_connection function
        from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import (
            get_connection,
        )

        # Get connection from module
        connection = get_connection(self._module)

        # Get acls data
        data = self.get_config(connection)

        # Parse acls from data
        acls_data = self.parse_acls(data)

        # Store facts in the expected format
        self.facts["acls"] = acls_data

    def parse_acls(self, data):
        """Parse ACLs data from show access-lists output"""
        facts = []

        if not data:
            return facts

        lines = data.split("\n")
        current_afi = None
        current_acl_name = None
        current_acl = None
        afi_dict = {}  # Track ACLs by AFI

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Detect AFI section headers
            if line.startswith("Access Lists - Ipv4"):
                current_afi = "ipv4"
                i += 1
                continue
            elif line.startswith("Access Lists - Ipv6"):
                current_afi = "ipv6"
                i += 1
                continue
            elif line.startswith("Access Lists - Ethernet"):
                current_afi = "ethernet"
                i += 1
                continue

            # Skip empty lines and separator lines
            if not line or line.startswith("|---") or line.startswith("+---"):
                i += 1
                continue

            # Skip header lines
            if "| Access-list name" in line:
                i += 1
                continue

            # Process ACL entry lines
            if "|" in line and current_afi:
                columns = [col.strip() for col in line.split("|")[1:-1]]

                if current_afi in ["ipv4", "ipv6"]:
                    if len(columns) < 17:
                        i += 1
                        continue

                    acl_name = columns[0] if columns[0] else current_acl_name
                    index = columns[1]

                    # New ACL if name is present
                    if acl_name:
                        current_acl_name = acl_name
                        if current_afi not in afi_dict:
                            afi_dict[current_afi] = {}
                        if acl_name not in afi_dict[current_afi]:
                            afi_dict[current_afi][acl_name] = {"name": acl_name, "aces": []}
                        current_acl = afi_dict[current_afi][acl_name]

                    if current_acl and index:
                        ace = {
                            "sequence": index,
                            "grant": columns[2],
                        }

                        # Add optional fields if present
                        if columns[3]:  # nexthop1
                            ace["nexthop1"] = columns[3]
                        if columns[4]:  # next_table
                            ace["next_table"] = columns[4]
                        if columns[5]:  # vrf
                            ace["vrf"] = columns[5]
                        if columns[6]:  # protocol
                            ace["protocol"] = columns[6]

                        # Source (Src Ports = column 7, Src IP = column 8)
                        if columns[7] or columns[8]:
                            ace["source"] = {}

                            # Source IP (column 8)
                            if columns[8] and columns[8] != "any":
                                if "/" in columns[8]:
                                    ace["source"]["address"] = columns[8]
                                else:
                                    ace["source"]["host"] = columns[8]
                            elif columns[8] == "any":
                                ace["source"]["any"] = True

                            # Source ports (column 7)
                            if columns[7] and columns[7] != "any":
                                ace["source"]["port_protocol"] = columns[7]

                        # Destination (Dest Ports = column 9, Dest IP = column 10)
                        if columns[9] or columns[10]:
                            ace["destination"] = {}

                            # Destination IP (column 10)
                            if columns[10] and columns[10] != "any":
                                if "/" in columns[10]:
                                    ace["destination"]["address"] = columns[10]
                                else:
                                    ace["destination"]["host"] = columns[10]
                            elif columns[10] == "any":
                                ace["destination"]["any"] = True

                            # Destination ports (column 9)
                            if columns[9] and columns[9] != "any":
                                ace["destination"]["port_protocol"] = columns[9]

                        # Additional fields
                        if columns[11]:  # dscp
                            ace["dscp"] = columns[11]
                        if columns[12]:  # packet_length
                            ace["packet_length"] = columns[12]
                        if columns[13]:  # qos_tcm
                            ace["qos_tcm"] = columns[13]
                        if columns[14]:  # description
                            ace["description"] = columns[14]
                        if columns[15]:  # log
                            ace["log"] = True
                        if columns[16]:  # cir_mbps
                            ace["cir_mbps"] = columns[16]
                        if len(columns) > 17 and columns[17]:  # cbs_kbytes
                            ace["cbs_kbytes"] = columns[17]

                        current_acl["aces"].append(ace)

                elif current_afi == "ethernet":
                    if len(columns) < 9:
                        i += 1
                        continue

                    acl_name = columns[0] if columns[0] else current_acl_name
                    index = columns[1]

                    # New ACL if name is present
                    if acl_name:
                        current_acl_name = acl_name
                        if current_afi not in afi_dict:
                            afi_dict[current_afi] = {}
                        if acl_name not in afi_dict[current_afi]:
                            afi_dict[current_afi][acl_name] = {"name": acl_name, "aces": []}
                        current_acl = afi_dict[current_afi][acl_name]

                    if current_acl and index:
                        ace = {
                            "sequence": index,
                            "grant": columns[2],
                        }

                        # Ethernet-specific fields
                        if columns[3]:  # src_mac
                            ace["src_mac"] = columns[3]
                        if columns[4]:  # dest_mac
                            ace["dest_mac"] = columns[4]
                        if columns[5]:  # ether_type
                            ace["ether_type"] = columns[5]
                        if columns[6]:  # packet_type
                            ace["packet_type"] = columns[6]
                        if columns[7]:  # inner_vlan
                            ace["inner_vlan"] = columns[7]
                        if columns[8]:  # outer_vlan
                            ace["outer_vlan"] = columns[8]
                        if len(columns) > 9 and columns[9]:  # description
                            ace["description"] = columns[9]

                        current_acl["aces"].append(ace)

            i += 1

        # Convert to list format
        for afi, acls in afi_dict.items():
            facts.append({"afi": afi, "acls": list(acls.values())})

        return facts

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for ACLs network resource
        :param connection: the connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        if not data:
            data = self.get_config(connection)

        # Parse acls from data
        acls_data = self.parse_acls(data)

        facts.update({"acls": acls_data})
        facts.update({"ansible_network_resources": {"acls": acls_data}})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
