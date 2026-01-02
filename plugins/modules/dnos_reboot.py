#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = r"""
---
module: dnos_reboot
short_description: Reboot Drivenets DNOS devices
description:
  - This module provides the ability to reboot Drivenets DNOS network devices.
  - The module sends a reboot command to the device and handles the confirmation prompt.
  - After you execute the reboot command, the device restarts and the connection closes.
version_added: '1.0.0'
author:
  - Abishek Suresh Kumar (@askumar-dn)
  - Gennady Mescheryakov (@gennadym-dn)
  - Dragos Lazar (@dlazar-dn)
notes:
  - Tested against DNOS 25.2.x
  - This module works with connection C(network_cli).
  - The module will close the connection after sending the reboot command.
  - Use with caution as this will restart the target device.
attributes:
  check_mode:
    description: This module supports check mode.
    support: full
options:
  reboot:
    description:
      - When set to C(true), reboots the device.
      - When set to C(false), takes no action.
    type: bool
    default: false
    required: false
"""

EXAMPLES = r"""
# Reboot the device
- name: Reboot DNOS device
  drivenets.dnos.dnos_reboot:
    reboot: true

# Check if reboot is needed (no action taken)
- name: Check reboot status
  drivenets.dnos.dnos_reboot:
    reboot: false
"""

RETURN = r"""
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Device reboot initiated successfully"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.argspec.reboot.reboot import (
    RebootArgs,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.config.reboot.reboot import (
    RebootModule,
)


def main():
    """
    Main entry point for module execution
    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=RebootArgs.argument_spec,
        supports_check_mode=True,
    )
    result = RebootModule(module).execute_reboot()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
