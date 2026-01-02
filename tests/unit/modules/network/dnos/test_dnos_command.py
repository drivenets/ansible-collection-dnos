# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for DNOS command module."""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

import json
import os

from unittest.mock import patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

from ansible_collections.drivenets.dnos.plugins.modules import dnos_command

from ...fixtures import AnsibleModuleFixtures


def set_module_args(args):
    """Set module arguments for testing."""
    args_json = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args_json)


def _load_resource_file(filename):
    """Load a resource file from the resources directory."""
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    file_path = os.path.join(resources_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


class TestDNOSCommand:
    """Test cases for DNOS command module."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures."""
        self.fixtures = AnsibleModuleFixtures()

        # Set up common patches
        self.fixtures.setup_load_params()
        self.get_connection, self.mock_connection = self.fixtures.setup_get_connection(
            "ansible_collections.drivenets.dnos.plugins.modules.dnos_command"
        )

        yield

        # Clean up all patches
        self.fixtures.teardown()

    def test_dnos_command_simple(self):
        """Test simple command execution."""
        set_module_args(dict(commands=["show system version"]))

        # Mock the device response using actual system command output from resource file
        output = _load_resource_file("show_system.txt")
        self.mock_connection.get.return_value = output

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        assert len(result["stdout"]) == 1
        assert "System Name: TestRouter" in result["stdout"][0]
        assert "Version: DNOS [25.2.0]" in result["stdout"][0]
        assert len(result["stdout_lines"]) == 1
        # Count actual lines in the output (including empty lines in the output)
        expected_lines = len(output.split("\n"))
        assert len(result["stdout_lines"][0]) == expected_lines

    def test_dnos_command_multiple(self):
        """Test multiple command execution."""
        set_module_args(
            dict(commands=["show system version", "show system uptime", "show interfaces"])
        )

        # Mock the device responses using actual command output from resource files
        responses = [
            _load_resource_file("show_system_version.txt"),
            _load_resource_file("show_system_uptime.txt"),
            _load_resource_file("show_interfaces.txt"),
        ]
        self.mock_connection.get.side_effect = responses

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        assert len(result["stdout"]) == 3
        assert "DNOS [25.2.0]" in result["stdout"][0]
        assert "System Uptime: 7 days, 0:11:05" in result["stdout"][1]
        assert "ge100-0/0/1" in result["stdout"][2]

    def test_dnos_command_wait_for_success(self):
        """Test command with successful wait_for condition."""
        set_module_args(
            dict(
                commands=["show interfaces ge100-0/0/1"],
                wait_for=['result[0] contains "Admin-State: up"'],
                retries=3,
                interval=0,
            )
        )

        # Mock the device response
        self.mock_connection.reset_mock()
        self.mock_connection.get.return_value = (
            "Interface: ge100-0/0/1\nAdmin-State: up\nOper-State: up"
        )

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        assert "up" in result["stdout"][0]
        # Should only call once since condition is met
        assert self.mock_connection.get.call_count == 1

    def test_dnos_command_wait_for_failure(self):
        """Test command with failing wait_for condition."""
        set_module_args(
            dict(
                commands=["show interfaces ge100-0/0/1"],
                wait_for=['result[0] contains "Admin-State: down"'],
                retries=2,
                interval=0,
            )
        )

        # Mock the device response
        self.mock_connection.get.return_value = (
            "Interface: ge100-0/0/1\nAdmin-State: up\nOper-State: up"
        )

        with patch.object(basic.AnsibleModule, "fail_json") as fail_json:
            # Configure fail_json to raise SystemExit(1) like the real implementation
            fail_json.side_effect = SystemExit(1)

            # fail_json should raise SystemExit(1) which we should catch
            with pytest.raises(SystemExit) as exc_info:
                dnos_command.main()

            # Verify it was called and exited with code 1 (failure)
            assert exc_info.value.code == 1

        # Verify failure
        fail_json.assert_called_once()

    def test_dnos_command_wait_for_match_any(self):
        """Test command with match=any wait_for conditions."""
        set_module_args(
            dict(
                commands=["show interfaces ge100-0/0/1"],
                wait_for=[
                    'result[0] contains "Admin-State: down"',
                    'result[0] contains "Admin-State: up"',
                ],
                match="any",
                retries=3,
                interval=0,
            )
        )

        # Mock the device response
        self.mock_connection.get.return_value = (
            "Interface: ge100-0/0/1\nAdmin-State: up\nOper-State: up"
        )

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        # Should succeed because one condition matches
        assert self.mock_connection.get.call_count == 1

    def test_dnos_command_with_prompt(self):
        """Test command execution with prompt handling."""
        set_module_args(
            dict(
                commands=[
                    {
                        "command": "clear counters all",
                        "prompt": "Clear all counters? [y/N]:",
                        "answer": "y",
                    }
                ]
            )
        )

        # Mock the device response
        self.mock_connection.get.return_value = "All counters cleared"

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        assert "All counters cleared" in result["stdout"][0]

        # Verify the connection was called with prompt/answer
        self.mock_connection.get.assert_called_with(
            "clear counters all", prompt="Clear all counters? [y/N]:", answer="y", newline=True
        )

    def test_dnos_command_config_mode_rejected(self):
        """Test that config mode commands are rejected."""
        set_module_args(dict(commands=["configure"]))

        with patch.object(basic.AnsibleModule, "fail_json") as fail_json:
            # Configure fail_json to raise SystemExit(1) like the real implementation
            fail_json.side_effect = SystemExit(1)

            # Should raise SystemExit(1) when config command is rejected
            with pytest.raises(SystemExit) as exc_info:
                dnos_command.main()

            # Verify it exited with code 1 (failure)
            assert exc_info.value.code == 1

        # Verify failure
        fail_json.assert_called_once()
        result = fail_json.call_args[1]

        assert "does not support running config mode commands" in result["msg"]
        assert "use dnos_config instead" in result["msg"]

    def test_dnos_command_sendonly(self):
        """Test command with sendonly option."""
        set_module_args(dict(commands=[{"command": "exit", "sendonly": True}]))

        # Mock the device response
        self.mock_connection.send.return_value = None

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        assert result["stdout"] == [None]
        assert result["stdout_lines"] == [[]]

        # Verify send was called, not get
        self.mock_connection.send.assert_called_once()
        self.mock_connection.get.assert_not_called()

    def test_dnos_command_error_handling(self):
        """Test command error handling."""
        set_module_args(dict(commands=["show invalid command"]))

        # Mock an error response
        self.mock_connection.get.side_effect = Exception("Unknown command")

        with patch.object(basic.AnsibleModule, "fail_json") as fail_json:
            # Configure fail_json to raise SystemExit(1) like the real implementation
            fail_json.side_effect = SystemExit(1)

            # Should raise SystemExit(1) when command execution fails
            with pytest.raises(SystemExit) as exc_info:
                dnos_command.main()

            # Verify it exited with code 1 (failure)
            assert exc_info.value.code == 1

        # Verify failure
        fail_json.assert_called_once()
        result = fail_json.call_args[1]

        assert "Unknown command" in result["msg"]

    def test_dnos_command_complex_conditionals(self):
        """Test complex wait_for conditionals."""
        set_module_args(
            dict(
                commands=["show interfaces ge100-0/0/1", "show bgp neighbors"],
                wait_for=[
                    'result[0] contains "admin-state up"',
                    'result[0] contains "oper-state up"',
                    'result[1] contains "State: Established"',
                ],
                match="all",
                retries=3,
                interval=0,
            )
        )

        # Mock the device responses
        self.mock_connection.get.side_effect = [
            "Interface: ge100-0/0/1\nadmin-state up\noper-state up",
            "Neighbor: 10.0.0.1\nState: Established",
        ]

        with patch.object(basic.AnsibleModule, "exit_json") as exit_json:
            dnos_command.main()

        # Verify results
        exit_json.assert_called_once()
        result = exit_json.call_args[1]

        assert result["changed"] is False
        assert len(result["stdout"]) == 2
        assert "admin-state up" in result["stdout"][0]
        assert "State: Established" in result["stdout"][1]
