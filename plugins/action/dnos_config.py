# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dnos_config action plugin.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
from ansible.plugins.action.normal import ActionModule
from ansible.utils.display import Display


display = Display()


class ActionModule(ActionModule):
    """Action plugin for dnos_config module."""

    def run(self, tmp=None, task_vars=None):
        """Execute the action plugin."""
        # Connection validation is handled by base class
        return super(ActionModule, self).run(tmp=tmp, task_vars=task_vars)
