# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
DNOS NETCONF utility functions for modules with YANG support
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import json

from xml.etree import ElementTree as ET

from ansible.module_utils.connection import Connection, ConnectionError


class DNOSNetconfUtils:
    """DNOS NETCONF utility functions for modules with comprehensive YANG support"""

    def __init__(self, module):
        """
        Initialize NETCONF utilities.
        Args:
            module: AnsibleModule instance
        """
        self.module = module
        self._connection = None
        self._netconf = None
        self._capabilities = None
        self._yang_capabilities = None

    @property
    def connection(self):
        """Get or create the connection object."""
        if self._connection is None:
            self._connection = Connection(self.module._socket_path)
        return self._connection

    @property
    def netconf(self):
        """Get NETCONF plugin instance with YANG support."""
        if self._netconf is None:
            # Import here to avoid circular imports
            from ansible_collections.drivenets.dnos.plugins.netconf.dnos import Netconf

            # Check if connection supports NETCONF
            if hasattr(self.connection, "netconf"):
                self._netconf = self.connection.netconf
            else:
                # For direct NETCONF connections
                try:
                    caps = json.loads(self.connection.get_capabilities())
                    if caps.get("network_api") == "netconf":
                        # Create NETCONF instance with connection manager
                        self._netconf = Netconf(self.connection._manager)
                except Exception:
                    raise ConnectionError("Device does not support NETCONF operations")
        return self._netconf

    def check_netconf_capability(self):
        """
        Check if device supports NETCONF.
        Returns:
            bool: True if NETCONF is supported
        """
        try:
            caps = self.get_capabilities()
            return caps.get("network_api") == "netconf"
        except Exception:
            return False

    def get_capabilities(self):
        """
        Get device capabilities.
        Returns:
            dict: Device capabilities
        """
        if self._capabilities is None:
            try:
                self._capabilities = json.loads(self.connection.get_capabilities())
            except ConnectionError as exc:
                self.module.fail_json(msg=f"Failed to get device capabilities: {str(exc)}")
        return self._capabilities

    def get_yang_capabilities(self):
        """
        Get YANG capabilities supported by device.
        Returns:
            list: List of YANG model capabilities
        """
        if self._yang_capabilities is None:
            caps = self.get_capabilities()
            self._yang_capabilities = []
            for cap in caps.get("server_capabilities", []):
                if "drivenets.com/ns/yang" in cap:
                    self._yang_capabilities.append(cap)
        return self._yang_capabilities

    def supports_yang_model(self, model_name):
        """
        Check if device supports specific YANG model.
        Args:
            model_name: Name of YANG model
        Returns:
            bool: True if model is supported
        """
        yang_caps = self.get_yang_capabilities()
        model_namespace = f"http://drivenets.com/ns/yang/dn-{model_name}"
        return any(model_namespace in cap for cap in yang_caps)

    def get_yang_config(self, yang_module, source="running", filter_xpath=None, vrf_name=None):
        """
        Get configuration using YANG model.
        Args:
            yang_module: YANG module name
            source: Configuration source ('running', 'candidate')
            filter_xpath: Optional XPath filter
            vrf_name: Optional VRF name for VRF-specific protocols (BGP, VRRP)
        Returns:
            dict: Parsed configuration data
        """
        try:
            if filter_xpath:
                # Build XPath-based filter
                filter_xml = self._build_xpath_filter(yang_module, filter_xpath)
            else:
                # Use module's default filter with VRF support
                filter_xml = self.netconf.get_yang_filter(
                    yang_module, "get-config", vrf_name=vrf_name
                )
            # Get configuration
            config_xml = self.netconf.get_config(source=source, filter=filter_xml)
            # Parse XML to dict
            return self._xml_to_dict(config_xml)
        except Exception as e:
            self.module.fail_json(msg=f"Failed to get {yang_module} config: {str(e)}")

    def edit_yang_config(
        self,
        yang_module,
        config_data,
        target="candidate",
        operation="merge",
        test_option=None,
        error_option=None,
        vrf_name=None,
    ):
        """
        Edit configuration using YANG model.
        Args:
            yang_module: YANG module name
            config_data: Configuration data (dict)
            target: Target datastore
            operation: Default operation ('merge', 'replace', 'create', 'delete')
            test_option: Test option for edit-config
            error_option: Error option for edit-config
            vrf_name: Optional VRF name for VRF-specific protocols (BGP, VRRP)
        Returns:
            bool: True if successful
        """
        try:
            # Use netconf plugin's new method with VRF support
            self.netconf.edit_protocol_config(
                yang_module,
                config_data,
                target=target,
                operation=operation,
                test_option=test_option,
                error_option=error_option,
                vrf_name=vrf_name,
            )
            return True
        except Exception as e:
            self.module.fail_json(msg=f"Failed to edit {yang_module} config: {str(e)}")

    def validate_yang_config(self, yang_module, config_data):
        """
        Validate configuration against YANG model.
        Args:
            yang_module: YANG module name
            config_data: Configuration to validate
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            return self.netconf.validate_yang_config(yang_module, config_data)
        except Exception as e:
            return False, str(e)

    def commit_config(self, confirmed=False, timeout=None, comment=None):
        """
        Commit candidate configuration.
        Args:
            confirmed: Enable confirmed commit
            timeout: Timeout for confirmed commit
            comment: Commit comment
        Returns:
            bool: True if successful
        """
        try:
            self.netconf.commit(confirmed=confirmed, timeout=timeout, comment=comment)
            return True
        except Exception as e:
            self.module.fail_json(msg=f"Failed to commit configuration: {str(e)}")

    def discard_changes(self):
        """
        Discard candidate configuration changes.
        Returns:
            bool: True if successful
        """
        try:
            self.netconf.discard_changes()
            return True
        except Exception as e:
            # Log error but don't fail
            self.module.warn(f"Failed to discard changes: {str(e)}")
            return False

    def lock_config(self, target="candidate"):
        """
        Lock configuration datastore.
        Args:
            target: Datastore to lock
        Returns:
            bool: True if successful
        """
        try:
            self.netconf.lock(target=target)
            return True
        except Exception as e:
            self.module.fail_json(msg=f"Failed to lock {target}: {str(e)}")

    def unlock_config(self, target="candidate"):
        """
        Unlock configuration datastore.
        Args:
            target: Datastore to unlock
        Returns:
            bool: True if successful
        """
        try:
            self.netconf.unlock(target=target)
            return True
        except Exception as e:
            # Log error but don't fail
            self.module.warn(f"Failed to unlock {target}: {str(e)}")
            return False

    def validate_datastore(self, source="candidate"):
        """
        Validate configuration datastore.
        Args:
            source: Datastore to validate
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            self.netconf.validate(source=source)
            return True, None
        except Exception as e:
            return False, str(e)

    def get_config_diff(self, source="candidate", target="running"):
        """
        Get configuration diff between datastores.
        Args:
            source: Source datastore
            target: Target datastore
        Returns:
            str: Configuration diff
        """
        try:
            source_config = self.netconf.get_config(source=source)
            target_config = self.netconf.get_config(source=target)
            # Simple diff - modules can implement more sophisticated diff
            if source_config == target_config:
                return ""
            else:
                return f"Source ({source}) and target ({target}) configurations differ"
        except Exception as e:
            self.module.fail_json(msg=f"Failed to get config diff: {str(e)}")

    def copy_config(self, source, target):
        """
        Copy configuration between datastores.
        Args:
            source: Source datastore or config URL
            target: Target datastore
        Returns:
            bool: True if successful
        """
        try:
            # Build copy-config RPC
            rpc_xml = f"""
            <copy-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <source>{self._get_datastore_xml(source)}</source>
                <target>{self._get_datastore_xml(target)}</target>
            </copy-config>
            """
            # Execute RPC
            self.netconf.m.rpc(rpc_xml)
            return True
        except Exception as e:
            self.module.fail_json(msg=f"Failed to copy config: {str(e)}")

    def _get_datastore_xml(self, datastore):
        """Get datastore XML element."""
        if datastore in ["running", "candidate", "startup"]:
            return f"<{datastore}/>"
        else:
            # Assume it's a URL or other source
            return f"<url>{datastore}</url>"

    def _build_xpath_filter(self, yang_module, xpath):
        """Build XPath-based filter."""
        namespace = self.netconf.YANG_NAMESPACES.get(yang_module)
        if not namespace:
            raise ValueError(f"Unknown YANG module: {yang_module}")
        # Build filter with XPath
        return f"""
        <filter type="xpath" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
                select="{xpath}"
                xmlns:dn="{namespace}"/>
        """

    def _xml_to_dict(self, xml_string):
        """
        Convert XML string to dictionary.
        Args:
            xml_string: XML configuration string
        Returns:
            dict: Parsed configuration
        """
        try:
            root = ET.fromstring(xml_string)
            return self._element_to_dict(root)
        except Exception:
            # Return raw XML if parsing fails
            return {"_raw_xml": xml_string}

    def _element_to_dict(self, element):
        """Convert XML element to dictionary recursively."""
        result = {}
        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # No children
                return element.text.strip()
            else:
                result["_text"] = element.text.strip()
        # Process children
        children = {}
        for child in element:
            # Remove namespace from tag
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            # Convert hyphen to underscore for Python compatibility
            tag = tag.replace("-", "_")
            child_data = self._element_to_dict(child)
            if tag in children:
                # Multiple children with same tag - convert to list
                if not isinstance(children[tag], list):
                    children[tag] = [children[tag]]
                children[tag].append(child_data)
            else:
                children[tag] = child_data
        result.update(children)
        # Simplify if only text content
        if len(result) == 1 and "_text" in result:
            return result["_text"]
        return result if result else None

    def execute_rpc(self, rpc_name, rpc_params=None):
        """
        Execute custom RPC operation.
        Args:
            rpc_name: Name of RPC operation
            rpc_params: Optional RPC parameters (dict)
        Returns:
            dict: RPC response
        """
        try:
            # Check if RPC module exists
            rpc_module = f"rpc-{rpc_name}"
            if rpc_module not in self.netconf.YANG_NAMESPACES:
                raise ValueError(f"Unknown RPC: {rpc_name}")
            namespace = self.netconf.YANG_NAMESPACES[rpc_module]
            # Build RPC XML
            rpc_elem = ET.Element(rpc_name, xmlns=namespace)
            if rpc_params:
                self._dict_to_element(rpc_elem, rpc_params)
            rpc_xml = ET.tostring(rpc_elem, encoding="unicode")
            # Execute RPC
            response = self.netconf.m.rpc(rpc_xml)
            # Parse response
            return self._xml_to_dict(response.xml)
        except Exception as e:
            self.module.fail_json(msg=f"Failed to execute RPC {rpc_name}: {str(e)}")

    def _dict_to_element(self, parent, data):
        """Convert dictionary to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                # Skip special keys
                if key.startswith("@") or key.startswith("_"):
                    continue
                # Convert underscore to hyphen
                xml_key = key.replace("_", "-")
                if isinstance(value, list):
                    for item in value:
                        elem = ET.SubElement(parent, xml_key)
                        if isinstance(item, dict):
                            self._dict_to_element(elem, item)
                        else:
                            elem.text = str(item)
                elif isinstance(value, dict):
                    elem = ET.SubElement(parent, xml_key)
                    self._dict_to_element(elem, value)
                elif value is not None:
                    elem = ET.SubElement(parent, xml_key)
                    elem.text = str(value)
        else:
            parent.text = str(data)

    def batch_edit_config(self, edits, target="candidate", stop_on_error=True):
        """
        Perform batch configuration edits.
        Args:
            edits: List of (yang_module, config_data, operation) tuples
            target: Target datastore
            stop_on_error: Stop on first error
        Returns:
            tuple: (success_count, errors)
        """
        success_count = 0
        errors = []
        # Lock configuration
        self.lock_config(target=target)
        try:
            for yang_module, config_data, operation in edits:
                try:
                    self.edit_yang_config(
                        yang_module, config_data, target=target, operation=operation
                    )
                    success_count += 1
                except Exception as e:
                    errors.append({"module": yang_module, "error": str(e)})
                    if stop_on_error:
                        break
            # Validate if any edits succeeded
            if success_count > 0:
                is_valid, error = self.validate_datastore(target)
                if not is_valid:
                    errors.append({"module": "validation", "error": error})
                    # Discard invalid changes
                    self.discard_changes()
                    success_count = 0
        finally:
            # Always unlock
            self.unlock_config(target=target)
        return success_count, errors

    def get_module_state(self, yang_module):
        """
        Get operational state for a YANG module.
        Args:
            yang_module: YANG module name
        Returns:
            dict: Operational state data
        """
        try:
            # Use get operation instead of get-config for state data
            filter_xml = self.netconf.get_yang_filter(yang_module, "get")
            # Get state data
            state_xml = self.netconf.m.get(filter=filter_xml).data_xml
            # Parse and return
            return self._xml_to_dict(state_xml)
        except Exception as e:
            self.module.fail_json(msg=f"Failed to get {yang_module} state: {str(e)}")


def check_netconf_support(module):
    """
    Check if the device supports NETCONF.
    Args:
        module: AnsibleModule instance
    Returns:
        bool: True if NETCONF is supported
    """
    utils = DNOSNetconfUtils(module)
    return utils.check_netconf_capability()


def get_netconf_config(module, yang_module, source="running"):
    """
    Get configuration for a YANG module via NETCONF.
    Args:
        module: AnsibleModule instance
        yang_module: YANG module name
        source: Configuration source
    Returns:
        dict: Configuration data
    """
    utils = DNOSNetconfUtils(module)
    return utils.get_yang_config(yang_module, source=source)


def edit_netconf_config(module, yang_module, config_data, commit=True):
    """
    Edit configuration for a YANG module via NETCONF.
    Args:
        module: AnsibleModule instance
        yang_module: YANG module name
        config_data: Configuration data
        commit: Whether to commit changes
    Returns:
        bool: True if successful
    """
    utils = DNOSNetconfUtils(module)
    # Validate configuration
    is_valid, error = utils.validate_yang_config(yang_module, config_data)
    if not is_valid:
        module.fail_json(msg=f"Configuration validation failed: {error}")
    # Apply configuration
    utils.edit_yang_config(yang_module, config_data)
    # Commit if requested
    if commit:
        utils.commit_config()
    return True
