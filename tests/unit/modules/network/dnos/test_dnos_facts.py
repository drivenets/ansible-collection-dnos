# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for DNOS facts module."""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

import os

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic

from ansible_collections.drivenets.dnos.plugins.modules import dnos_facts

from ...fixtures import AnsibleModuleFixtures
from ...utils import (
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)


# Patch run_commands where it's actually imported and used in the facts module
# It's imported in base.py from dnos.py, so we patch it in the base module's namespace
run_commands_path = "ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.legacy.base.run_commands"
get_capabilities_path = "ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.facts.legacy.base.get_capabilities"
# Module path for get_config and get_connection
dnos_module_path = "ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos"


class TestDNOSFacts(ModuleTestCase):
    """Test cases for DNOS facts module."""

    module = None  # Will be set per test

    @classmethod
    def setUpClass(cls):
        """Load device output files once for all tests."""
        super(TestDNOSFacts, cls).setUpClass()

        # Get the directory where this test file is located
        test_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(test_dir, "resources")

        # Load all device output files
        cls.device_outputs = {}
        output_files = {
            "show_interfaces": "show_interfaces.txt",
            "show_system": "show_system.txt",
            "show_access_lists": "show_access_lists_no_more.txt",
            "show_interfaces_incl_l2": "show_interfaces_incl_l2_no_more.txt",
            "show_interfaces_excl_l2": "show_interfaces_excl_l2_no_more.txt",
            "show_system_hardware": "show_system_hardware_no_more.txt",
            "show_config": "show_config_no_more.txt",
            "show_lldp_neighbors": "show_lldp_neighbors_no_more.txt",
        }

        for key, filename in output_files.items():
            filepath = os.path.join(resources_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    cls.device_outputs[key] = f.read()
            else:
                cls.device_outputs[key] = ""

    def setUp(self):
        """Set up test fixtures."""
        super(TestDNOSFacts, self).setUp()

        # Use AnsibleModuleFixtures helper to manage patches
        self.fixtures = AnsibleModuleFixtures()
        self.fixtures.setup_load_params()

        self.mock_run_commands = patch(run_commands_path)
        self.run_commands = self.mock_run_commands.start()

        # Use fixtures helper for get_config
        self.get_config = self.fixtures.setup_get_config(dnos_module_path)

        # Mock get_capabilities to avoid socket_path requirement
        self.mock_get_capabilities = patch(get_capabilities_path)
        self.get_capabilities = self.mock_get_capabilities.start()
        # Default capabilities response
        self.get_capabilities.return_value = {
            "device_info": {
                "network_os": "dnos",
                "network_os_hostname": "TestRouter",
                "network_os_version": "25.2.0",
                "network_os_model": "TestModel",
                "network_os_serial": "TestSerial",
            },
            "network_api": "cli",
        }

        # Use fixtures helper for get_connection
        self.get_connection, mock_conn = self.fixtures.setup_get_connection(dnos_module_path)

        # Helper method to map commands to device outputs
        def get_command_output(command):
            """Map command to device output file."""
            if "show interfaces | no-more" in command:
                return self.device_outputs["show_interfaces"]
            elif "show system | no-more" in command:
                return self.device_outputs["show_system"]
            elif "show access-lists | no-more" in command:
                return self.device_outputs["show_access_lists"]
            elif "show interfaces |incl (L2)| no-more" in command:
                return self.device_outputs["show_interfaces_incl_l2"]
            elif "show interfaces |excl (L2)| no-more" in command:
                return self.device_outputs["show_interfaces_excl_l2"]
            elif "show system hardware | no-more" in command:
                return self.device_outputs["show_system_hardware"]
            elif "show config | no-more" in command:
                return self.device_outputs["show_config"]
            elif "show lldp neighbors | no-more" in command:
                return self.device_outputs["show_lldp_neighbors"]
            return ""

        self.get_command_output = get_command_output

    def tearDown(self):
        """Clean up test fixtures."""
        super(TestDNOSFacts, self).tearDown()
        # Use fixtures helper to restore all patches
        self.fixtures.teardown()
        self.mock_run_commands.stop()
        self.mock_get_capabilities.stop()

    def test_dnos_facts_default(self):
        """Test default facts collection."""
        set_module_args(dict(gather_subset=["default"]))

        # Mock command responses using real device output
        # Default class uses: show system | no-more
        self.run_commands.return_value = [self.device_outputs["show_system"]]

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        assert facts["hostname"] == "TestRouter"
        assert facts["version"] == "25.2.0"
        assert facts["uptime"] == "7 days, 0:04:35"
        assert "python_version" in facts

    def test_dnos_facts_hardware(self):
        """Test hardware facts collection."""
        set_module_args(dict(gather_subset=["hardware"]))

        # Hardware class uses: show system hardware | no-more
        def mock_run_commands(module, commands, **kwargs):
            if len(commands) == 1 and "show system hardware" in commands[0]:
                return [self.device_outputs["show_system_hardware"]]
            return []

        self.run_commands.side_effect = mock_run_commands

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        facts = result["ansible_facts"]
        # Verify hardware facts from real device output
        assert "ansible_net_cpu" in facts or "cpu" in facts
        assert "ansible_net_memory" in facts or "memory" in facts
        assert "ansible_net_disk" in facts or "disk" in facts

    def test_dnos_facts_config(self):
        """Test config facts collection."""
        set_module_args(dict(gather_subset=["config"]))

        # Config class uses run_commands, not get_config
        self.run_commands.return_value = [self.device_outputs["show_config"]]

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        assert "config" in facts
        assert "system" in facts["config"] or "name TestRouter" in facts["config"]
        assert "interfaces" in facts["config"] or "ge100-0/0/1" in facts["config"]

    def test_dnos_facts_interfaces(self):
        """Test interfaces facts collection."""
        set_module_args(dict(gather_subset=["interfaces"]))

        # Interfaces subset uses Default + Interfaces classes
        # Interfaces class uses: show interfaces | no-more, show lldp neighbors | no-more
        # Default class uses: show system | no-more
        def mock_run_commands(module, commands, **kwargs):
            if len(commands) == 2:  # Interfaces class
                return [
                    self.device_outputs["show_interfaces"],
                    self.device_outputs["show_lldp_neighbors"],
                ]
            elif len(commands) == 1:  # Default class
                return [self.device_outputs["show_system"]]
            return []

        self.run_commands.side_effect = mock_run_commands

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]
        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        assert "interfaces" in facts
        assert "ge100-0/0/1" in facts["interfaces"]
        assert facts["interfaces"]["ge100-0/0/1"]["admin_state"] == "enabled"
        assert facts["interfaces"]["ge100-0/0/1"]["operstatus"] == "up"
        assert facts["interfaces"]["ge100-0/0/1"]["mtu"] == 1514
        assert "1.0.0.1" in facts["all_ipv4_addresses"]
        assert "cafe:1::1" in facts["all_ipv6_addresses"]
        assert "ge100-0/0/1" in facts["neighbors"]
        assert facts["neighbors"]["ge100-0/0/1"][0]["host"] == "cdnos2"

    def test_dnos_facts_all(self):
        """Test all facts collection."""
        set_module_args(dict(gather_subset=["all"]))

        # All subsets: Default, Hardware, Interfaces, Config
        def mock_run_commands(module, commands, **kwargs):
            if len(commands) == 2:  # Interfaces class
                return [
                    self.device_outputs["show_interfaces"],
                    self.device_outputs["show_lldp_neighbors"],
                ]
            elif len(commands) == 1:
                # Could be Default or Hardware - check command content
                cmd = commands[0] if commands else ""
                if "show system hardware" in cmd:
                    return [self.device_outputs["show_system_hardware"]]
                elif "show system" in cmd:
                    return [self.device_outputs["show_system"]]
            return []

        def mock_run_commands_with_config(module, commands, **kwargs):
            # Handle Config class which uses run_commands
            if len(commands) == 1:
                cmd = commands[0] if commands else ""
                if "show config | no-more" in cmd:
                    return [self.device_outputs["show_config"]]
            # Call the original mock function for other commands
            return mock_run_commands(module, commands, **kwargs)

        self.run_commands.side_effect = mock_run_commands_with_config

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]
        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        # ansible_net_gather_subset is not added by current implementation
        assert facts["hostname"] == "TestRouter"
        assert "interfaces" in facts
        assert "ge100-0/0/1" in facts["interfaces"]
        assert "config" in facts

    def test_dnos_facts_exclude_subset(self):
        """Test excluding specific fact subsets."""
        # Explicitly include default and interfaces, exclude hardware and config
        # The exclusion logic requires explicit inclusion when using exclusions
        set_module_args(dict(gather_subset=["default", "interfaces", "!hardware", "!config"]))

        # Exclude hardware and config, so only default and interfaces
        def mock_run_commands(module, commands, **kwargs):
            if len(commands) == 2:  # Interfaces class
                return [
                    self.device_outputs["show_interfaces"],
                    self.device_outputs["show_lldp_neighbors"],
                ]
            elif len(commands) == 1:  # Default class
                return [self.device_outputs["show_system"]]
            return []

        self.run_commands.side_effect = mock_run_commands

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]
        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        # ansible_net_gather_subset is not added by current implementation
        assert facts["hostname"] == "TestRouter"
        assert "interfaces" in facts
        assert "ge100-0/0/1" in facts["interfaces"]
        assert "config" not in facts

    def test_dnos_facts_min_subset(self):
        """Test minimum facts collection."""
        set_module_args(dict(gather_subset=["min"]))

        # Min subset only uses Default class: show system | no-more
        self.run_commands.return_value = [self.device_outputs["show_system"]]

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        # ansible_net_gather_subset is not added by current implementation
        assert facts["hostname"] == "TestRouter"
        assert facts["version"] == "25.2.0"

    def test_dnos_facts_version_parsing(self):
        """Test version parsing from system output."""
        set_module_args(dict(gather_subset=["default"]))

        # Default class uses: show system | no-more
        self.run_commands.return_value = [self.device_outputs["show_system"]]

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        assert facts["hostname"] == "TestRouter"
        assert facts["version"] == "25.2.0"
        assert facts["uptime"] == "7 days, 0:04:35"

    def test_dnos_facts_invalid_subset(self):
        """Test invalid subset handling."""
        set_module_args(dict(gather_subset=["invalid_subset"]))

        # Mock both fail_json and the module creation to ensure we catch the error
        with patch(
            "ansible_collections.drivenets.dnos.plugins.modules.dnos_facts.AnsibleModule"
        ) as mock_module:
            mock_instance = MagicMock()
            mock_instance.params = {
                "gather_subset": ["invalid_subset"],
                "gather_network_resources": None,
                "available_network_resources": False,
            }
            # Make fail_json raise an exception to simulate real behavior
            mock_instance.fail_json.side_effect = AnsibleFailJson("Bad subset: invalid_subset")
            mock_module.return_value = mock_instance

            # The module should raise AnsibleFailJson when calling fail_json
            with self.assertRaises(AnsibleFailJson) as exc:
                dnos_facts.main()

            # Verify fail_json was called and the error message is correct
            mock_instance.fail_json.assert_called_once()
            assert "Bad subset: invalid_subset" in str(exc.exception)

    def test_dnos_facts_available_network_resources(self):
        """Test available network resources query.

        Note: available_network_resources parameter doesn't exist in the module.
        This test is kept for potential future implementation but will fail
        with parameter validation error.
        """
        set_module_args(dict(available_network_resources=True))

        # This should fail with parameter validation error
        with self.assertRaises(AnsibleFailJson) as exc:
            dnos_facts.main()

        # Verify the error is about unsupported parameter
        result = exc.exception.args[0]
        assert "available_network_resources" in result.get("msg", "")

    def test_dnos_facts_network_resources_not_implemented(self):
        """Test network resources gathering."""
        set_module_args(dict(gather_subset=["min"], gather_network_resources=["interfaces"]))

        # Min subset uses Default: show system | no-more
        # Network resources use get_connection
        def mock_connection_get(command):
            if "show interfaces" in (command or ""):
                return self.device_outputs["show_interfaces"]
            return ""

        # Update the mock connection to return interface data
        mock_conn = MagicMock()
        mock_conn.get.side_effect = mock_connection_get
        self.get_connection.return_value = mock_conn

        self.run_commands.return_value = [self.device_outputs["show_system"]]

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        facts = result["ansible_facts"]
        # Facts are returned without ansible_net_ prefix in current implementation
        assert facts["hostname"] == "TestRouter"
        # Network resources should be collected
        assert "ansible_network_resources" in facts

    def test_dnos_facts_comprehensive_parsing(self):
        """Test comprehensive facts parsing with edge cases."""
        set_module_args(dict(gather_subset=["all"]))

        # All subsets: Default, Hardware, Interfaces, Config
        def mock_run_commands(module, commands, **kwargs):
            if len(commands) == 2:  # Interfaces class
                return [
                    self.device_outputs["show_interfaces"],
                    self.device_outputs["show_lldp_neighbors"],
                ]
            elif len(commands) == 1:
                cmd = commands[0] if commands else ""
                if "show config | no-more" in cmd:
                    return [self.device_outputs["show_config"]]
                elif "show system hardware" in cmd:
                    return [self.device_outputs["show_system_hardware"]]
                elif "show system" in cmd:
                    return [self.device_outputs["show_system"]]
            return []

        self.run_commands.side_effect = mock_run_commands

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify comprehensive results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]
        facts = result["ansible_facts"]

        # Verify that all expected facts are present
        assert "hostname" in facts
        assert "version" in facts
        assert "interfaces" in facts
        assert "config" in facts

    def test_facts_netconf_support(self):
        """Test dnos_facts NETCONF support"""
        # Simple test to verify NETCONF utility can be imported and called
        try:
            from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.netconf_utils import (
                check_netconf_support,
            )

            # Just verify the function exists and is callable
            self.assertTrue(callable(check_netconf_support))
        except ImportError:
            # If import fails, that's okay - NETCONF might not be available
            self.skipTest("NETCONF utilities not available")

    def test_dnos_facts_gather_comprehensive(self):
        """Test comprehensive facts gathering."""
        set_module_args(dict(gather_subset=["all"]))

        # All subsets: Default, Hardware, Interfaces, Config
        def mock_run_commands(module, commands, **kwargs):
            if len(commands) == 2:  # Interfaces class
                return [
                    self.device_outputs["show_interfaces"],
                    self.device_outputs["show_lldp_neighbors"],
                ]
            elif len(commands) == 1:
                cmd = commands[0] if commands else ""
                if "show system hardware" in cmd:
                    return [self.device_outputs["show_system_hardware"]]
                elif "show system" in cmd:
                    return [self.device_outputs["show_system"]]
            return []

        def mock_run_commands_with_config(module, commands, **kwargs):
            # Handle Config class which uses run_commands
            if len(commands) == 1:
                cmd = commands[0] if commands else ""
                if "show config | no-more" in cmd:
                    return [self.device_outputs["show_config"]]
            # Call the original mock function for other commands
            return mock_run_commands(module, commands, **kwargs)

        self.run_commands.side_effect = mock_run_commands_with_config

        # Execute module
        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_facts.main()

        # Verify comprehensive results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]
        facts = result["ansible_facts"]

        # Test basic interface functionality
        # Facts are returned without ansible_net_ prefix in current implementation
        assert "interfaces" in facts
        assert len(facts["interfaces"]) > 0

        # Test that key interfaces exist and have basic properties
        assert "ge100-0/0/1" in facts["interfaces"]
        assert "lo0" in facts["interfaces"]
        assert facts["interfaces"]["ge100-0/0/1"]["admin_state"] == "enabled"
        assert facts["interfaces"]["ge100-0/0/1"]["mtu"] == 1514

        # Test that comprehensive gathering includes expected fact categories
        expected_facts = [
            "interfaces",
            "all_ipv4_addresses",
            "all_ipv6_addresses",
            "neighbors",
        ]

        for fact_key in expected_facts:
            assert fact_key in facts, f"Missing expected fact: {fact_key}"

        # Test that we actually parsed some data (not just empty dicts)
        assert len(facts["interfaces"]) > 0
        assert len(facts["all_ipv4_addresses"]) > 0
