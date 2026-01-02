# -*- coding: utf-8 -*-
"""
DNOS Interface Utilities
Provides interface naming, validation, and hardware-aware capabilities
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import re


# Hardware type definitions and capabilities
HARDWARE_CAPABILITIES = {
    # NCP-40C (40-port 100G) Hardware
    "NCP-40C": {
        "models": ["S9700-53DX"],
        "physical_speeds": [100],
        "port_ranges": {100: (1, 40)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88690",
        "breakout_support": ["4x25G", "2x50G"],
    },
    # NCP-38E (18-port 400G + Management)
    "NCP-38E": {
        "models": ["ASA926-18XKE", "ASA926-18XKA"],
        "physical_speeds": [400],
        "port_ranges": {400: (1, 18)},
        "mgmt_ports": (37, 38),
        "cpu_ports": (39, 40),
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88890",
        "ai_optimized": True,
    },
    # NCP-10CD (10-port 400G)
    "NCP-10CD": {
        "models": ["S9700-23D"],
        "physical_speeds": [400],
        "port_ranges": {400: (1, 10)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88690",
        "breakout_support": ["8x50G", "4x100G"],
    },
    # NCP-36CD-S (36-port 400G Standalone)
    "NCP-36CD-S": {
        "models": ["S9710-76D"],
        "physical_speeds": [400],
        "port_ranges": {400: (1, 36)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88850",
        "fabric_ports": 40,
    },
    # NCP-36CD-S-SA (36-port 400G Standalone Specific)
    "NCP-36CD-S-SA": {
        "models": ["S9610-36D"],
        "physical_speeds": [400],
        "port_ranges": {400: (1, 36)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88690",
    },
    # NCP-64X12C-S (76-port Mixed Speed)
    "NCP-64X12C-S": {
        "models": ["S9701-82DC"],
        "physical_speeds": [10, 100],
        "port_ranges": {10: (1, 64), 100: (65, 76)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88802",
    },
    # NCP-64X8C-S (72-port Mixed Speed)
    "NCP-64X8C-S": {
        "models": ["S9600-72XC"],
        "physical_speeds": [10, 100],
        "port_ranges": {10: (1, 64), 100: (65, 72)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88802",
    },
    # NCP-40C8CD (48-port EMUX without KBP)
    "NCP-40C8CD": {
        "models": ["S9610-48DX"],
        "physical_speeds": [100, 400],
        "port_ranges": {100: (1, 40), 400: (41, 48)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88840",
        "emux_topology": True,
    },
    # NCP-40C6CD-S (46-port EMUX with KBP)
    "NCP-40C6CD-S": {
        "models": ["S9610-46DX"],
        "physical_speeds": [100, 400],
        "port_ranges": {100: (1, 40), 400: (41, 46)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "BCM88840",
        "emux_topology": True,
        "kbp_support": True,
    },
    # NCP-32CD (32-port 100G)
    "NCP-32CD": {
        "models": ["CS1-8203", "CS1-WB2000-32FH", "AS9286-32D"],
        "physical_speeds": [100],
        "port_ranges": {100: (1, 32)},
        "max_bundles": 999,
        "max_irb": 4094,
        "bcm_chip": "CS1-Q200-A2-0",
    },
}
# Interface naming patterns for DNOS (standalone deployment, ncp_id=0, node_id=0)
INTERFACE_PATTERNS = {
    # Physical interfaces based on speed
    "physical": {
        "ge1": r"^ge1-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])$",  # 1G ports
        "ge10": r"^ge10-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])$",  # 10G ports
        "ge25": r"^ge25-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])$",  # 25G ports
        "ge100": r"^ge100-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])$",  # 100G ports
        "ge400": r"^ge400-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])$",  # 400G ports
    },
    # VLAN sub-interfaces
    "vlan_sub": {
        "ge10_vlan": r"^ge10-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])\.([1-9]|[1-9][0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
        "ge25_vlan": r"^ge100-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])\.([1-9]|[1-9][0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
        "ge100_vlan": r"^ge100-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])\.([1-9]|[1-9][0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
        "ge400_vlan": r"^ge400-0/0/([1-9]|[1-9][0-9]|[1-6][0-9][0-9])\.([1-9]|[1-9][0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
    },
    # Bundle (LAG) interfaces
    "bundle": {
        "bundle": r"^bundle-([1-9]|[1-9][0-9]{1,2})$",  # bundle-1 to bundle-999
        "bundle_vlan": r"^bundle-([1-9]|[1-9][0-9]{1,2})\.([1-9]|[1-9][0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
    },
    # Loopback interfaces
    "loopback": {
        # lo0 to lo65535
        "loopback": r"^lo([0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
    },
    # Management interfaces (standalone: nce=ncc, node_id=0)
    "management": {
        "mgmt0": r"^mgmt0$",  # Out-of-band logical management
        "mgmt_ncc": r"^mgmt-ncc-0(/[0-9]+)?$",  # Physical management
    },
    # Control interfaces (standalone: nce=ncc, node_id=0)
    "control": {
        "ctrl_ncc": r"^ctrl-ncc-0/[0-9]+$",  # Control interfaces
    },
    # IPMI interfaces (standalone: nce=ncc, node_id=0)
    "ipmi": {
        "ipmi_ncc": r"^ipmi-ncc-0/0$",  # IPMI interfaces
    },
    # Console interfaces (standalone: nce=ncc, node_id=0)
    "console": {
        "console_ncc": r"^console-ncc-0/0$",  # Console interfaces
    },
    # Special interfaces
    "special": {
        "gre_tunnel": r"^gre-tunnel-([1-9]|[1-9][0-9]{1,4})$",  # GRE tunnels
        # IRB interfaces (1-4094)
        "irb": r"^irb([1-9]|[1-9][0-9]{1,3}|[1-3][0-9]{3}|40[0-8][0-9]|409[0-4])$",
        "ice": r"^ice[0-9]+$",  # ICE interfaces
        "fabric": r"^fab-ncc-0/[0-9]+/[0-9]+(/[0-9]+)?$",  # Fabric interfaces
        "sge": r"^sge[0-9]+-0/0/[0-9]+$",  # SGE interfaces
        "nat": r"^nat-[0-9]+$",  # NAT interfaces
    },
}


def get_interface_type(interface_name):
    """
    Determine the type of interface based on the name.
    Args:
        interface_name (str): The interface name to classify
    Returns:
        str: The interface type or 'unknown' if not recognized
    """
    if not interface_name:
        return "unknown"
    # Check each pattern category
    for category, patterns in INTERFACE_PATTERNS.items():
        for interface_type, pattern in patterns.items():
            if re.match(pattern, interface_name):
                return interface_type
    return "unknown"


def validate_interface_name(interface_name, hardware_type=None):
    """
    Validate an interface name against DNOS naming conventions.
    Args:
        interface_name (str): The interface name to validate
        hardware_type (str, optional): Specific hardware type for additional validation
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not interface_name:
        return False, "Interface name cannot be empty"
    interface_type = get_interface_type(interface_name)
    if interface_type == "unknown":
        return False, f"Invalid interface name format: {interface_name}"
    # Hardware-specific validation
    if hardware_type and hardware_type in HARDWARE_CAPABILITIES:
        hw_caps = HARDWARE_CAPABILITIES[hardware_type]
        # Validate physical interface ports against hardware capabilities
        if interface_type.startswith("ge"):
            speed_match = re.match(r"^ge(\d+)-0/0/(\d+)", interface_name)
            if speed_match:
                speed = int(speed_match.group(1))
                port = int(speed_match.group(2))
                if speed not in hw_caps["physical_speeds"]:
                    return False, f"Speed {speed}G not supported on hardware type {hardware_type}"
                if speed in hw_caps["port_ranges"]:
                    min_port, max_port = hw_caps["port_ranges"][speed]
                    if not (min_port <= port <= max_port):
                        return (
                            False,
                            f"Port {port} out of range for {speed}G interfaces ({min_port}-{max_port})",
                        )
    return True, ""


def normalize_interface_name(interface_name):
    """
    Normalize interface name to standard DNOS format.
    Args:
        interface_name (str): The interface name to normalize
    Returns:
        str: Normalized interface name
    """
    if not interface_name:
        return interface_name
    # Remove extra spaces and convert to lowercase for processing
    normalized = interface_name.strip().lower()
    # Handle legacy naming conversions
    legacy_patterns = {
        # Convert ge-X/Y/Z to ge100-X/Y/Z (legacy pattern)
        r"^ge-(\d+)/(\d+)/(\d+)$": r"ge100-\1/\2/\3",
    }
    for pattern, replacement in legacy_patterns.items():
        if re.match(pattern, normalized):
            normalized = re.sub(pattern, replacement, normalized)
            break
    return normalized


def get_interface_examples(hardware_type=None, count=2):
    """
    Generate valid interface name examples for documentation and testing.
    Args:
        hardware_type (str, optional): Hardware type to generate specific examples
        count (int): Number of examples per type
    Returns:
        dict: Dictionary of interface type to example list
    """
    examples = {
        "physical_100g": [f"ge100-0/0/{i}" for i in range(1, count + 1)],
        "physical_400g": [f"ge400-0/0/{i}" for i in range(1, count + 1)],
        "vlan_sub": [f"ge100-0/0/{i}.100" for i in range(1, count + 1)],
        "bundle": [f"bundle-{i}" for i in range(1, count + 1)],
        "bundle_vlan": [f"bundle-{i}.100" for i in range(1, count + 1)],
        "loopback": [f"lo{i}" for i in range(1, count + 1)],
        "irb": [f"irb{100 + i}" for i in range(1, count + 1)],
        "management": ["mgmt0", "mgmt-ncc-0", "mgmt-ncc-1"],
        "control": ["ctrl-ncc-0/0", "ctrl-ncc-0/1", "ctrl-ncp-0/0", "ctrl-ncp-0/1"][:count],
    }
    # Hardware-specific examples
    if hardware_type and hardware_type in HARDWARE_CAPABILITIES:
        hw_caps = HARDWARE_CAPABILITIES[hardware_type]
        examples["physical_speeds"] = []
        for speed in hw_caps["physical_speeds"]:
            if speed in hw_caps["port_ranges"]:
                min_port, max_port = hw_caps["port_ranges"][speed]
                examples["physical_speeds"].extend(
                    [f"ge{speed}-0/0/{min_port}", f"ge{speed}-0/0/{min(min_port + 1, max_port)}"][
                        :count
                    ]
                )
    return examples


def get_default_interface_examples():
    """
    Get default interface examples for use in module documentation.
    Provides realistic examples based on common DNOS hardware.
    Returns:
        dict: Default interface examples for different categories
    """
    return {
        "physical": ["ge100-0/0/1", "ge100-0/0/2"],
        "high_speed": ["ge400-0/0/1", "ge400-0/0/2"],
        "mixed_speed": ["ge10-0/0/1", "ge100-0/0/65"],  # Based on NCP-64X12C-S
        "vlan_sub": ["ge100-0/0/1.100", "ge100-0/0/2.200"],
        "bundle": ["bundle-1", "bundle-2"],
        "bundle_vlan": ["bundle-1.100", "bundle-2.200"],
        "loopback": ["lo0", "lo1"],
        "irb": ["irb100", "irb200"],
        "management": ["mgmt0", "mgmt-ncc-0"],
        "special": ["gre-tunnel-1", "ctrl-ncc-0/0"],
    }


# Legacy interface patterns (for backward compatibility during migration)
LEGACY_INTERFACE_PATTERNS = {
    r"^ge-(\d+)/(\d+)/(\d+)$": "ge100-{}/{}/{}",  # Convert legacy ge- prefix to ge100-
    r"^lo(\d+)$": "lo{}",  # Convert loX to loX
    r"^Loopback(\d+)$": "lo{}",  # Convert LoopbackX to loX
}


def convert_legacy_interface_name(interface_name):
    """
    Convert legacy interface naming to current DNOS standard.
    Args:
        interface_name (str): Legacy interface name
    Returns:
        str: Converted interface name in DNOS standard format
    """
    if not interface_name:
        return interface_name
    for pattern, template in LEGACY_INTERFACE_PATTERNS.items():
        match = re.match(pattern, interface_name)
        if match:
            if "{}" in template:
                return template.format(*match.groups())
            else:
                return template
    return interface_name


# Export commonly used interface examples for module documentation
DEFAULT_EXAMPLES = get_default_interface_examples()
