# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Common fixtures and utilities for DNOS unit tests."""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic


def patch_load_params():
    """Patch basic._load_params to handle profile "2.0" with plain JSON encoding.

    Ansible requires a profile to be set, but we use plain json.dumps() in tests
    rather than the profile-specific encoder. This patch allows plain JSON to work
    with profile "2.0" for testing purposes.

    Returns:
        tuple: (original_load_params, patched_load_params) for cleanup
    """
    original_load_params = basic._load_params

    def patched_load_params():
        """Patched _load_params that handles errors such as
        No serialization profile was specified.
        Failed to decode JSON module parameters.
        """
        if basic._ANSIBLE_ARGS is None:
            # Use the original implementation if args aren't set
            return original_load_params()

        buffer = basic._ANSIBLE_ARGS

        # For profile "2.0" in tests, use plain JSON decoding
        # In real Ansible execution, this would use the profile decoder
        try:
            params = json.loads(buffer.decode("utf-8"))
        except Exception as ex:
            raise Exception("Failed to decode JSON module parameters.") from ex

        return params.get("ANSIBLE_MODULE_ARGS", {})

    # Apply the patch
    basic._load_params = patched_load_params

    return original_load_params, patched_load_params


class AnsibleModuleFixtures:
    """Helper class to manage Ansible module patches in test classes."""

    def __init__(self):
        self.original_load_params = None
        self.original_record_module_result = None
        self.mock_patches = []

    def setup_load_params(self):
        """Set up _load_params patch."""
        self.original_load_params = patch_load_params()[0]

    def setup_get_connection(self, module_path):
        """Set up get_connection patch.

        Args:
            module_path: The module path where get_connection is imported

        Returns:
            tuple: (mock_get_connection, mock_connection)
        """
        get_connection_path = f"{module_path}.get_connection"
        mock_patch = patch(get_connection_path)
        mock_get_connection = mock_patch.start()
        self.mock_patches.append(mock_patch)

        # Create a mock connection object
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        # Ensure mock connection methods return strings by default
        mock_connection.get.return_value = ""
        mock_connection.send.return_value = None

        return mock_get_connection, mock_connection

    def setup_get_config(self, module_path):
        """Set up get_config patch.

        Args:
            module_path: The module path where get_config is imported

        Returns:
            mock_get_config: The mocked get_config function
        """
        get_config_path = f"{module_path}.get_config"
        mock_patch = patch(get_config_path)
        mock_get_config = mock_patch.start()
        self.mock_patches.append(mock_patch)
        return mock_get_config

    def teardown(self):
        """Restore all patches."""
        if self.original_load_params is not None:
            basic._load_params = self.original_load_params
        if self.original_record_module_result is not None:
            basic.AnsibleModule._record_module_result = self.original_record_module_result
        for mock_patch in self.mock_patches:
            mock_patch.stop()
        self.mock_patches.clear()
