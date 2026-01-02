# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dnos_netconf config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import xml.etree.ElementTree as ET

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.facts import Facts

# Import NETCONF utilities
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.netconf_utils import (
    DNOSNetconfUtils,
    check_netconf_support,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.rm_templates.netconf import (
    NetconfTemplate,
)


class Netconf(ResourceModule):
    """
    The dnos_netconf config class with NETCONF support
    """

    def __init__(self, module):
        super(Netconf, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="netconf",
            tmplt=NetconfTemplate(),
        )
        self.parsers = [
            "enabled",
            "port",
            "vrf",
            "vrf_admin_state",
            "session_timeout",
            "max_sessions",
            "class_of_service",
            "authentication",
            "encryption",
            "call_home",
            "idle_timeout",
            "hello_timeout",
            "capabilities",
            "source_interface",
        ]
        # Initialize NETCONF utilities
        self.netconf_utils = None
        self.use_netconf = False
        # NETCONF capability check moved to execute_module for better mock support

    def _check_netconf_capability(self):
        """Check if NETCONF is supported and preferred"""
        try:
            # Check if device supports NETCONF
            netconf_supported = check_netconf_support(self._module)
            self._module.log(f"NETCONF support check result: {netconf_supported}")
            if netconf_supported:
                self.netconf_utils = DNOSNetconfUtils(self._module)
                # Check if system YANG model is supported
                yang_supported = self.netconf_utils.supports_yang_model("system")
                self._module.log(f"System YANG model support: {yang_supported}")
                if yang_supported:
                    self.use_netconf = True
                    self._module.log("Using NETCONF for NETCONF configuration")
                else:
                    self.use_netconf = False
                    self._module.log("System YANG model not supported, falling back to CLI")
            else:
                self.use_netconf = False
                self._module.log("NETCONF not supported, using CLI")
        except Exception as e:
            self._module.log(f"NETCONF check failed: {str(e)}, using CLI")
            self.use_netconf = False
        self._module.log(f"Final use_netconf decision: {self.use_netconf}")

    def execute_module(self):
        """Execute the module
        :rtype: A dictionary
        :returns: The result from module execution
        """
        # Re-check NETCONF capability at execution time for proper mock support
        self._check_netconf_capability()
        if self.state not in ["parsed", "gathered"]:
            if self.use_netconf and self.state != "rendered":
                return self.run_netconf_commands()
            else:
                # For CLI operations, use base ResourceModule logic
                self.generate_commands()
                self.run_commands()
        elif self.state == "gathered":
            # For gathered state, use facts gathering
            return self.gather_facts()
        elif self.state == "parsed":
            # For parsed state, parse running config
            return self.parse_running_config()
        return self.result

    def gather_facts(self):
        """Gather NETCONF facts"""
        result = {"changed": False}
        # Use ResourceModule's populate_facts for gathering
        result["gathered"] = self.have
        return result

    def parse_running_config(self):
        """Parse running configuration for parsed state"""
        result = {"changed": False}
        # Get running config from module params
        running_config = self._module.params.get("running_config", "")
        if running_config:
            # Parse the configuration using template
            from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.rm_templates.netconf import (
                NetconfTemplate,
            )

            netconf_parser = NetconfTemplate(lines=running_config.splitlines(), module=self._module)
            parsed_config = netconf_parser.parse()
            if parsed_config:
                # Handle different return formats from the parser
                if isinstance(parsed_config, dict) and "config" in parsed_config:
                    result["parsed"] = parsed_config["config"]
                elif isinstance(parsed_config, dict):
                    result["parsed"] = parsed_config
                else:
                    result["parsed"] = {}
            else:
                result["parsed"] = {}
        else:
            result["parsed"] = {}
        return result

    def run_netconf_commands(self):
        """Execute NETCONF operations for NETCONF configuration"""
        result = {"changed": False}
        # Get existing NETCONF configuration using ResourceModule's have
        have = self.have
        want = self._module.params.get("config", {})
        # Store before state
        result["before"] = have
        if self.state == "deleted":
            # Delete NETCONF configuration
            if have:
                netconf_delete = self._get_delete_config(have, want)
                if netconf_delete:
                    try:
                        netconf_config_xml = self._build_netconf_xml(
                            netconf_delete, operation="delete"
                        )
                        self.netconf_utils.netconf.edit_config(
                            config=netconf_config_xml, target="candidate"
                        )
                        self.netconf_utils.netconf.commit()
                        result["changed"] = True
                        result["commands"] = ["NETCONF: delete netconf config"]
                    except Exception as e:
                        self._module.fail_json(msg=f"NETCONF delete operation failed: {str(e)}")
        elif self.state in ["merged", "replaced", "overridden"]:
            # Merge or replace NETCONF configuration
            if want:
                try:
                    if self.state == "replaced":
                        netconf_config = self._get_replaced_config(want, have)
                    else:
                        netconf_config = self._get_merged_config(want, have)
                    if netconf_config:
                        netconf_config_xml = self._build_netconf_xml(netconf_config)
                        self.netconf_utils.netconf.edit_config(
                            config=netconf_config_xml, target="candidate"
                        )
                        self.netconf_utils.netconf.commit()
                        result["changed"] = True
                        result["commands"] = ["NETCONF: configure netconf"]
                        # Get after state
                        after_facts = self._facts_module.get_facts(resource_facts_type=["netconf"])
                        result["after"] = (
                            after_facts.get("ansible_facts", {})
                            .get("ansible_network_resources", {})
                            .get("netconf", {})
                        )
                except Exception as e:
                    # Fallback to CLI on NETCONF failure
                    self._module.log(f"NETCONF operation failed: {str(e)}, falling back to CLI")
                    self.use_netconf = False
                    self.generate_commands()
                    self.run_commands()
                    return self.result
        return result

    def _convert_to_netconf_format(self, config):
        """Convert configuration to NETCONF format"""
        if not config:
            return {}
        netconf_config = {
            "drivenets-top": {
                "@xmlns": "http://drivenets.com/ns/yang/dn-top",
                "system": {"@xmlns": "http://drivenets.com/ns/yang/dn-system"},
            }
        }
        # Build NETCONF configuration
        system_config = netconf_config["drivenets-top"]["system"]
        if any(
            k in config
            for k in [
                "enabled",
                "port",
                "vrf",
                "session_timeout",
                "max_sessions",
                "class_of_service",
            ]
        ):
            system_config["netconf"] = {}
            netconf_config_dict = system_config["netconf"]
            # Basic NETCONF configuration
            if "enabled" in config:
                netconf_config_dict["admin-state"] = "enabled" if config["enabled"] else "disabled"
            if "port" in config:
                netconf_config_dict["port"] = config["port"]
            if "vrf" in config:
                netconf_config_dict["vrf"] = {
                    "vrf-name": config["vrf"],
                    "admin-state": "enabled",  # Default for VRF
                }
            if "session_timeout" in config:
                netconf_config_dict["session-timeout"] = config["session_timeout"]
            if "max_sessions" in config:
                netconf_config_dict["max-sessions"] = config["max_sessions"]
            if "class_of_service" in config:
                netconf_config_dict["class-of-service"] = config["class_of_service"]
        return netconf_config

    def _convert_from_netconf_format(self, netconf_data):
        """Convert NETCONF response to module format"""
        config = {}
        try:
            system_data = netconf_data.get("drivenets-top", {}).get("system", {})
            netconf_data = system_data.get("netconf", {})
            if netconf_data:
                # Parse basic configuration
                if "admin-state" in netconf_data:
                    config["enabled"] = netconf_data["admin-state"] == "enabled"
                if "port" in netconf_data:
                    config["port"] = int(netconf_data["port"])
                if "vrf" in netconf_data:
                    vrf_config = netconf_data["vrf"]
                    if isinstance(vrf_config, dict) and "vrf-name" in vrf_config:
                        config["vrf"] = vrf_config["vrf-name"]
                    elif isinstance(vrf_config, str):
                        config["vrf"] = vrf_config
                if "session-timeout" in netconf_data:
                    config["session_timeout"] = int(netconf_data["session-timeout"])
                if "max-sessions" in netconf_data:
                    config["max_sessions"] = int(netconf_data["max-sessions"])
                if "class-of-service" in netconf_data:
                    config["class_of_service"] = int(netconf_data["class-of-service"])
        except Exception as e:
            self._module.log(f"Error converting NETCONF data: {str(e)}")
        return config

    def _parse_netconf_config(self, config_lines):
        """Parse NETCONF configuration from CLI output"""
        config = {}
        for line in config_lines:
            line = line.strip()
            if "admin-state enabled" in line:
                config["enabled"] = True
            elif "admin-state disabled" in line:
                config["enabled"] = False
            elif line.startswith("port "):
                config["port"] = int(line.split("port ")[1])
            elif line.startswith("vrf "):
                config["vrf"] = line.split("vrf ")[1]
            elif line.startswith("session-timeout "):
                config["session_timeout"] = int(line.split("session-timeout ")[1])
            elif line.startswith("max-sessions "):
                config["max_sessions"] = int(line.split("max-sessions ")[1])
            elif line.startswith("class-of-service "):
                config["class_of_service"] = int(line.split("class-of-service ")[1])
        return config

    def _parse_netconf_config_legacy(self, config_data):
        """Legacy parser for old format compatibility"""
        return self._parse_netconf_config(
            config_data.splitlines() if isinstance(config_data, str) else config_data
        )

    def _get_merged_config(self, want, have):
        """Get merged configuration for NETCONF"""
        # Start with have configuration
        merged = have.copy() if have else {}
        # Merge want into have
        for key, value in want.items():
            if value is not None:
                merged[key] = value
        return merged

    def _get_replaced_config(self, want, have):
        """Get replaced configuration for NETCONF"""
        # For replaced, use want configuration as-is
        return want

    def _get_delete_config(self, have, want):
        """Get delete configuration for NETCONF"""
        # For delete, return empty configuration
        return {}

    def _build_netconf_xml(self, config, operation="merge"):
        """Build NETCONF XML from configuration dictionary"""
        try:
            netconf_config = self._convert_to_netconf_format(config)
            # Convert dict to XML
            root = ET.Element("config")
            root.set("xmlns:xc", "urn:ietf:params:xml:ns:netconf:base:1.0")

            def dict_to_xml(parent, data):
                for key, value in data.items():
                    if key.startswith("@"):
                        # Handle XML attributes
                        attr_name = key[1:]  # Remove @ prefix
                        parent.set(attr_name, str(value))
                    elif isinstance(value, dict):
                        elem = ET.SubElement(parent, key)
                        if operation == "delete":
                            elem.set("xc:operation", "delete")
                        dict_to_xml(elem, value)
                    elif isinstance(value, list):
                        for item in value:
                            elem = ET.SubElement(parent, key)
                            if isinstance(item, dict):
                                dict_to_xml(elem, item)
                            else:
                                elem.text = str(item)
                    else:
                        elem = ET.SubElement(parent, key)
                        elem.text = str(value)

            dict_to_xml(root, netconf_config)
            return ET.tostring(root, encoding="unicode")
        except Exception as e:
            self._module.fail_json(msg=f"Failed to build NETCONF XML: {str(e)}")

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        wantd = self.want
        haved = self.have
        # For different states, determine what needs to be configured
        if self.state == "deleted":
            # For delete, generate delete commands based on existing config
            if haved:  # Only delete if there's something to delete
                self.commands = self._generate_config_commands({}, haved)
            else:
                self.commands = []
        elif self.state == "merged":
            # For merged, configure want if different from have
            self._module.log(f"DEBUG: merged - checking diff between want={wantd} and have={haved}")
            # Simple diff: if want has values not in have, or different values, generate commands
            needs_config = False
            for key, value in wantd.items():
                if key not in haved or haved[key] != value:
                    needs_config = True
                    break
            if needs_config and wantd:  # Only generate commands if there are differences
                self.commands = self._generate_config_commands(wantd, haved)
            else:
                self.commands = []
        elif self.state == "replaced":
            # For replaced, configure everything in want
            if wantd:
                self.commands = self._generate_config_commands(wantd, haved)
            else:
                self.commands = []
        elif self.state == "rendered":
            # For rendered, generate commands for want regardless of have
            if wantd:
                self.commands = self._generate_config_commands(wantd, {})
            else:
                self.commands = []
        else:
            self.commands = []
        self._module.log(f"DEBUG: generated commands: {self.commands}")

    def _generate_config_commands(self, want, have):
        """Generate the actual CLI commands"""
        commands = []
        # Check if we're deleting everything
        if not want:
            # Delete all NETCONF configuration
            commands.append("system")
            commands.append("no netconf")
            return commands
        # Enter NETCONF configuration context
        commands.append("system")
        commands.append("netconf")
        # Port configuration
        if "port" in want:
            commands.append(f"port {want['port']}")
        # VRF configuration
        if "vrf" in want:
            commands.append(f"vrf {want['vrf']}")
            # Enable admin-state within VRF context for enabled NETCONF
            if want.get("enabled", True):
                commands.append("admin-state enabled")
            commands.append("exit")  # Exit VRF context
        # Session timeout
        if "session_timeout" in want:
            commands.append(f"session-timeout {want['session_timeout']}")
        # Max sessions
        if "max_sessions" in want:
            commands.append(f"max-sessions {want['max_sessions']}")
        # Class of service
        if "class_of_service" in want:
            commands.append(f"class-of-service {want['class_of_service']}")
        return commands
