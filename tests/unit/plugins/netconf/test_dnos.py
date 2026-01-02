# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets Inc.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for DNOS NETCONF plugin functionality."""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

import json
import os

from unittest.mock import MagicMock, Mock, patch

import pytest


try:
    from ncclient.operations import RPCError

    HAS_NCCLIENT = True
except ImportError:
    HAS_NCCLIENT = False


def _load_resource_file(filename):
    """Load a resource file from the resources directory."""
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    file_path = os.path.join(resources_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


class FakeManager:
    """Mock ncclient manager for testing."""

    def __init__(self):
        self.server_capabilities = [
            "urn:ietf:params:netconf:base:1.0",
            "urn:ietf:params:netconf:base:1.1",
            "urn:ietf:params:netconf:capability:candidate:1.0",
            "urn:ietf:params:netconf:capability:confirmed-commit:1.0",
            "urn:ietf:params:netconf:capability:validate:1.0",
            "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
        ]
        self.client_capabilities = [
            "urn:ietf:params:netconf:base:1.0",
            "urn:ietf:params:netconf:base:1.1",
        ]
        self.session_id = 12345

        # Create mock methods that can be asserted
        self._create_mock_methods()

    def _create_mock_methods(self):
        """Create mock methods that return proper responses based on actual device responses."""

        def _get_config_side_effect(source=None, filter=None):
            mock_resp = Mock()
            # Load get-config response from resource file
            mock_resp.xml = _load_resource_file("get_config_response.xml")
            return mock_resp

        def _get_side_effect(filter=None, with_defaults=None):
            mock_resp = Mock()
            # Load get() response from resource file
            if with_defaults == "report-all":
                # Empty data response for with-defaults=report-all
                mock_resp.xml = _load_resource_file("get_with_defaults_response.xml")
            else:
                # Response with state and config data
                mock_resp.xml = _load_resource_file("get_response.xml")
            return mock_resp

        def _edit_config_side_effect(**kwargs):
            mock_resp = Mock()
            # Load edit-config response from resource file
            mock_resp.xml = _load_resource_file("edit_config_response.xml")
            return mock_resp

        def _commit_side_effect(confirmed=False, timeout=None, persist=None):
            mock_resp = Mock()
            # Negative flow: commit error response (empty commit)
            # User requested only negative flow responses for commit
            mock_resp.xml = _load_resource_file("commit_error_response.xml")
            mock_resp.data_xml = None
            return mock_resp

        def _reboot_side_effect():
            mock_resp = Mock()
            # Load reboot response from resource file
            mock_resp.data_xml = _load_resource_file("reboot_response.xml")
            return mock_resp

        self.get_config = MagicMock(side_effect=_get_config_side_effect)
        self.get = MagicMock(side_effect=_get_side_effect)
        self.edit_config = MagicMock(side_effect=_edit_config_side_effect)
        self.commit = MagicMock(side_effect=_commit_side_effect)
        self.reboot = MagicMock(side_effect=_reboot_side_effect)

    def dispatch(self, rpc_element):
        """Mock dispatch for RPC operations."""
        mock_resp = Mock()
        # Load show-system response from resource file
        mock_resp.xml = _load_resource_file("show_system_response.xml")
        return mock_resp


def _setup_netconf_with_mock(monkeypatch, manager=None):
    """Create a Netconf instance with mocked manager.

    Args:
        manager: Optional FakeManager instance. If None, creates a new one.
    """
    from ansible_collections.drivenets.dnos.plugins.netconf.dnos import Netconf

    if manager is None:
        manager = FakeManager()

    # Create a mock connection object
    mock_connection = Mock()

    # Create Netconf instance
    netconf = Netconf(mock_connection)

    # Replace the 'm' property with a new property that returns our manager
    # We do this by replacing the property descriptor on the class
    # This creates a new property that always returns our manager
    def get_m(self):
        return manager

    # Replace the property on the class using monkeypatch
    # This affects all instances, but since we're in tests, that's okay
    monkeypatch.setattr(type(netconf), "m", property(get_m), raising=False)

    return netconf, manager


def test_get_capabilities_returns_proper_structure(monkeypatch):
    """Test that get_capabilities returns expected structure with all required keys."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Mock get_base_rpc to return standard RPCs
    def fake_get_base_rpc(self):
        return ["get", "get-config", "edit-config"]

    monkeypatch.setattr(type(netconf), "get_base_rpc", fake_get_base_rpc, raising=True)

    capabilities_json = netconf.get_capabilities()
    capabilities = json.loads(capabilities_json)

    assert "rpc" in capabilities
    assert "network_api" in capabilities
    assert "device_info" in capabilities
    assert "server_capabilities" in capabilities
    assert "client_capabilities" in capabilities
    assert "session_id" in capabilities
    assert "device_operations" in capabilities

    assert capabilities["network_api"] == "netconf"
    assert capabilities["session_id"] == 12345
    assert "commit" in capabilities["rpc"]
    assert "discard-changes" in capabilities["rpc"]
    assert "validate" in capabilities["rpc"]
    assert "rollback" in capabilities["rpc"]


def test_get_device_info_parses_show_system_response(monkeypatch):
    """Test that get_device_info correctly parses show-system RPC response."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    device_info = netconf.get_device_info()

    assert device_info["network_os"] == "dnos"
    assert device_info["network_os_hostname"] == "cdnos1"
    assert device_info["network_os_version"] == "25.4.0"
    assert device_info["network_os_model"] == "SA-VR"


def test_get_device_info_handles_rpc_failure(monkeypatch):
    """Test that get_device_info handles RPC failures gracefully."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Make dispatch raise an exception
    def failing_dispatch(self, rpc_element):
        raise Exception("RPC failed")

    monkeypatch.setattr(manager, "dispatch", failing_dispatch, raising=True)

    device_info = netconf.get_device_info()

    assert device_info["network_os"] == "dnos"
    assert device_info["network_os_version"] == "unknown"
    assert device_info["network_os_hostname"] == "unknown"
    assert device_info["network_os_model"] == "unknown"


def test_get_device_info_handles_missing_result_element(monkeypatch):
    """Test that get_device_info handles missing result element."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    def empty_dispatch(self, rpc_element):
        mock_resp = Mock()
        mock_resp.xml = '<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"></rpc-reply>'
        return mock_resp

    monkeypatch.setattr(manager, "dispatch", empty_dispatch, raising=True)

    device_info = netconf.get_device_info()

    assert device_info["network_os"] == "dnos"
    assert device_info["network_os_version"] == "unknown"
    assert device_info["network_os_hostname"] == "unknown"
    assert device_info["network_os_model"] == "unknown"


def test_get_config_with_default_source(monkeypatch):
    """Test get_config uses 'running' as default source."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    result = netconf.get_config()

    assert result is not None
    assert "<rpc-reply" in result
    assert manager.get_config.called


def test_get_config_with_specified_source(monkeypatch):
    """Test get_config with specified source datastore."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    result = netconf.get_config(source="candidate")

    assert result is not None
    manager.get_config.assert_called_with(source="candidate", filter=None)


def test_get_config_with_subtree_filter(monkeypatch):
    """Test get_config with subtree filter."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    filter_xml = '<interfaces xmlns="http://drivenets.com/ns/yang/dn-interfaces"/>'
    result = netconf.get_config(source="running", filter=("subtree", filter_xml))

    assert result is not None
    manager.get_config.assert_called_with(source="running", filter=("subtree", filter_xml))


def test_get_config_converts_list_filter_to_tuple(monkeypatch):
    """Test get_config converts list filter to tuple."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    filter_list = ["subtree", "<interfaces/>"]
    result = netconf.get_config(source="running", filter=filter_list)

    assert result is not None
    # Verify filter was converted to tuple
    call_args = manager.get_config.call_args
    assert isinstance(call_args[1]["filter"], tuple)


def test_get_with_filter(monkeypatch):
    """Test get operation with filter."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    filter_xml = '<interfaces xmlns="http://drivenets.com/ns/yang/dn-interfaces"/>'
    result = netconf.get(filter=("subtree", filter_xml))

    assert result is not None
    assert "<rpc-reply" in result
    manager.get.assert_called_with(filter=("subtree", filter_xml), with_defaults=None)


def test_get_with_defaults(monkeypatch):
    """Test get operation with with_defaults parameter."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    result = netconf.get(with_defaults="report-all")

    assert result is not None
    manager.get.assert_called_with(filter=None, with_defaults="report-all")


def test_get_converts_list_filter_to_tuple(monkeypatch):
    """Test get converts list filter to tuple."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    filter_list = ["subtree", "<interfaces/>"]
    result = netconf.get(filter=filter_list)

    assert result is not None
    call_args = manager.get.call_args
    assert isinstance(call_args[1]["filter"], tuple)


def test_get_device_operations_returns_expected_operations(monkeypatch):
    """Test get_device_operations returns correct DNOS operation flags."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    operations = netconf.get_device_operations(manager.server_capabilities)

    assert operations["supports_commit"] is True
    assert operations["supports_rollback"] is True
    assert operations["supports_defaults"] is True
    assert operations["supports_commit_label"] is False
    assert operations["supports_commit_confirmed"] is True
    assert operations["supports_confirm_commit"] is True
    assert operations["supports_startup"] is False
    assert operations["supports_xpath"] is True
    assert operations["supports_writable_running"] is False
    assert operations["supports_validate"] is True
    assert operations["supports_lock"] is False
    assert operations["supports_unlock"] is False
    assert operations["supports_candidate"] is True
    assert operations["supports_commit_comment"] is False
    assert operations["supports_discard_changes"] is True
    assert operations["supports_yang"] is True
    assert operations["supports_yang_library"] is True


def test_edit_config_requires_config_parameter(monkeypatch):
    """Test edit_config raises ValueError when config is None."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    with pytest.raises(ValueError, match="config must be provided"):
        netconf.edit_config(config=None)


def test_edit_config_with_xml_format(monkeypatch):
    """Test edit_config with XML format (default)."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_xml = "<config><interfaces/></config>"
    result = netconf.edit_config(config=config_xml)

    assert result is not None
    assert "<rpc-reply" in result
    manager.edit_config.assert_called_with(
        target="candidate",
        config=config_xml,
    )


def test_edit_config_with_custom_target(monkeypatch):
    """Test edit_config with custom target datastore."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_xml = "<config><interfaces/></config>"
    result = netconf.edit_config(config=config_xml, target="running")

    assert result is not None
    manager.edit_config.assert_called_with(
        target="running",
        config=config_xml,
    )


def test_edit_config_with_default_operation(monkeypatch):
    """Test edit_config with default_operation parameter."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_xml = "<config><interfaces/></config>"
    result = netconf.edit_config(
        config=config_xml,
        default_operation="merge",
    )

    assert result is not None
    manager.edit_config.assert_called_with(
        target="candidate",
        config=config_xml,
        default_operation="merge",
    )


def test_edit_config_with_test_option(monkeypatch):
    """Test edit_config with test_option parameter."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_xml = "<config><interfaces/></config>"
    result = netconf.edit_config(
        config=config_xml,
        test_option="test-then-set",
    )

    assert result is not None
    manager.edit_config.assert_called_with(
        target="candidate",
        config=config_xml,
        test_option="test-then-set",
    )


def test_edit_config_with_rollback_on_error(monkeypatch):
    """Test edit_config with rollback-on-error error_option."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_xml = "<config><interfaces/></config>"
    result = netconf.edit_config(
        config=config_xml,
        error_option="rollback-on-error",
    )

    assert result is not None
    manager.edit_config.assert_called_with(
        target="candidate",
        config=config_xml,
        error_option="rollback-on-error",
    )


def test_edit_config_ignores_unsupported_error_option(monkeypatch):
    """Test edit_config ignores unsupported error_option values."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_xml = "<config><interfaces/></config>"
    result = netconf.edit_config(
        config=config_xml,
        error_option="stop-on-error",  # Not supported by DNOS
    )

    assert result is not None
    # Should not include error_option in kwargs
    call_kwargs = manager.edit_config.call_args[1]
    assert "error_option" not in call_kwargs


def test_edit_config_converts_non_xml_format(monkeypatch):
    """Test edit_config converts non-XML format to XML."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    config_dict = {"interfaces": {}}

    with patch("ansible_collections.drivenets.dnos.plugins.netconf.dnos.to_xml") as mock_to_xml:
        mock_to_xml.return_value = "<config><interfaces/></config>"
        result = netconf.edit_config(config=config_dict, format="json")

        assert result is not None
        mock_to_xml.assert_called_once_with(config_dict)


def test_edit_config_success(monkeypatch):
    """Test edit_config returns successful response."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Override edit_config to return success response
    def _edit_config_success_side_effect(**kwargs):
        mock_resp = Mock()
        mock_resp.xml = _load_resource_file("success_response.xml")
        return mock_resp

    manager.edit_config = MagicMock(side_effect=_edit_config_success_side_effect)

    # Load config from resource file
    config_xml = _load_resource_file("edit_config_request.xml")

    result = netconf.edit_config(config=config_xml)

    assert result is not None
    assert "<rpc-reply" in result
    assert "<ok/>" in result
    manager.edit_config.assert_called_once_with(
        target="candidate",
        config=config_xml,
    )


def test_commit_success(monkeypatch):
    """Test commit operation returns successful response."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Override commit to return success response
    def _commit_success_side_effect(confirmed=False, timeout=None, persist=None):
        mock_resp = Mock()
        mock_resp.data_xml = _load_resource_file("success_response.xml")
        return mock_resp

    manager.commit = MagicMock(side_effect=_commit_success_side_effect)

    result = netconf.commit()

    assert result is not None
    assert "<rpc-reply" in result
    assert "<ok/>" in result
    manager.commit.assert_called_with(
        confirmed=False,
        timeout="None",
        persist=None,
    )


def test_commit_with_confirmed_flag(monkeypatch):
    """Test commit with confirmed flag returns successful response."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Override commit to return success response
    def _commit_confirmed_success_side_effect(confirmed=False, timeout=None, persist=None):
        mock_resp = Mock()
        mock_resp.data_xml = _load_resource_file("success_response.xml")
        return mock_resp

    manager.commit = MagicMock(side_effect=_commit_confirmed_success_side_effect)

    result = netconf.commit(confirmed=True)

    assert result is not None
    assert "<rpc-reply" in result
    assert "<ok/>" in result
    manager.commit.assert_called_with(
        confirmed=True,
        timeout="None",
        persist=None,
    )


def test_commit_with_timeout(monkeypatch):
    """Test commit with timeout returns successful response."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Override commit to return success response
    def _commit_timeout_success_side_effect(confirmed=False, timeout=None, persist=None):
        mock_resp = Mock()
        mock_resp.data_xml = _load_resource_file("success_response.xml")
        return mock_resp

    manager.commit = MagicMock(side_effect=_commit_timeout_success_side_effect)

    result = netconf.commit(confirmed=True, timeout=120)

    assert result is not None
    assert "<rpc-reply" in result
    assert "<ok/>" in result
    manager.commit.assert_called_with(
        confirmed=True,
        timeout="120",
        persist=None,
    )


def test_commit_failure(monkeypatch):
    """Test commit failure when commit confirm is already in progress."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Create RPCError from the failure response
    from ncclient.xml_ import to_ele

    error_xml = _load_resource_file("commit_failure_response.xml")
    error_element = to_ele(error_xml)

    def _commit_failure_side_effect(confirmed=False, timeout=None, persist=None):
        rpc_error_exc = RPCError(error_element)
        raise rpc_error_exc

    manager.commit = MagicMock(side_effect=_commit_failure_side_effect)

    with pytest.raises(Exception) as exc_info:
        netconf.commit(confirmed=True)

    # Verify the exception contains the expected error message
    assert "Commit confirm requested while another commit confirm is in progress" in str(
        exc_info.value
    )
    manager.commit.assert_called_with(
        confirmed=True,
        timeout="None",
        persist=None,
    )


def test_commit_with_remove_ns(monkeypatch):
    """Test commit with remove_ns flag."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    with patch(
        "ansible_collections.drivenets.dnos.plugins.netconf.dnos.remove_namespaces"
    ) as mock_remove_ns:
        mock_remove_ns.return_value = "<rpc-reply><ok/></rpc-reply>"
        result = netconf.commit(remove_ns=True)

        assert result is not None
        mock_remove_ns.assert_called_once()


def test_commit_handles_rpc_error(monkeypatch):
    """Test commit handles RPCError exceptions."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Create a properly formatted rpc-error XML string and convert to element using ncclient
    # RPCError expects an XML element (lxml element), not a string or ElementTree element
    from ncclient.xml_ import to_ele

    error_xml = _load_resource_file("commit_rpc_error_response.xml")
    error_element = to_ele(error_xml)

    def _commit_rpc_error_side_effect(confirmed=False, timeout=None, persist=None):
        rpc_error_exc = RPCError(error_element)
        raise rpc_error_exc

    manager.commit = MagicMock(side_effect=_commit_rpc_error_side_effect)
    with pytest.raises(Exception) as exc_info:
        netconf.commit()
    # Verify the exception contains the expected error message
    assert "Unknown element 'enabled'" in str(exc_info.value)


def test_reboot_operation(monkeypatch):
    """Test reboot operation returns successful response."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    result = netconf.reboot()

    assert result is not None
    assert "<rpc-reply" in result
    assert 'xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"' in result
    # Response is an empty rpc-reply (device acknowledges the restart request)
    manager.reboot.assert_called_once()


@pytest.mark.skipif(not HAS_NCCLIENT, reason="ncclient not available")
def test_get_capabilities_integration(monkeypatch):
    """Integration test for get_capabilities with real JSON parsing."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    def fake_get_base_rpc(self):
        return ["get", "get-config", "edit-config"]

    monkeypatch.setattr(type(netconf), "get_base_rpc", fake_get_base_rpc, raising=True)

    capabilities_json = netconf.get_capabilities()
    capabilities = json.loads(capabilities_json)

    # Verify JSON is valid and contains expected structure
    assert isinstance(capabilities, dict)
    assert all(
        key in capabilities
        for key in [
            "rpc",
            "network_api",
            "device_info",
            "server_capabilities",
            "client_capabilities",
            "session_id",
            "device_operations",
        ]
    )


def test_get_device_info_regex_parsing_edge_cases(monkeypatch):
    """Test get_device_info handles various response formats."""
    netconf, manager = _setup_netconf_with_mock(monkeypatch)

    # Test with different response format
    def custom_dispatch(rpc_element):
        mock_resp = Mock()
        mock_resp.xml = """<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <result xmlns="http://drivenets.com/ns/yang/dn-rpc">
    System Name: edge-router-01
    Version: DNOS [30.1.5] build [1000_prod]
    System Type: NCR-2S, Family: NCR
  </result>
</rpc-reply>"""
        return mock_resp

    monkeypatch.setattr(manager, "dispatch", custom_dispatch, raising=True)

    device_info = netconf.get_device_info()

    assert device_info["network_os_hostname"] == "edge-router-01"
    assert device_info["network_os_version"] == "30.1.5"
    assert device_info["network_os_model"] == "NCR-2S"
