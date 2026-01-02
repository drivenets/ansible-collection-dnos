# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class NetconfTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(NetconfTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # Define parsers
    PARSERS = [
        {
            "name": "enabled",
            "getval": re.compile(
                r"""
                ^\s*admin-state\s+(?P<state>enabled|disabled)$
                """,
                re.VERBOSE,
            ),
            "setval": "admin-state {{ 'enabled' if enabled else 'disabled' }}",
            "result": {"enabled": "{{ True if state == 'enabled' else False }}"},
        },
        {
            "name": "port",
            "getval": re.compile(
                r"""
                ^\s*port\s+(?P<port>\d+)$
                """,
                re.VERBOSE,
            ),
            "setval": "port {{ port }}",
            "result": {"port": "{{ port|int }}"},
        },
        {
            "name": "vrf",
            "getval": re.compile(
                r"""
                ^\s*vrf\s+(?P<vrf>\S+)$
                """,
                re.VERBOSE,
            ),
            "setval": "vrf {{ vrf }}",
            "result": {"vrf": "{{ vrf }}"},
        },
        {
            "name": "session_timeout",
            "getval": re.compile(
                r"""
                ^\s*session-timeout\s+(?P<timeout>\d+)$
                """,
                re.VERBOSE,
            ),
            "setval": "session-timeout {{ session_timeout }}",
            "result": {"session_timeout": "{{ timeout|int }}"},
        },
        {
            "name": "max_sessions",
            "getval": re.compile(
                r"""
                ^\s*max-sessions\s+(?P<sessions>\d+)$
                """,
                re.VERBOSE,
            ),
            "setval": "max-sessions {{ max_sessions }}",
            "result": {"max_sessions": "{{ sessions|int }}"},
        },
        {
            "name": "class_of_service",
            "getval": re.compile(
                r"""
                ^\s*class-of-service\s+(?P<cos>\d+)$
                """,
                re.VERBOSE,
            ),
            "setval": "class-of-service {{ class_of_service }}",
            "result": {"class_of_service": "{{ cos|int }}"},
        },
    ]
