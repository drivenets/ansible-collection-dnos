# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the dnos_acls module.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


class AclsArgs(object):
    """The arg spec for the dnos_acls module."""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "afi": {
                    "type": "str",
                    "required": True,
                    "choices": ["ipv4", "ipv6", "ethernet"],
                },
                "acls": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {
                            "type": "str",
                            "required": True,
                        },
                        "aces": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "sequence": {
                                    "type": "str",
                                    "required": True,
                                },
                                "grant": {
                                    "type": "str",
                                    "choices": ["allow", "deny", "description"],
                                },
                                "nexthop1": {
                                    "type": "str",
                                },
                                "next_table": {
                                    "type": "str",
                                },
                                "vrf": {
                                    "type": "str",
                                },
                                "protocol": {
                                    "type": "str",
                                },
                                "source": {
                                    "type": "dict",
                                    "options": {
                                        "address": {
                                            "type": "str",
                                        },
                                        "wildcard_bits": {
                                            "type": "str",
                                        },
                                        "host": {
                                            "type": "str",
                                        },
                                        "any": {
                                            "type": "bool",
                                        },
                                        "port_protocol": {
                                            "type": "dict",
                                            "options": {
                                                "eq": {
                                                    "type": "str",
                                                },
                                                "gt": {
                                                    "type": "str",
                                                },
                                                "lt": {
                                                    "type": "str",
                                                },
                                                "neq": {
                                                    "type": "str",
                                                },
                                                "range": {
                                                    "type": "dict",
                                                    "options": {
                                                        "start": {
                                                            "type": "str",
                                                        },
                                                        "end": {
                                                            "type": "str",
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                "destination": {
                                    "type": "dict",
                                    "options": {
                                        "address": {
                                            "type": "str",
                                        },
                                        "wildcard_bits": {
                                            "type": "str",
                                        },
                                        "host": {
                                            "type": "str",
                                        },
                                        "any": {
                                            "type": "bool",
                                        },
                                        "port_protocol": {
                                            "type": "dict",
                                            "options": {
                                                "eq": {
                                                    "type": "str",
                                                },
                                                "gt": {
                                                    "type": "str",
                                                },
                                                "lt": {
                                                    "type": "str",
                                                },
                                                "neq": {
                                                    "type": "str",
                                                },
                                                "range": {
                                                    "type": "dict",
                                                    "options": {
                                                        "start": {
                                                            "type": "str",
                                                        },
                                                        "end": {
                                                            "type": "str",
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                "dscp": {
                                    "type": "str",
                                },
                                "packet_length": {
                                    "type": "str",
                                },
                                "qos_tcm": {
                                    "type": "str",
                                },
                                "description": {
                                    "type": "str",
                                },
                                "log": {
                                    "type": "bool",
                                },
                                "cir_mbps": {
                                    "type": "str",
                                },
                                "cbs_kbytes": {
                                    "type": "str",
                                },
                                # Ethernet-specific fields
                                "src_mac": {
                                    "type": "str",
                                },
                                "dest_mac": {
                                    "type": "str",
                                },
                                "ether_type": {
                                    "type": "str",
                                },
                                "packet_type": {
                                    "type": "str",
                                },
                                "inner_vlan": {
                                    "type": "str",
                                },
                                "outer_vlan": {
                                    "type": "str",
                                },
                            },
                        },
                    },
                },
            },
        },
        "running_config": {
            "type": "str",
        },
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }  # argument_spec
