# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the dnos_reboot module
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


class RebootArgs(object):
    """The arg spec for the dnos_reboot module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "reboot": {
            "type": "bool",
            "default": False,
        },
    }
