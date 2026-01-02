# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The hostname template for DNOS.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class HostnameTemplate(NetworkTemplate):
    """
    The DNOS hostname template class.
    This template generates configuration commands for hostname management.
    """

    def __init__(self, lines=None, module=None):
        """
        Initialize the hostname template.
        Args:
            lines: Configuration lines
            module: The module instance
        """
        super(HostnameTemplate, self).__init__(
            lines=lines,
            tmplt=self,
            module=module,
        )

    # Template definitions for hostname configuration
    PARSERS = [
        {
            "name": "hostname",
            "getval": re.compile(
                r"""
                ^\s*name\s+(?P<name>\S+)$
                """,
                re.VERBOSE | re.MULTILINE,
            ),
            "setval": "configure\nsystem\nname {{ name }}\ncommit",
            "result": {"name": "{{ name }}"},
        }
    ]
