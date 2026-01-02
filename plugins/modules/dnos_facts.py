#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for dnos_facts
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = """
---
module: dnos_facts
version_added: "1.0.0"
short_description: Get facts about dnos devices
description:
  - Collect facts from network devices running the dnos operating
    system. This module places the facts gathered in the fact tree keyed by the
    respective resource name. The facts module always collects a
    base set of facts from the device and can enable or disable
    collection of additional facts.
author:
  - Abishek Suresh Kumar (@askumar-dn)
  - Gennady Mescheryakov (@gennadym-dn)
  - Dragos Lazar (@dlazar-dn)
options:
  gather_subset:
    description:
      - When supplied, this argument restricts the facts collected
        to a given subset. Possible values for this argument include
        all, hardware, config, and interfaces. You can specify a list of
        values to include a larger subset. Values can also be used
        with an initial C(M(!)) to specify that a specific subset should
        not be collected.
    required: false
    type: list
    elements: str
    choices:
      - all
      - min
      - default
      - hardware
      - config
      - interfaces
      - "!all"
      - "!min"
      - "!default"
      - "!hardware"
      - "!config"
      - "!interfaces"
    default: '!config'
  gather_network_resources:
    description:
      - When supplied, this argument restricts the facts collected
        to a given subset. Possible values for this argument include
        all and the resources like interfaces, vlans, and so on.
        You can specify a list of values to include a larger subset.
        Values can also be used with an initial C(M(!)) to specify that a
        specific subset should not be collected.
    required: false
    type: list
    elements: str
"""

EXAMPLES = """
- name: Gather all facts
  drivenets.dnos.dnos_facts:
    gather_subset: all
    gather_network_resources: all

- name: Collect only the config and default facts
  drivenets.dnos.dnos_facts:
    gather_subset:
      - config

- name: Do not collect hardware facts
  drivenets.dnos.dnos_facts:
    gather_subset:
      - "!hardware"
"""

RETURN = """
ansible_net_gather_subset:
  description: The list of fact subsets collected from the device.
  returned: always
  type: list
ansible_net_model:
  description: The model name returned from the device.
  returned: always
  type: str
ansible_net_serialnum:
  description: The serial number of the remote device.
  returned: always
  type: str
ansible_net_version:
  description: The operating system version running on the remote device.
  returned: always
  type: str
ansible_net_hostname:
  description: The configured hostname of the device.
  returned: always
  type: str
ansible_net_filesystems:
  description: All file system names available on the device.
  returned: when hardware is configured
  type: list
ansible_net_memfree_mb:
  description: The available free memory on the remote device in Mb.
  returned: when hardware is configured
  type: int
ansible_net_memtotal_mb:
  description: The total memory on the remote device in Mb.
  returned: when hardware is configured
  type: int
ansible_net_config:
  description: The current active config from the device.
  returned: when config is configured
  type: str
ansible_net_all_ipv4_addresses:
  description: All IPv4 addresses configured on the device.
  returned: when interfaces is configured
  type: list
ansible_net_all_ipv6_addresses:
  description: All IPv6 addresses configured on the device.
  returned: when interfaces is configured
  type: list
ansible_net_interfaces:
  description: A dictionary of all interfaces running on the system.
  returned: when interfaces is configured
  type: dict
ansible_net_neighbors:
  description: The list of LLDP neighbors from the remote device.
  returned: when interfaces is configured
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.argspec.facts.facts import (
    FactsArgs,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.facts import Facts


def main():
    """
    Main entry point for module execution

    :returns: ansible_facts
    """
    module = AnsibleModule(argument_spec=FactsArgs.argument_spec, supports_check_mode=True)
    warnings = []

    try:
        result = Facts(module).get_facts()
        ansible_facts, additional_warnings = result
        warnings.extend(additional_warnings)

        module.exit_json(changed=False, ansible_facts=ansible_facts, warnings=warnings)
    except Exception as e:
        module.fail_json(msg=str(e), warnings=warnings)


if __name__ == "__main__":
    main()
