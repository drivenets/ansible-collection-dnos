# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The facts class for dnos
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.acls.acls import (
    AclsFacts,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.hostname.hostname import (
    HostnameFacts,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.l2_interfaces.interfaces import (
    L2InterfacesFacts,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.l3_interfaces.interfaces import (
    L3InterfacesFacts,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.legacy.base import (
    Config,
    Default,
    Hardware,
    Interfaces,
)


FACT_LEGACY_SUBSETS = dict(
    default=Default,
    hardware=Hardware,
    config=Config,
    interfaces=Interfaces,
)

FACT_RESOURCE_SUBSETS = dict(
    interfaces=InterfacesFacts,
    hostname=HostnameFacts,
    # 'acl_interfaces': None,
    acls=AclsFacts,
    # 'bgp_global': None,
    l2_interfaces=L2InterfacesFacts,
    l3_interfaces=L3InterfacesFacts,
    # 'lacp': None,
    # 'lacp_interfaces': None,
    # 'lag_interfaces': None,
    # 'lldp_global': None,
    # 'lldp_interfaces': None,
    # 'logging_global': None,
    # 'ntp_global': None,
    # 'prefix_lists': None,
    # 'snmp_server': None,
    # 'static_routes': None,
    # 'bgp_address_family': None
    # ping: None,
)


class Facts(object):
    """The fact class for dnos"""

    def __init__(self, module):
        self.module = module
        self.warnings = []
        self.legacy_facts = dict()
        self.resource_facts = dict()

    def get_facts(self):
        """Collect the facts for dnos

        :rtype: dict
        :returns: Facts gathered
        """
        gather_subset = self.module.params["gather_subset"]
        gather_network_resources = self.module.params["gather_network_resources"]

        # Initialize the facts list
        facts = dict()
        facts["ansible_network_resources"] = dict()

        if not gather_subset:
            gather_subset = ["!config"]

        # Transform gather_subset to a list if it's a string
        if isinstance(gather_subset, str):
            gather_subset = [gather_subset]

        # Process the legacy facts
        self.get_network_legacy_facts(FACT_LEGACY_SUBSETS, gather_subset)
        facts.update(self.legacy_facts)

        # Process the network resource facts
        self.get_network_resource_facts(FACT_RESOURCE_SUBSETS, gather_network_resources)
        facts["ansible_network_resources"].update(self.resource_facts)

        return facts, self.warnings

    def get_network_legacy_facts(self, fact_legacy_obj, gather_subset):
        """Collect the legacy facts

        :param fact_legacy_obj: The legacy facts object
        :param gather_subset: The list of legacy facts to gather
        """

        runable_subsets = set()
        exclude_subsets = set()
        minimal_gather_subset = frozenset(["default"])

        for subset in gather_subset:
            if subset == "all":
                runable_subsets.update(fact_legacy_obj.keys())
                continue
            if subset == "min":
                runable_subsets.update(minimal_gather_subset)
                continue
            if subset.startswith("!"):
                subset = subset[1:]
                if subset == "min":
                    exclude_subsets.update(minimal_gather_subset)
                    continue
                if subset == "all":
                    exclude_subsets.update(fact_legacy_obj.keys() - minimal_gather_subset)
                    continue
                exclude = True
            else:
                exclude = False

            if subset not in fact_legacy_obj:
                self.warnings.append("Subset %s not found" % subset)
            elif exclude:
                exclude_subsets.add(subset)
            else:
                runable_subsets.add(subset)

        # Only apply fallback logic if no explicit subsets were specified
        # If user specified exclusions (like !all), respect them
        if not runable_subsets and not exclude_subsets:
            runable_subsets.update(fact_legacy_obj.keys())

        runable_subsets.difference_update(exclude_subsets)

        facts = dict()
        for subset in runable_subsets:
            instances = fact_legacy_obj[subset](self.module)
            instances.populate()
            facts.update(instances.facts)

        self.legacy_facts = facts

    def get_network_resource_facts(self, fact_resource_obj, gather_network_resources):
        """Collect the network resource facts

        :param fact_resource_obj: The resource facts object
        :param gather_network_resources: The list of network resources to gather
        """

        if not gather_network_resources:
            return

        if isinstance(gather_network_resources, str):
            gather_network_resources = [gather_network_resources]

        runable_subsets = set()
        exclude_subsets = set()

        for resource in gather_network_resources:
            if resource == "all":
                runable_subsets.update(fact_resource_obj.keys())
                continue
            if resource.startswith("!"):
                resource = resource[1:]
                if resource == "all":
                    exclude_subsets.update(fact_resource_obj.keys())
                    continue
                exclude = True
            else:
                exclude = False

            if resource not in fact_resource_obj:
                self.warnings.append("Resource %s not found" % resource)
            elif exclude:
                exclude_subsets.add(resource)
            else:
                runable_subsets.add(resource)

        if not runable_subsets:
            runable_subsets.update(fact_resource_obj.keys())

        runable_subsets.difference_update(exclude_subsets)

        for resource in runable_subsets:
            instances = fact_resource_obj[resource](self.module)
            instances.populate()
            self.resource_facts[resource] = instances.facts
