# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for DNOS cliconf edit_config workflow."""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

import pytest

from ansible.errors import AnsibleConnectionFailure


class FakeConnection:
    def __init__(self):
        self.connected = True

    def get_prompt(self):
        # Return a non-config prompt to avoid unintended discard in edit_config
        return b"dn>"


def _setup_cliconf_with_spy(monkeypatch, *, diff_present=True, fail_on_commit=False):
    """Create a Cliconf instance with spies on transport and config state.

    Args:
        diff_present: Whether 'show config compare' should indicate diffs.
        fail_on_commit: Whether wrapper commit() should raise failure.
    """
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    state = {"in_cfg": False}
    calls = {"commands": [], "wrapper_commit_calls": 0, "discard_calls": 0}

    def fake_in_config_mode(self):
        return state["in_cfg"]

    def fake_send_command(
        self,
        command=None,
        prompt=None,
        answer=None,
        sendonly=False,
        newline=True,
        check_all=False,
        **kwargs,
    ):
        # Record every command
        calls["commands"].append(command)
        # Simulate config mode transitions
        if command == "configure":
            state["in_cfg"] = True
            return ""
        if command == "exit":
            state["in_cfg"] = False
            return ""
        return ""

    def fake_get(self, command=None, **kwargs):
        # Only 'show config compare' is used by edit_config
        if command == "show config compare":
            # Return a non-empty string if diffs present, else empty
            return "diff" if diff_present else ""
        return ""

    def fake_commit(self, comment=None, confirm=None, ignore_empty_commit=True):
        calls["wrapper_commit_calls"] += 1
        if fail_on_commit:
            raise AnsibleConnectionFailure("simulated commit failure")
        # Mirror real behavior by sending a commit command
        calls["commands"].append("commit" if comment is None else f"commit {comment}")
        return ""

    def fake_discard_changes(self):
        calls["discard_calls"] += 1
        calls["commands"].append("rollback")
        return ""

    # Patch helpers and transport interactions
    def fake_connection_get_prompt():
        # Return config-mode-like prompt when in_cfg is True, else operational
        return b"dn(cfg)#" if state["in_cfg"] else b"dn>"

    monkeypatch.setattr(cliconf._connection, "get_prompt", fake_connection_get_prompt, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)
    monkeypatch.setattr(type(cliconf), "get", fake_get, raising=True)
    monkeypatch.setattr(type(cliconf), "commit", fake_commit, raising=True)
    monkeypatch.setattr(type(cliconf), "discard_changes", fake_discard_changes, raising=True)

    return cliconf, calls


def test_edit_config_calls_single_commit_when_diff_present(monkeypatch):
    """Normal edit_config should commit exactly once when diff is present."""
    cliconf, calls = _setup_cliconf_with_spy(monkeypatch, diff_present=True)

    # DNOS capabilities do not support commit comments; omit comment
    cliconf.edit_config(candidate=["system name TestRouter"], commit=True)

    # 'configure' called exactly once and 'exit' once
    assert calls["commands"].count("configure") == 1
    assert calls["commands"].count("exit") == 1
    # Wrapper commit called once
    assert (
        calls["wrapper_commit_calls"] == 1
    ), f"Wrapper commit calls: {calls['wrapper_commit_calls']}"
    # Candidate command was sent
    assert "system name TestRouter" in calls["commands"]


def test_edit_config_commit_error_triggers_rollback_and_configure_once(monkeypatch):
    """On commit error, edit_config should rollback; 'configure' called once."""
    cliconf, calls = _setup_cliconf_with_spy(monkeypatch, diff_present=True, fail_on_commit=True)

    with pytest.raises(AnsibleConnectionFailure):
        cliconf.edit_config(candidate=["interfaces lo0"], commit=True)

    # Verify 'configure' called exactly once
    assert calls["commands"].count("configure") == 1
    # Verify rollback executed due to commit failure
    assert "rollback" in calls["commands"], f"Calls: {calls['commands']}"


def test_edit_config_candidate_commit_with_commit_false_calls_single_commit(monkeypatch):
    """When candidate has 'commit' and commit=False, wrapper must not add another commit."""
    # No diff should be present after explicit commit
    cliconf, calls = _setup_cliconf_with_spy(monkeypatch, diff_present=False)

    cliconf.edit_config(candidate=["commit"], commit=False)

    # 'configure' called exactly once
    assert calls["commands"].count("configure") == 1
    # Wrapper commit must not be called
    assert calls["wrapper_commit_calls"] == 0
    # Exactly one commit command recorded (the explicit candidate one)
    actual_commits = [c for c in calls["commands"] if c.startswith("commit")]
    assert (
        len(actual_commits) == 1
    ), f"Unexpected commits: {actual_commits}, All calls: {calls['commands']}"


def test_edit_config_candidate_rollback_then_commit_with_commit_false_single_commit(monkeypatch):
    """When candidate has 'rollback' then 'commit' and commit=False, no duplicate commit occurs."""
    # After rollback+commit, no diffs should remain
    cliconf, calls = _setup_cliconf_with_spy(monkeypatch, diff_present=False)

    cliconf.edit_config(
        candidate=["rollback", 'commit log "Ansible rollback operation"'], commit=False
    )

    # 'configure' called exactly once
    assert calls["commands"].count("configure") == 1
    # Ensure rollback was sent
    assert any(c == "rollback" for c in calls["commands"]), f"Calls: {calls['commands']}"
    # Wrapper commit must not be called
    assert calls["wrapper_commit_calls"] == 0
    # Exactly one commit recorded (the explicit candidate commit)
    actual_commits = [c for c in calls["commands"] if c.startswith("commit")]
    assert (
        len(actual_commits) == 1
    ), f"Unexpected commits: {actual_commits}, All calls: {calls['commands']}"


def test_commit_succeeded_in_config_mode(monkeypatch):
    """commit() should pass when device returns 'Commit succeeded'."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent = {"commands": []}

    def fake_is_config_mode(self):
        return True

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return "Commit succeeded by dnroot at 11-Sep-2025 17:33:29 UTC"

    monkeypatch.setattr(type(cliconf), "_is_config_mode", fake_is_config_mode, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    # Should not raise
    cliconf.commit()
    assert sent["commands"] and sent["commands"][-1] == "commit"


def test_commit_confirm_in_config_mode(monkeypatch):
    """commit(confirm=True) should pass when device returns 'Commit confirm'."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent = {"commands": []}

    def fake_is_config_mode(self):
        return True

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return """Commit succeeded by dnroot at 11-Sep-2025 17:34:35 UTC
Commit confirm will be automatically rolled back in 1 minutes unless confirmed"""

    monkeypatch.setattr(type(cliconf), "_is_config_mode", fake_is_config_mode, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    # Should not raise
    cliconf.commit(confirm=123)
    assert sent["commands"] and sent["commands"][-1] == "commit confirm 123"

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return "NOTICE: commit action is not applicable. no configuration changes were made"

    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    with pytest.raises(AnsibleConnectionFailure):
        cliconf.commit(confirm=123, ignore_empty_commit=False)
    assert sent["commands"] and sent["commands"][-1] == "commit confirm 123"


def test_commit_confirm_pending_commit_in_config_mode(monkeypatch):
    """commit(confirm=True) should pass when device returns 'Commit confirm'."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent = {"commands": []}

    def fake_is_config_mode(self):
        return True

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return "Commit confirmed"

    monkeypatch.setattr(type(cliconf), "_is_config_mode", fake_is_config_mode, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    # Should not raise
    cliconf.commit()
    assert sent["commands"] and sent["commands"][-1] == "commit"


def test_commit_empty_commit_ignored_by_default(monkeypatch):
    """Empty commit notice should be ignored by default (no exception)."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent = {"commands": []}

    def fake_is_config_mode(self):
        return True

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return "NOTICE: commit action is not applicable. no configuration changes were made"

    monkeypatch.setattr(type(cliconf), "_is_config_mode", fake_is_config_mode, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    # Default ignore_empty_commit=True, so no exception expected
    cliconf.commit()
    assert sent["commands"] and sent["commands"][-1] == "commit"

    with pytest.raises(AnsibleConnectionFailure):
        cliconf.commit(ignore_empty_commit=False)
    assert sent["commands"] and sent["commands"][-1] == "commit"


def test_cancel_pending_commit_in_config_mode(monkeypatch):
    """cancel_pending_commit() should pass when device returns 'Commit confirmed'."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent = {"commands": []}

    call_counts = {"n": 0}

    def fake_is_config_mode(self):
        """
        config mode should be set to True at the beginning, after entering the config mode context manager
        but it will be exited successfully only after config mode is False"""
        call_counts["n"] += 1
        return call_counts["n"] <= 5

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return "Configuration commit confirm rollbacked by dnroot at 11-Sep-2025 18:19:15 UTC"

    monkeypatch.setattr(type(cliconf), "_is_config_mode", fake_is_config_mode, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    cliconf.cancel_pending_commit()
    assert "clear system commit" in sent["commands"]

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent["commands"].append(command)
        return "ERROR: No commit confirm scheduled."

    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    with pytest.raises(AnsibleConnectionFailure):
        cliconf.cancel_pending_commit()
    assert "clear system commit" in sent["commands"]


def test_edit_config_does_not_send_configure_when_already_in_config_mode(monkeypatch):
    """edit_config() should NOT send 'configure' command when already in config mode."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent_commands = []

    def fake_get_prompt():
        # Return config mode prompt
        return b"dn(cfg)#"

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent_commands.append(command)
        return ""

    def fake_get(self, command=None, **kwargs):
        if command == "show config compare":
            return "diff"
        return ""

    def fake_commit(self, comment=None, confirm=None, ignore_empty_commit=True):
        return {"changed": True}

    monkeypatch.setattr(cliconf._connection, "get_prompt", fake_get_prompt, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)
    monkeypatch.setattr(type(cliconf), "get", fake_get, raising=True)
    monkeypatch.setattr(type(cliconf), "commit", fake_commit, raising=True)

    cliconf.edit_config(candidate=["system name TestRouter"], commit=True)

    # Verify 'configure' was NOT sent since we were already in config mode
    assert (
        "configure" not in sent_commands
    ), f"'configure' should not be sent when already in config mode. Commands sent: {sent_commands}"
    # Verify the candidate command was sent
    assert "system name TestRouter" in sent_commands
    # Verify 'exit' was sent after commit
    assert "exit" in sent_commands


def test_edit_config_sends_configure_when_not_in_config_mode(monkeypatch):
    """edit_config() should send 'configure' command when NOT in config mode."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent_commands = []
    config_mode_state = False

    def fake_get_prompt():
        # Return operational prompt initially, config mode after 'configure' is sent
        return b"dn(cfg)#" if config_mode_state else b"dn>"

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent_commands.append(command)
            # Simulate entering config mode when 'configure' is sent
            if command == "configure":
                nonlocal config_mode_state
                config_mode_state = True
            elif command == "exit":
                config_mode_state = False
        return ""

    def fake_get(self, command=None, **kwargs):
        if command == "show config compare":
            return "diff"
        return ""

    def fake_commit(self, comment=None, confirm=None, ignore_empty_commit=True):
        return {"changed": True}

    monkeypatch.setattr(cliconf._connection, "get_prompt", fake_get_prompt, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)
    monkeypatch.setattr(type(cliconf), "get", fake_get, raising=True)
    monkeypatch.setattr(type(cliconf), "commit", fake_commit, raising=True)

    cliconf.edit_config(candidate=["system name TestRouter"], commit=True)

    # Verify 'configure' WAS sent since we were not in config mode
    assert (
        "configure" in sent_commands
    ), f"'configure' should be sent when not in config mode. Commands sent: {sent_commands}"
    # Verify the candidate command was sent
    assert "system name TestRouter" in sent_commands
    # Verify 'exit' was sent after commit
    assert "exit" in sent_commands


def test_config_mode_context_manager_does_not_send_configure_when_already_in_config_mode(
    monkeypatch,
):
    """config_mode() context manager should NOT send 'configure' when already in config mode."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent_commands = []
    config_mode_state = True  # Start in config mode

    def fake_get_prompt():
        # Return config mode prompt initially, operational after 'exit' is sent
        return b"dn(cfg)#" if config_mode_state else b"dn>"

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent_commands.append(command)
            # Simulate exiting config mode when 'exit' is sent
            if command == "exit":
                nonlocal config_mode_state
                config_mode_state = False
        return ""

    monkeypatch.setattr(cliconf._connection, "get_prompt", fake_get_prompt, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    with cliconf.config_mode():
        pass

    # Verify 'configure' was NOT sent since we were already in config mode
    assert (
        "configure" not in sent_commands
    ), f"'configure' should not be sent when already in config mode. Commands sent: {sent_commands}"
    # Verify 'exit' was sent to exit config mode
    assert "exit" in sent_commands


def test_config_mode_context_manager_sends_configure_when_not_in_config_mode(monkeypatch):
    """config_mode() context manager should send 'configure' when NOT in config mode."""
    from ansible_collections.drivenets.dnos.plugins.cliconf.dnos import Cliconf

    conn = FakeConnection()
    cliconf = Cliconf(conn)

    sent_commands = []
    config_mode_state = False

    def fake_get_prompt():
        # Return operational prompt initially, config mode after 'configure' is sent
        return b"dn(cfg)#" if config_mode_state else b"dn>"

    def fake_send_command(self, command=None, **kwargs):
        if command is not None:
            sent_commands.append(command)
            # Simulate entering config mode when 'configure' is sent
            if command == "configure":
                nonlocal config_mode_state
                config_mode_state = True
            elif command == "exit":
                config_mode_state = False
        return ""

    monkeypatch.setattr(cliconf._connection, "get_prompt", fake_get_prompt, raising=True)
    monkeypatch.setattr(type(cliconf), "send_command", fake_send_command, raising=True)

    with cliconf.config_mode():
        pass

    # Verify 'configure' WAS sent since we were not in config mode
    assert (
        "configure" in sent_commands
    ), f"'configure' should be sent when not in config mode. Commands sent: {sent_commands}"
    # Verify 'exit' was sent to exit config mode
    assert "exit" in sent_commands
