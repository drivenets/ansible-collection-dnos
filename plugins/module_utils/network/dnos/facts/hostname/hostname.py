# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.argspec.hostname.hostname import (
    HostnameArgs,
)


"""
The dnos hostname fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""


class HostnameFacts(object):
    """The dnos hostname facts class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = HostnameArgs.argument_spec
        self.facts = {}

    def get_config(self, connection):
        return connection.get("show system | no-more")

    def populate(self):
        """Populate the facts for Hostname network resource
        This method is called by the facts gathering system
        """
        import re

        # Import get_connection function
        from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import (
            get_connection,
        )

        # Get connection from module
        connection = get_connection(self._module)

        # Get system data
        data = self.get_config(connection)

        # Parse hostname from system data using same logic as base.py
        system_name_match = re.search(r"System Name: (.+?),\s*System-Id: (.+)", data)
        if system_name_match:
            hostname = system_name_match.group(1).strip()
            hostname_data = {"hostname": hostname}
        else:
            hostname_data = {}

        # Store facts in the expected format
        self.facts["hostname"] = hostname_data

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Hostname network resource
        :param connection: the connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        import re

        facts = {}
        if not data:
            data = self.get_config(connection)

        # Parse hostname from system data using same logic as base.py
        system_name_match = re.search(r"System Name: (.+?),\s*System-Id: (.+)", data)
        if system_name_match:
            hostname = system_name_match.group(1).strip()
            obj = {"hostname": hostname}
        else:
            obj = {}

        facts.update({"hostname": obj})
        facts.update({"ansible_network_resources": obj})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
