# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The arg spec for the dnos facts module.
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type


class FactsArgs(object):
    """The arg spec for the dnos facts module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "gather_subset": dict(
            type="list",
            elements="str",
            choices=[
                "all",
                "min",
                "default",
                "hardware",
                "config",
                "interfaces",
                "!all",
                "!min",
                "!default",
                "!hardware",
                "!config",
                "!interfaces",
            ],
            default=["!config"],
        ),
        "gather_network_resources": dict(type="list", elements="str"),
    }
