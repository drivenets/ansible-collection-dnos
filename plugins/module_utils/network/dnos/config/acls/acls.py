# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dnos_acls config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import xml.etree.ElementTree as ET

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.facts import Facts


# Import NETCONF utilities - conditional import to handle missing dependencies
try:
    from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.netconf_utils import (
        DNOSNetconfUtils,
        check_netconf_support,
    )

    HAS_NETCONF_UTILS = True
except ImportError:
    HAS_NETCONF_UTILS = False


class Acls(ResourceModule):
    """
    The dnos_acls config class with NETCONF support
    """

    def __init__(self, module):
        super(Acls, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="acls",
            tmplt=None,
        )
        self.parsers = []
        # Initialize NETCONF utilities
        self.netconf_utils = None
        self.use_netconf = False
        self._check_netconf_capability()

    def _check_netconf_capability(self):
        """Check if NETCONF is supported and preferred"""
        if not HAS_NETCONF_UTILS:
            self._module.log("NETCONF utilities not available, using CLI")
            self.use_netconf = False
            return
        try:
            # Check if device supports NETCONF
            if check_netconf_support(self._module):
                self.netconf_utils = DNOSNetconfUtils(self._module)
                # Check if ACL YANG model is supported
                if self.netconf_utils.supports_yang_model("acl"):
                    self.use_netconf = True
                    self._module.log("Using NETCONF for ACL configuration")
                else:
                    self._module.log("ACL YANG model not supported, falling back to CLI")
            else:
                self._module.log("NETCONF not supported, using CLI")
        except Exception as e:
            self._module.log(f"NETCONF check failed: {str(e)}, using CLI")
            self.use_netconf = False

    def execute_module(self):
        """Execute the module
        Returns:
            dict: The result from module execution
        """
        if self.state not in ["parsed", "gathered", "rendered"]:
            if self.use_netconf and HAS_NETCONF_UTILS:
                try:
                    return self.run_netconf_commands()
                except Exception as e:
                    self._module.log(f"NETCONF execution failed: {str(e)}, falling back to CLI")
                    self.use_netconf = False
            # Use CLI commands
            self.generate_commands()
            self.run_commands()
        return self.result

    def run_netconf_commands(self):
        """Execute NETCONF operations for ACL configuration"""
        result = {"changed": False}
        # Get existing ACL configuration
        existing_facts = self.facts_module.get_facts(self._module, ["acls"])
        have = (
            existing_facts.get("ansible_facts", {})
            .get("ansible_network_resources", {})
            .get("acls", [])
        )
        want = self._module.params.get("config", [])
        # Store before state
        result["before"] = have
        # Convert to NETCONF format
        if self.state == "deleted":
            netconf_config = self._get_delete_config(have, want)
        elif self.state == "merged":
            netconf_config = self._get_merged_config(have, want)
        elif self.state == "replaced":
            netconf_config = self._get_replaced_config(have, want)
        elif self.state == "overridden":
            netconf_config = self._get_overridden_config(have, want)
        else:
            return result
        if not netconf_config:
            return result
        try:
            # Lock configuration
            self.netconf_utils.lock_config()
            # Apply configuration directly with correct structure
            operation = "replace" if self.state in ["replaced", "overridden"] else "merge"
            # Convert dict to XML element for NETCONF
            root = ET.Element("config")
            self.netconf_utils._dict_to_element(root, netconf_config)
            config_xml = ET.tostring(root, encoding="unicode")
            # Edit configuration
            self.netconf_utils.netconf.edit_config(
                target="candidate", config=config_xml, default_operation=operation
            )
            # Get diff for check mode
            if self._module.check_mode:
                diff = self.netconf_utils.get_config_diff()
                result["diff"] = {"prepared": diff}
                # Discard changes in check mode
                self.netconf_utils.discard_changes()
            else:
                # Commit configuration
                self.netconf_utils.commit_config(
                    comment=f"Ansible ACL configuration - {self.state}"
                )
                result["changed"] = True
            # Get after configuration with correct hierarchy
            filter_xml = """
            <drivenets-top xmlns="http://drivenets.com/ns/yang/dn-top">
                <access-lists xmlns="http://drivenets.com/ns/yang/dn-access-control-list"/>
            </drivenets-top>
            """
            config_xml = self.netconf_utils.netconf.get_config(
                source="running", filter=("subtree", filter_xml)
            )
            after_config = self.netconf_utils._xml_to_dict(config_xml)
            result["after"] = self._convert_from_netconf_format(after_config)
            # Store commands for visibility
            result["commands"] = ["NETCONF: edit-config acl"]
        except Exception as e:
            self._module.fail_json(msg=f"NETCONF operation failed: {str(e)}")
        finally:
            # Always unlock
            self.netconf_utils.unlock_config()
        return result

    def _convert_to_netconf_format(self, config):
        """Convert module parameters to NETCONF/YANG format for ACLs with correct DNOS hierarchy"""
        if not config:
            return {}
        # Build correct DNOS YANG hierarchy for ACLs
        netconf_config = {
            "drivenets-top": {
                "@xmlns": "http://drivenets.com/ns/yang/dn-top",
                "access-lists": {"@xmlns": "http://drivenets.com/ns/yang/dn-access-control-list"},
            }
        }
        # Shortcut reference for cleaner code
        acl_config = netconf_config["drivenets-top"]["access-lists"]
        # Organize by AFI
        for afi_config in config:
            afi = afi_config["afi"]
            if afi == "ipv4":
                if "ipv4" not in acl_config:
                    acl_config["ipv4"] = {"access-list": []}
                for acl in afi_config.get("acls", []):
                    acl_entry = {"name": acl["name"], "config-items": {"name": acl["name"]}}
                    if "aces" in acl:
                        rules = []
                        for ace in acl["aces"]:
                            rule_config = {"rule-id": ace.get("sequence", "10"), "config-items": {}}
                            # Add rule-id to config-items
                            rule_config["config-items"]["rule-id"] = rule_config["rule-id"]
                            # Action (rule-type in YANG)
                            if "action" in ace:
                                rule_config["config-items"]["rule-type"] = f"dn-acl:{ace['action']}"
                            # Description
                            if "description" in ace:
                                rule_config["config-items"]["description"] = ace["description"]
                            # Protocol
                            if "protocols" in ace:
                                rule_config["config-items"]["protocol"] = ace["protocols"]
                            # DNOS-specific fields based on YANG models
                            # Log
                            if "log" in ace:
                                rule_config["config-items"]["log"] = ace["log"]
                            # Rate limit (police)
                            if "rate_limit" in ace:
                                rl = ace["rate_limit"]
                                rule_config["config-items"]["police"] = {
                                    "committed-rate": int(
                                        rl.get("cir", "1000")
                                        .replace("mbps", "")
                                        .replace("kbps", "")
                                    )
                                    * (1000 if "mbps" in rl.get("cir", "") else 1),
                                    "committed-burst-size": int(
                                        rl.get("cbs", "1000")
                                        .replace("kbytes", "")
                                        .replace("bytes", "")
                                    )
                                    * (1000 if "kbytes" in rl.get("cbs", "") else 1),
                                }
                            # QoS
                            if "set_qos" in ace:
                                qos = ace["set_qos"]
                                if qos.get("traffic_class"):
                                    rule_config["config-items"]["set-qos-traffic-class-map"] = qos[
                                        "traffic_class"
                                    ]
                                elif qos.get("default"):
                                    rule_config["config-items"]["set-qos-default"] = True
                            rules.append(rule_config)
                        if rules:
                            acl_entry["rules"] = {"rule": rules}
                    acl_config["ipv4"]["access-list"].append(acl_entry)
            elif afi == "ipv6":
                if "ipv6" not in acl_config:
                    acl_config["ipv6"] = {"access-list": []}
                for acl in afi_config.get("acls", []):
                    acl_entry = {"name": acl["name"], "config-items": {"name": acl["name"]}}
                    if "aces" in acl:
                        rules = []
                        for ace in acl["aces"]:
                            rule_config = {
                                "rule-id": ace.get("sequence", "10"),
                                "config-items": {
                                    "rule-id": ace.get("sequence", "10"),
                                    "rule-type": f"dn-acl:{ace.get('action', 'allow')}",
                                },
                            }
                            # Same DNOS-specific handling as IPv4
                            if "protocols" in ace:
                                rule_config["config-items"]["protocol"] = ace["protocols"]
                            if "log" in ace:
                                rule_config["config-items"]["log"] = ace["log"]
                            rules.append(rule_config)
                        if rules:
                            acl_entry["rules"] = {"rule": rules}
                    acl_config["ipv6"]["access-list"].append(acl_entry)
            elif afi == "ethernet":
                if "eth" not in acl_config:
                    acl_config["eth"] = {"access-list": []}
                for acl in afi_config.get("acls", []):
                    acl_entry = {"name": acl["name"], "config-items": {"name": acl["name"]}}
                    if "aces" in acl:
                        rules = []
                        for ace in acl["aces"]:
                            rule_config = {
                                "rule-id": ace.get("sequence", "10"),
                                "config-items": {
                                    "rule-id": ace.get("sequence", "10"),
                                    "rule-type": f"dn-acl:{ace.get('action', 'allow')}",
                                },
                            }
                            # Ethernet-specific fields
                            if "ethernet" in ace:
                                eth = ace["ethernet"]
                                rule_config["config-items"]["eth-matches"] = {}
                                if eth.get("source_mac"):
                                    rule_config["config-items"]["eth-matches"]["src-mac"] = eth[
                                        "source_mac"
                                    ]
                                if eth.get("destination_mac"):
                                    rule_config["config-items"]["eth-matches"]["dest-mac"] = eth[
                                        "destination_mac"
                                    ]
                                if eth.get("ethertype"):
                                    rule_config["config-items"]["eth-matches"]["ether-type"] = eth[
                                        "ethertype"
                                    ]
                            rules.append(rule_config)
                        if rules:
                            acl_entry["rules"] = {"rule": rules}
                    acl_config["eth"]["access-list"].append(acl_entry)
        return netconf_config

    def _convert_from_netconf_format(self, netconf_config):
        """Convert NETCONF format back to module format from DNOS hierarchy"""
        if not netconf_config:
            return []
        # Navigate through DNOS hierarchy to ACL config
        try:
            if "drivenets-top" in netconf_config:
                acl_config = netconf_config["drivenets-top"].get("access-control-list", {})
            else:
                # Handle case where we get config without top-level wrapper
                acl_config = netconf_config.get("access-control-list", {})
            return self._parse_acl_config(acl_config)
        except Exception:
            # If structure is different, try old format
            return self._parse_acl_config_legacy(netconf_config)

    def _parse_acl_config(self, acl_config):
        """Parse ACL config from DNOS YANG structure"""
        module_config = []
        # Process IPv4 ACLs
        if "ipv4" in acl_config and "acl" in acl_config["ipv4"]:
            ipv4_config = {"afi": "ipv4", "acls": []}
            for acl in acl_config["ipv4"]["acl"]:
                acl_config = {"name": acl["name"]}
                if "aces" in acl and "ace" in acl["aces"]:
                    aces = []
                    for ace in acl["aces"]["ace"]:
                        ace_config = {}
                        # Sequence
                        if "sequence" in ace:
                            ace_config["sequence"] = ace["sequence"]
                        # Action
                        if "action" in ace:
                            ace_config["action"] = ace["action"]
                        # Description
                        if "description" in ace:
                            ace_config["description"] = ace["description"]
                        # protocols
                        if "protocols" in ace:
                            ace_config["protocols"] = ace["protocols"]
                        # Source
                        if "source" in ace:
                            src = ace["source"]
                            ace_config["source"] = {}
                            if src.get("any"):
                                ace_config["source"]["any"] = True
                            elif "host" in src:
                                ace_config["source"]["host"] = src["host"]
                            elif "prefix" in src:
                                ace_config["source"]["prefix"] = src["prefix"]
                            elif "mask" in src:
                                ace_config["source"]["mask"] = src["mask"]
                            # Source port
                            if "port" in src:
                                ace_config["source"]["port"] = src["port"]
                            elif "port-range" in src:
                                ace_config["source"]["port_range"] = [
                                    src["port-range"]["start"],
                                    src["port-range"]["end"],
                                ]
                        # Destination
                        if "destination" in ace:
                            dst = ace["destination"]
                            ace_config["destination"] = {}
                            if dst.get("any"):
                                ace_config["destination"]["any"] = True
                            elif "host" in dst:
                                ace_config["destination"]["host"] = dst["host"]
                            elif "prefix" in dst:
                                ace_config["destination"]["prefix"] = dst["prefix"]
                            elif "mask" in dst:
                                ace_config["destination"]["mask"] = dst["mask"]
                            # Destination port
                            if "port" in dst:
                                ace_config["destination"]["port"] = dst["port"]
                            elif "port-range" in dst:
                                ace_config["destination"]["port_range"] = [
                                    dst["port-range"]["start"],
                                    dst["port-range"]["end"],
                                ]
                        # TCP flags
                        if "tcp-flags" in ace:
                            ace_config["tcp_flags"] = ace["tcp-flags"]
                        # ICMP
                        if "icmp-type" in ace:
                            ace_config["icmp_type"] = ace["icmp-type"]
                        if "icmp-code" in ace:
                            ace_config["icmp_code"] = ace["icmp-code"]
                        # DSCP
                        if "dscp" in ace:
                            ace_config["dscp"] = ace["dscp"]
                        # Fragments
                        if "fragments" in ace:
                            ace_config["fragments"] = ace["fragments"]
                        # Log
                        if "log" in ace:
                            ace_config["log"] = ace["log"]
                        aces.append(ace_config)
                    if aces:
                        acl_config["aces"] = aces
                ipv4_config["acls"].append(acl_config)
            if ipv4_config["acls"]:
                module_config.append(ipv4_config)
        # Process IPv6 ACLs (similar structure)
        if "ipv6" in acl_config and "acl" in acl_config["ipv6"]:
            ipv6_config = {"afi": "ipv6", "acls": []}
            # ... (similar processing as IPv4)
            if ipv6_config["acls"]:
                module_config.append(ipv6_config)
        return module_config

    def _parse_acl_config_legacy(self, netconf_config):
        """Parse ACL config from legacy format (backward compatibility)"""
        # For legacy format, the structure is flat so we can reuse the parser
        return self._parse_acl_config(netconf_config)

    def _get_merged_config(self, have, want):
        """Get merged configuration for NETCONF"""
        have_netconf = self._convert_to_netconf_format(have)
        want_netconf = self._convert_to_netconf_format(want)
        # Deep merge want into have
        merged = have_netconf.copy()
        for afi in ["ipv4", "ipv6"]:
            if afi in want_netconf:
                if afi not in merged:
                    merged[afi] = {"acl": []}
                # Create dict of existing ACLs by name
                have_acls = {acl["name"]: acl for acl in merged[afi].get("acl", [])}
                for want_acl in want_netconf[afi].get("acl", []):
                    if want_acl["name"] in have_acls:
                        # Merge ACEs
                        have_acl = have_acls[want_acl["name"]]
                        if "aces" in want_acl and "ace" in want_acl["aces"]:
                            if "aces" not in have_acl:
                                have_acl["aces"] = {"ace": []}
                            elif "ace" not in have_acl["aces"]:
                                have_acl["aces"]["ace"] = []
                            # Create dict of existing ACEs by sequence
                            have_aces = {
                                str(ace.get("sequence", "")): ace for ace in have_acl["aces"]["ace"]
                            }
                            # Merge or add new ACEs
                            for want_ace in want_acl["aces"]["ace"]:
                                seq = str(want_ace.get("sequence", ""))
                                if seq in have_aces:
                                    have_aces[seq].update(want_ace)
                                else:
                                    have_acl["aces"]["ace"].append(want_ace)
                    else:
                        # Add new ACL
                        merged[afi]["acl"].append(want_acl)
        return merged

    def _get_replaced_config(self, have, want):
        """Get replaced configuration for NETCONF"""
        have_netconf = self._convert_to_netconf_format(have)
        want_netconf = self._convert_to_netconf_format(want)
        # Replace specific ACLs
        replaced = have_netconf.copy()
        for afi in ["ipv4", "ipv6"]:
            if afi in want_netconf:
                if afi not in replaced:
                    replaced[afi] = {"acl": []}
                # Create dict of existing ACLs by name
                have_acls = {
                    acl["name"]: idx for idx, acl in enumerate(replaced[afi].get("acl", []))
                }
                for want_acl in want_netconf[afi].get("acl", []):
                    if want_acl["name"] in have_acls:
                        # Replace existing ACL
                        idx = have_acls[want_acl["name"]]
                        replaced[afi]["acl"][idx] = want_acl
                    else:
                        # Add new ACL
                        replaced[afi]["acl"].append(want_acl)
        return replaced

    def _get_overridden_config(self, have, want):
        """Get overridden configuration for NETCONF"""
        # Simply return the wanted configuration, overriding everything
        return self._convert_to_netconf_format(want)

    def _get_delete_config(self, have, want):
        """Get delete configuration for NETCONF"""
        if not want:
            # Delete all ACLs
            return {}
        else:
            # Delete specific ACLs
            have_netconf = self._convert_to_netconf_format(have)
            want_names = {}
            # Collect ACL names to delete by AFI
            for afi_config in want:
                afi = afi_config["afi"]
                want_names[afi] = [acl["name"] for acl in afi_config.get("acls", [])]
            # Keep only ACLs not in the delete list
            filtered = {}
            for afi in ["ipv4", "ipv6"]:
                if afi in have_netconf and afi in want_names:
                    filtered_acls = []
                    for acl in have_netconf[afi].get("acl", []):
                        if acl["name"] not in want_names[afi]:
                            filtered_acls.append(acl)
                    if filtered_acls:
                        filtered[afi] = {"acl": filtered_acls}
                elif afi in have_netconf:
                    # Keep all ACLs for this AFI
                    filtered[afi] = have_netconf[afi]
            return filtered

    def generate_commands(self):
        """Generate configuration commands to send based on want, have and desired state"""
        wantd = {
            (afi["afi"], acl["name"]): (afi["afi"], acl)
            for afi in self.want
            for acl in afi.get("acls", [])
        }
        haved = {
            (afi["afi"], acl["name"]): (afi["afi"], acl)
            for afi in self.have
            for acl in afi.get("acls", [])
        }
        # Turn all lists of ACEs into dicts for easier processing
        for key in wantd:
            afi, acl = wantd[key]
            if acl.get("aces"):
                acl["aces"] = {ace["sequence"]: ace for ace in acl["aces"]}
        for key in haved:
            afi, acl = haved[key]
            if acl.get("aces"):
                acl["aces"] = {ace["sequence"]: ace for ace in acl["aces"]}
        if self.state == "overridden":
            self.commands = self._state_overridden(wantd, haved)
        elif self.state == "deleted":
            self.commands = self._state_deleted(wantd, haved)
        elif self.state == "merged":
            self.commands = self._state_merged(wantd, haved)
        elif self.state == "replaced":
            self.commands = self._state_replaced(wantd, haved)

    def _state_merged(self, wantd, haved):
        """The command generator when state is merged
        Args:
            wantd: The desired ACL configuration
            haved: The current ACL configuration
        Returns:
            list: Commands to merge configuration
        """
        commands = []
        for key, (want_afi, want_acl) in wantd.items():
            if key in haved:
                have_afi, have_acl = haved[key]
                commands.extend(self._update_acl(want_afi, want_acl, have_acl))
            else:
                commands.extend(self._create_acl(want_afi, want_acl))
        return commands

    def _state_replaced(self, wantd, haved):
        """The command generator when state is replaced
        Args:
            wantd: The desired ACL configuration
            haved: The current ACL configuration
        Returns:
            list: Commands to replace configuration
        """
        commands = []
        for key, (want_afi, want_acl) in wantd.items():
            if key in haved:
                have_afi, have_acl = haved[key]
                commands.extend(self._replace_acl(want_afi, want_acl, have_acl))
            else:
                commands.extend(self._create_acl(want_afi, want_acl))
        return commands

    def _state_overridden(self, wantd, haved):
        """The command generator when state is overridden
        Args:
            wantd: The desired ACL configuration
            haved: The current ACL configuration
        Returns:
            list: Commands to override configuration
        """
        commands = []
        # Delete ACLs that are not in want
        for key, (have_afi, have_acl) in haved.items():
            if key not in wantd:
                commands.extend(self._delete_acl(have_afi, have_acl["name"]))
        # Replace existing ACLs with want
        for key, (want_afi, want_acl) in wantd.items():
            if key in haved:
                have_afi, have_acl = haved[key]
                commands.extend(self._replace_acl(want_afi, want_acl, have_acl))
            else:
                commands.extend(self._create_acl(want_afi, want_acl))
        return commands

    def _state_deleted(self, wantd, haved):
        """The command generator when state is deleted
        Args:
            wantd: The desired ACL configuration (what to delete)
            haved: The current ACL configuration
        Returns:
            list: Commands to delete configuration
        """
        commands = []
        if wantd:
            # Delete specific ACLs mentioned in want
            for key, (want_afi, want_acl) in wantd.items():
                if key in haved:
                    have_afi, have_acl = haved[key]
                    if want_acl.get("aces"):
                        # Delete specific ACEs
                        commands.extend(self._delete_aces(have_afi, have_acl, want_acl["aces"]))
                    else:
                        # Delete entire ACL
                        commands.extend(self._delete_acl(have_afi, have_acl["name"]))
        else:
            # Delete all ACLs
            for key, (have_afi, have_acl) in haved.items():
                commands.extend(self._delete_acl(have_afi, have_acl["name"]))
        return commands

    def _create_acl(self, afi, acl):
        """Create a new ACL
        Args:
            afi: Address family identifier
            acl: ACL configuration
        Returns:
            list: Commands to create the ACL
        """
        commands = []
        # DNOS uses access-list syntax
        commands.append("access-list")
        if afi == "ipv4":
            acl_cmd = f"ipv4 {acl['name']}"
        elif afi == "ipv6":
            acl_cmd = f"ipv6 {acl['name']}"
        else:
            acl_cmd = f"eth {acl['name']}"
        commands.append(acl_cmd)
        if acl.get("description"):
            commands.append(f"  remark {acl['description']}")
        if acl.get("aces"):
            for seq, ace in sorted(acl["aces"].items()):
                ace_cmd = self._generate_ace_command(afi, ace)
                if ace_cmd:
                    commands.append(f"  {ace_cmd}")
        commands.append("!")
        return commands

    def _update_acl(self, afi, want_acl, have_acl):
        """Update an existing ACL
        Args:
            afi: Address family identifier
            want_acl: Desired ACL configuration
            have_acl: Current ACL configuration
        Returns:
            list: Commands to update the ACL
        """
        commands = []
        # DNOS uses access-list syntax
        commands.append("access-list")
        if afi == "ipv4":
            acl_cmd = f"ipv4 {want_acl['name']}"
        elif afi == "ipv6":
            acl_cmd = f"ipv6 {want_acl['name']}"
        else:
            acl_cmd = f"eth {want_acl['name']}"
        acl_updates = []
        # Update description if changed
        if want_acl.get("description") != have_acl.get("description"):
            if have_acl.get("description") and not want_acl.get("description"):
                acl_updates.append("  no remark")
            elif want_acl.get("description"):
                acl_updates.append(f"  remark {want_acl['description']}")
        # Process ACEs
        want_aces = want_acl.get("aces", {})
        have_aces = have_acl.get("aces", {})
        # Add or update ACEs
        for seq, ace in want_aces.items():
            if seq not in have_aces or self._ace_differs(ace, have_aces.get(seq, {})):
                ace_cmd = self._generate_ace_command(afi, ace)
                if ace_cmd:
                    acl_updates.append(f"  {ace_cmd}")
        if acl_updates:
            commands.append(acl_cmd)
            commands.extend(acl_updates)
            commands.append("!")
        return commands

    def _replace_acl(self, afi, want_acl, have_acl):
        """Replace an existing ACL
        Args:
            afi: Address family identifier
            want_acl: Desired ACL configuration
            have_acl: Current ACL configuration
        Returns:
            list: Commands to replace the ACL
        """
        commands = []
        # Delete the existing ACL
        commands.extend(self._delete_acl(afi, have_acl["name"]))
        # Create the new ACL
        commands.extend(self._create_acl(afi, want_acl))
        return commands

    def _delete_acl(self, afi, acl_name):
        """Delete an ACL
        Args:
            afi: Address family identifier
            acl_name: Name of the ACL to delete
        Returns:
            list: Commands to delete the ACL
        """
        # DNOS uses access-list syntax
        commands = ["access-list"]
        if afi == "ipv4":
            commands.append(f"no ipv4 {acl_name}")
        elif afi == "ipv6":
            commands.append(f"no ipv6 {acl_name}")
        else:
            commands.append(f"no eth {acl_name}")
        return commands

    def _delete_aces(self, afi, have_acl, ace_sequences):
        """Delete specific ACEs from an ACL
        Args:
            afi: Address family identifier
            have_acl: Current ACL configuration
            ace_sequences: Dictionary of ACE sequences to delete
        Returns:
            list: Commands to delete specific ACEs
        """
        commands = []
        # DNOS uses access-list syntax
        commands.append("access-list")
        if afi == "ipv4":
            acl_cmd = f"ipv4 {have_acl['name']}"
        elif afi == "ipv6":
            acl_cmd = f"ipv6 {have_acl['name']}"
        else:
            acl_cmd = f"eth {have_acl['name']}"
        commands.append(acl_cmd)
        for seq in ace_sequences:
            if seq in have_acl.get("aces", {}):
                commands.append(f"  no {seq}")
        commands.append("!")
        return commands

    def _generate_ace_command(self, afi, ace):
        """Generate an ACE command
        Args:
            afi: Address family identifier
            ace: ACE configuration
        Returns:
            str: ACE command
        """
        # DNOS ACL uses correct rule-based syntax discovered from device
        action = ace.get("action", "allow")
        if action == "description":
            # For description rules: rule X description "text"
            description = ace.get("description", "")
            return f"rule {str(ace['sequence'])} description \"{description}\""
        else:
            # For allow/deny rules: rule X allow/deny (not rule X action allow)
            return f"rule {str(ace['sequence'])} {action}"
        # Note: The current DNOS CLI doesn't support inline match commands
        # Each rule is created first, then match commands would be added separately
        # This simplified approach creates the rule with the basic action

    def _ace_differs(self, want_ace, have_ace):
        """Check if two ACEs differ
        Args:
            want_ace: Desired ACE
            have_ace: Current ACE
        Returns:
            bool: True if ACEs differ, False otherwise
        """
        # Remove sequence from comparison as it's the key
        want_copy = {k: v for k, v in want_ace.items() if k != "sequence"}
        have_copy = {k: v for k, v in have_ace.items() if k != "sequence"}
        return want_copy != have_copy
