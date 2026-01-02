# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit test file for dnos_reboot module
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from unittest.mock import MagicMock

from ansible_collections.drivenets.dnos.plugins.modules import dnos_reboot

from ...fixtures import AnsibleModuleFixtures
from ...utils import (
    ModuleTestCase,
    set_module_args,
)


class TestDnosRebootModule(ModuleTestCase):
    """Test the dnos_reboot module"""

    module = dnos_reboot

    def setUp(self):
        """Setup for tests"""
        super(TestDnosRebootModule, self).setUp()

        # Use AnsibleModuleFixtures to manage patches
        self.fixtures = AnsibleModuleFixtures()
        self.fixtures.setup_load_params()

        # Mock get_connection using fixtures
        module_path = "ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.config.reboot.reboot"
        self.get_connection, self.mock_connection = self.fixtures.setup_get_connection(module_path)

    def tearDown(self):
        """Teardown for tests"""
        super(TestDnosRebootModule, self).tearDown()
        # Restore all patches using fixtures
        self.fixtures.teardown()

    def test_dnos_reboot_no_action(self):
        """Test reboot module with reboot=false (no action)"""
        set_module_args(dict(reboot=False))

        result = self.execute_module(changed=False)

        # Verify all required fields are present
        assert result["changed"] is False
        assert result["failed"] is False
        assert result["rebooted"] is False
        assert result["commands"] == []
        assert "No reboot requested" in result["msg"]

    def test_dnos_reboot_success(self):
        """Test successful reboot operation"""
        set_module_args(dict(reboot=True))

        # Mock connection methods
        self.mock_connection.send_command = MagicMock()
        self.mock_connection.receive = MagicMock(side_effect=Exception("Connection closed"))

        result = self.execute_module(changed=True)

        # Verify all required fields are present and correct
        assert result["changed"] is True
        assert result["failed"] is False
        assert result["rebooted"] is True
        assert result["commands"] == ["request system restart", "yes"]
        assert "Device reboot initiated successfully" in result["msg"]

        # Verify reboot command was sent
        # Check that send_command was called with command="request system restart"
        # (ignoring other arguments that might have been passed)
        assert any(
            call.kwargs.get("command") == "request system restart"
            for call in self.mock_connection.send_command.call_args_list
        ), "send_command was not called with command='request system restart'"
        assert any(
            call.kwargs.get("answer") == "yes"
            for call in self.mock_connection.send_command.call_args_list
        ), "send_command was not called with answer='yes'"

    def test_dnos_reboot_connection_error(self):
        """Test reboot with ConnectionError (expected during reboot)"""
        set_module_args(dict(reboot=True))

        # Mock connection methods - ConnectionError is expected during reboot
        self.mock_connection.send_command = MagicMock()

        # Simulate ConnectionError which is expected during reboot
        from ansible.module_utils.connection import ConnectionError

        self.mock_connection.send_command.side_effect = ConnectionError("Connection terminated")

        result = self.execute_module(changed=True)

        # Verify all required fields are present and correct for expected connection error
        assert result["changed"] is True
        assert result["failed"] is False
        assert result["rebooted"] is True
        assert result["commands"] == ["request system restart", "yes"]
        assert "Device reboot initiated successfully" in result["msg"]

    def test_dnos_reboot_command_failure(self):
        """Test reboot failure when command fails"""
        set_module_args(dict(reboot=True))

        # Mock connection methods - command fails
        self.mock_connection.send_command = MagicMock(side_effect=Exception("Command failed"))

        result = self.failed()

        # Verify all required fields are present and correct for failure
        assert result["failed"] is True
        assert result["changed"] is False
        assert result["rebooted"] is False
        assert result["commands"] == ["request system restart", "yes"]
        assert "Failed to execute reboot command" in result["msg"]

    def test_response_payload_structure(self):
        """Test that all response payloads have the correct structure"""
        # Test no action response structure
        set_module_args(dict(reboot=False))
        result = self.execute_module(changed=False)

        # Verify all required fields exist
        required_fields = ["changed", "failed", "rebooted", "commands", "msg"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(result["changed"], bool)
        assert isinstance(result["failed"], bool)
        assert isinstance(result["rebooted"], bool)
        assert isinstance(result["commands"], list)
        assert isinstance(result["msg"], str)
