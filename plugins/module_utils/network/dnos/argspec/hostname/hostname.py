# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the dnos_hostname module.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


class HostnameArgs(object):
    """The arg spec for the dnos_hostname module."""

    argument_spec = {
        "config": {
            "options": {"hostname": {"type": "str", "required": False, "aliases": ["name"]}},
            "type": "dict",
        },
        "running_config": {
            "type": "str",
        },
        "state": {
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
            "type": "str",
        },
    }  # pylint: disable=C0301
