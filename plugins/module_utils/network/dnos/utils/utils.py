# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dnos utils file.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)


def normalize_interface(name):
    """Normalize interface name for consistent comparison.
    Args:
        name: Interface name to normalize
    Returns:
        str: Normalized interface name
    """
    if not name:
        return None
    # DNOS uses dash notation: ge100-0/0/1, ge100-0/0/1, etc
    # Just ensure consistent format
    return name.strip()


def dict_to_set(data):
    """Convert dictionary data to a set for comparison.
    Args:
        data: Dictionary to convert
    Returns:
        set: Set of tuples representing the dictionary
    """
    result = []
    for key, value in data.items():
        if isinstance(value, dict):
            for item in dict_to_set(value):
                result.append((key,) + item)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for i in dict_to_set(item):
                        result.append((key,) + i)
                else:
                    result.append((key, item))
        else:
            result.append((key, value))
    return set(result)


def validate_interface_name(name):
    """Validate DNOS interface name format.
    Args:
        name: Interface name to validate
    Returns:
        bool: True if valid, False otherwise
    """
    if not name:
        return False
    # Valid DNOS interface patterns (based on actual device testing)
    patterns = [
        r"^ge\d+-\d+/\d+/\d+$",  # Physical interfaces (ge100-0/0/1)
        r"^ge\d+-\d+/\d+/\d+/\d+$",  # Breakout interfaces (ge100-0/0/1/0)
        r"^ge\d+-\d+/\d+/\d+\.\d+$",  # Physical VLAN sub-interfaces (ge100-0/0/1.100)
        r"^ge\d+-\d+/\d+/\d+/\d+\.\d+$",  # Breakout VLAN sub-interfaces (ge100-0/0/1/0.100)
        r"^bundle-\d+$",  # Bundle interfaces (bundle-56)
        r"^bundle-\d+\.\d+$",  # Bundle VLAN sub-interfaces (bundle-56.100)
        r"^lo\d+$",  # Loopback
    ]
    for pattern in patterns:
        if re.match(pattern, name):
            return True
    return False


def get_interface_type(name):
    """Get interface type from name.
    Args:
        name: Interface name
    Returns:
        str: Interface type
    """
    if not name:
        return None
    if name.startswith("ge-") or name.startswith("ge"):
        return "GigabitEthernet"
    elif name.startswith("xe-"):
        return "10GigabitEthernet"
    elif name.startswith("et-"):
        return "100GigabitEthernet"
    elif name.startswith("bundle-"):
        return "PortChannel"
    elif name.startswith("lo"):
        return "Loopback"
    else:
        return "Unknown"


def remove_empties_from_list(config_list):
    """Remove empty elements from a list of configurations.
    Args:
        config_list: List of configuration dictionaries
    Returns:
        list: List with empty elements removed
    """
    if not config_list:
        return []
    result = []
    for config in config_list:
        if isinstance(config, dict):
            cleaned = {k: v for k, v in config.items() if v is not None}
            if cleaned:
                result.append(cleaned)
        elif config is not None:
            result.append(config)
    return result


class DnosFactsBase(FactsBase):
    """Base class for DNOS facts gathering"""

    def __init__(self, module, subspec="config", options="options"):
        super(DnosFactsBase, self).__init__(module)
        self._module = module
        self.subspec = subspec
        self.options = options


def xml_to_dict(xml_data):
    """Convert XML data to dictionary format"""
    try:
        import xml.etree.ElementTree as ET

        if isinstance(xml_data, str):
            root = ET.fromstring(xml_data)
        else:
            root = xml_data

        def element_to_dict(element):
            result = {}
            for child in element:
                child_data = element_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data or child.text)
                else:
                    result[child.tag] = child_data or child.text
            return result or element.text

        return {root.tag: element_to_dict(root)}
    except Exception:
        return {}


def netconf_get(module, filter_xml=None):
    """Get configuration via NETCONF"""
    try:
        from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network import (
            get_resource_connection,
        )

        connection = get_resource_connection(module)
        if filter_xml:
            return connection.get(filter=filter_xml)
        else:
            return connection.get()
    except Exception as e:
        return {"error": str(e)}


# Duplicate normalize_interface function removed - using the one defined earlier
