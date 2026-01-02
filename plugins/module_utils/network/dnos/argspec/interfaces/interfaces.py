# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the dnos_interfaces module.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


class InterfacesArgs(object):
    """The arg spec for the dnos_interfaces module."""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {
                    "type": "str",
                    "required": True,
                },
                "description": {
                    "type": "str",
                },
                "enabled": {
                    "type": "bool",
                },
                "speed": {
                    "type": "str",
                    "choices": [
                        "auto",
                        "10",
                        "100",
                        "1000",
                        "10000",
                        "25000",
                        "40000",
                        "100000",
                        "400000",
                    ],
                },
                "mtu": {
                    "type": "int",
                },
                "duplex": {
                    "type": "str",
                    "choices": ["full", "half", "auto"],
                },
                "l2_service": {
                    "type": "bool",
                },
                "max_links": {
                    "type": "int",
                },
                "min_links": {
                    "type": "int",
                },
                "ipv4_mtu": {
                    "type": "int",
                },
                "ipv6_mtu": {
                    "type": "int",
                },
                "mpls_mtu": {
                    "type": "int",
                },
                "l2_mtu": {
                    "type": "int",
                },
                "mpls": {
                    "type": "str",
                    "choices": ["enabled", "disabled"],
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
