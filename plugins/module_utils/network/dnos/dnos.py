# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The dnos module utils
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import json
import traceback

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection, ConnectionError
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network import (
    get_resource_connection,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.errors import (
    COMMAND_EXECUTION_ERROR_MSG,
    CONFIGURATION_ERROR_MSG,
    CONNECTION_ERROR_MSG,
    DNOSErrorCategory,
    format_error_message,
)


def get_connection(module):
    """Get connection object for DNOS device.
    Args:
        module: AnsibleModule instance
    Returns:
        Connection object
    """
    return Connection(module._socket_path)


def get_capabilities(module):
    """Get capabilities of the device"""
    if hasattr(module, "_dnos_capabilities"):
        return module._dnos_capabilities

    connection = Connection(module._socket_path)
    capabilities = connection.get_capabilities()
    module._dnos_capabilities = json.loads(capabilities)
    return module._dnos_capabilities


def get_dnos_connection(module):
    """Get DNOS connection object.
    This is a wrapper around get_resource_connection that provides
    DNOS-specific connection handling.
    Args:
        module: AnsibleModule instance
    Returns:
        Connection object
    """
    return get_resource_connection(module)


def get_config(module, source="running", flags=None):
    """Get device configuration.
    Args:
        module: AnsibleModule instance
        source: Configuration source (running, candidate, startup)
        flags: Additional flags
    Returns:
        str: Configuration text
    """
    connection = get_connection(module)
    cmd = "show config | no-more"
    if flags:
        cmd = f"{cmd} {' '.join(flags)}"
    try:
        return connection.get(cmd)
    except ConnectionError as exc:
        module.fail_json(
            msg=format_error_message(
                CONNECTION_ERROR_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="get_config",
            ),
            error_category=DNOSErrorCategory.CONNECTION,
            command=cmd,
        )
    except Exception as exc:
        module.fail_json(
            msg=format_error_message(
                CONFIGURATION_ERROR_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="get_config",
            ),
            error_category=DNOSErrorCategory.CONFIGURATION,
            exception=traceback.format_exc(),
            command=cmd,
        )


def load_config(module, commands, commit=True, comment=None, confirm=None):
    """Load configuration to device.
    Args:
        module: AnsibleModule instance
        commands: List of configuration commands
        commit: Whether to commit the configuration
        comment: Commit comment
        confirm: Confirmed commit timeout in minutes
    Returns:
        dict: Response from device
    """
    connection = get_connection(module)
    try:
        # Enter configuration mode
        connection.edit_config(candidate=commands, commit=commit, comment=comment)
        return {"changed": True}
    except ConnectionError as exc:
        module.fail_json(
            msg=format_error_message(
                CONNECTION_ERROR_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="load_config",
            ),
            error_category=DNOSErrorCategory.CONNECTION,
        )
    except Exception as exc:
        module.fail_json(
            msg=format_error_message(
                CONFIGURATION_ERROR_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="load_config",
            ),
            error_category=DNOSErrorCategory.CONFIGURATION,
            exception=traceback.format_exc(),
        )


def run_commands(module, commands, check_rc=True):
    """Run operational commands on device.
    Args:
        module: AnsibleModule instance
        commands: Command or list of commands
        check_rc: Whether to check return codes
    Returns:
        list: Command responses
    """
    connection = get_connection(module)
    commands = to_list(commands)
    responses = []
    for cmd in commands:
        try:
            response = connection.get(cmd)
            responses.append(response)
        except ConnectionError as exc:
            if check_rc:
                module.fail_json(
                    msg=format_error_message(
                        CONNECTION_ERROR_MSG,
                        details=to_text(exc, errors="surrogate_then_replace"),
                        operation="run_commands",
                    ),
                    error_category=DNOSErrorCategory.CONNECTION,
                    command=cmd,
                )
            else:
                responses.append(None)
        except Exception as exc:
            if check_rc:
                module.fail_json(
                    msg=format_error_message(
                        COMMAND_EXECUTION_ERROR_MSG,
                        details=to_text(exc, errors="surrogate_then_replace"),
                        operation="run_commands",
                    ),
                    error_category=DNOSErrorCategory.COMMAND,
                    exception=traceback.format_exc(),
                    command=cmd,
                )
            else:
                responses.append(None)
    return responses
