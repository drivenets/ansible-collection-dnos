# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for DNOS terminal plugin."""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from unittest.mock import Mock, call

import pytest

from ansible.errors import AnsibleConnectionFailure

from ansible_collections.drivenets.dnos.plugins.terminal import dnos


class TestDNOSTerminal:
    """Test cases for DNOS terminal plugin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.terminal = dnos.TerminalModule(self.mock_connection)

    def test_terminal_stdout_patterns(self):
        """Test that all prompt patterns are correctly defined."""
        patterns = self.terminal.terminal_stdout_re

        # Test privileged mode prompt
        assert any(p.match(b"\ndnRouter#") for p in patterns)
        assert any(p.match(b"dnRouter#") for p in patterns)

        # Test configuration mode prompts
        assert any(p.match(b"\ndnRouter(cfg)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-system)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-if)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-if-ge100-0/0/1)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-aaa-tacacs-server)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-protocol)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-routing)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-protocol-bgp)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-routing-isis)#") for p in patterns)
        assert any(p.match(b"dnRouter(cfg-system-snmp-community)#") for p in patterns)
        assert any(p.match(b"cdnos2(28-Aug-2025-13:12:48)# ") for p in patterns)
        assert not any(
            p.match(
                b"cdnos2(cfg-system-snmp-community 28-Aug-2025-13:16:18)#       client-list 24.40.64.0/20"
            )
            for p in patterns
        )

    def test_terminal_stderr_patterns(self):
        """Test that all error patterns are correctly defined."""
        patterns = self.terminal.terminal_stderr_re

        # Test error patterns
        test_errors = [
            b"Unknown command",
            b"Syntax error",
            b"Incomplete command",
            b"Invalid input detected",
            b"Access denied",
            b"% Error",
            b"% Bad secret",
            b"% This command is not authorized",
            b"% Ambiguous command",
            b"% Invalid parameter",
            b"% Configuration failed",
            b"% Commit failed",
            b"% Rollback failed",
        ]

        for error in test_errors:
            assert any(p.search(error) for p in patterns), f"Pattern not found for: {error}"

    def test_on_open_shell_success(self):
        """Test successful terminal initialization."""
        self.terminal._exec_cli_command = Mock(return_value=b"")

        self.terminal.on_open_shell()

        # Verify terminal settings commands were sent
        calls = self.terminal._exec_cli_command.call_args_list
        assert call(b"set cli-terminal-length 0") in calls
        assert call(b"\n") in calls

        # Verify terminal is marked as initialized
        assert self.terminal._terminal_initialized is True

    def test_on_open_shell_width_not_supported(self):
        """Test terminal initialization when width setting is not supported."""

        def mock_exec(cmd):
            if b"width" in cmd:
                raise AnsibleConnectionFailure("Command not supported")
            return b""

        self.terminal._exec_cli_command = Mock(side_effect=mock_exec)

        # Should not raise exception
        self.terminal.on_open_shell()

        # Verify terminal is still initialized
        assert self.terminal._terminal_initialized is True

    def test_on_open_shell_failure(self):
        """Test terminal initialization failure."""
        self.terminal._exec_cli_command = Mock(
            side_effect=AnsibleConnectionFailure("Connection failed")
        )

        with pytest.raises(AnsibleConnectionFailure) as exc_info:
            self.terminal.on_open_shell()

        assert "Failed to initialize DNOS terminal" in str(exc_info.value)

    def test_on_open_shell_unexpected_error(self):
        """Test terminal initialization with unexpected error."""
        self.terminal._exec_cli_command = Mock(side_effect=Exception("Unexpected error"))

        with pytest.raises(AnsibleConnectionFailure) as exc_info:
            self.terminal.on_open_shell()

        assert "Unexpected error during terminal initialization" in str(exc_info.value)

    def test_on_become_no_password_required(self):
        """Test privilege escalation when no password is required."""
        self.terminal._exec_cli_command = Mock(return_value=b"\ndnRouter#")

        self.terminal.on_become()

        self.terminal._exec_cli_command.assert_called_with(b"enable")

    def test_on_become_with_password(self):
        """Test privilege escalation with password."""
        responses = [b"Password: ", b"\ndnRouter#"]
        self.terminal._exec_cli_command = Mock(side_effect=responses)

        self.terminal.on_become(passwd="secret123")

        calls = self.terminal._exec_cli_command.call_args_list
        assert call(b"enable") in calls
        assert call(b"secret123") in calls

    def test_on_become_password_required_but_not_provided(self):
        """Test privilege escalation failure when password required but not provided."""
        self.terminal._exec_cli_command = Mock(return_value=b"Password: ")

        with pytest.raises(AnsibleConnectionFailure) as exc_info:
            self.terminal.on_become()

        assert "Privilege escalation requires password" in str(exc_info.value)

    def test_on_become_failure(self):
        """Test privilege escalation failure."""
        self.terminal._exec_cli_command = Mock(side_effect=Exception("Enable failed"))

        with pytest.raises(AnsibleConnectionFailure) as exc_info:
            self.terminal.on_become()

        assert "Failed to escalate privileges" in str(exc_info.value)

    def test_on_unbecome(self):
        """Test exiting privileged mode."""
        self.terminal._exec_cli_command = Mock(return_value=b"")

        self.terminal.on_unbecome()

        self.terminal._exec_cli_command.assert_called_with(b"disable")

    def test_on_unbecome_failure(self):
        """Test failure when exiting privileged mode."""
        self.terminal._exec_cli_command = Mock(side_effect=Exception("Disable failed"))

        with pytest.raises(AnsibleConnectionFailure) as exc_info:
            self.terminal.on_unbecome()

        assert "Failed to exit privileged mode" in str(exc_info.value)

    def test_on_close_shell(self):
        """Test terminal cleanup on shell close."""
        self.terminal._exec_cli_command = Mock(
            side_effect=[b"", b"", AnsibleConnectionFailure("Already at top")]
        )

        # Should not raise exception
        self.terminal.on_close_shell()

        # Verify exit commands were sent
        assert self.terminal._exec_cli_command.call_count >= 3

    def test_on_close_shell_with_exception(self):
        """Test terminal cleanup handles exceptions gracefully."""
        self.terminal._exec_cli_command = Mock(side_effect=Exception("Cleanup error"))

        # Should not raise exception
        self.terminal.on_close_shell()

    def test_on_authorize(self):
        """Test that on_authorize calls on_become."""
        self.terminal.on_become = Mock()

        self.terminal.on_authorize(passwd="test123")

        self.terminal.on_become.assert_called_once_with("test123")

    def test_on_deauthorize(self):
        """Test that on_deauthorize calls on_unbecome."""
        self.terminal.on_unbecome = Mock()

        self.terminal.on_deauthorize()

        self.terminal.on_unbecome.assert_called_once()

    def test_prompt_patterns_comprehensive(self):
        """Test comprehensive prompt pattern matching."""
        patterns = self.terminal.terminal_stdout_re

        # Test various hostname formats
        test_prompts = [
            b"router1#",
            b"dnos-device#",
            b"10.0.0.1#",
            b"device_name#",
            b"device-name#",
            b"device.name#",
            b"device:name#",
            b"device/name#",
            b"device[name]#",
            b"device+name#",
            # Configuration contexts
            b"router(cfg)#",
            b"router(cfg-if-bundle-1)#",
            b"router(cfg-protocol-isis)#",
            b"router(cfg-routing-bgp)#",
            b"router(cfg-system-aaa)#",
        ]

        for prompt in test_prompts:
            assert any(p.search(prompt) for p in patterns), f"No pattern matches: {prompt}"

    def test_error_patterns_case_insensitive(self):
        """Test that error patterns are case insensitive."""
        patterns = self.terminal.terminal_stderr_re

        # Test case variations
        test_errors = [
            (b"UNKNOWN COMMAND", b"unknown command"),
            (b"syntax ERROR", b"SYNTAX error"),
            (b"InCoMpLeTe CoMmAnD", b"incomplete command"),
        ]

        for upper, lower in test_errors:
            assert any(p.search(upper) for p in patterns), f"Pattern not found for: {upper}"
            assert any(p.search(lower) for p in patterns), f"Pattern not found for: {lower}"
