#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for dnos_config
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = r"""
---
module: dnos_config
short_description: Manage DNOS configuration sections
description:
  - DriveNets DNOS configurations use a simple block indent file syntax
    for segmenting configuration into sections. This module provides
    an implementation for working with DNOS configuration sections in
    a deterministic way.
version_added: '1.0.0'
author:
  - Abishek Suresh Kumar (@askumar-dn)
  - Gennady Mescheryakov (@gennadym-dn)
  - Dragos Lazar (@dlazar-dn)
notes:
  - Tested against DNOS 25.2.0
  - This module works with connection C(network_cli).
  - This module also supports C(netconf) connection for YANG model-based configuration.
  - DNOS uses a candidate configuration model. Configuration changes are applied to a candidate configuration and then committed.
  - When you use NETCONF transport, the module automatically uses YANG models for configuration, when available.
options:
  lines:
    description:
      - The ordered set of commands to configure in the
        section. The commands must be the exact same commands as found
        in the device config. Be sure to note the configuration
        command syntax as some commands are automatically modified by the
        device config parser.
    type: list
    elements: str
    aliases: [commands]
  parents:
    description:
      - The ordered set of parents that uniquely identify the section or hierarchy
        to check the commands against. If you omit the parents argument,
        the module checks the commands against the set of top
        level or global commands.
    type: list
    elements: str
  src:
    description:
      - Path to a file with configuration or a template rendered to configuration.
      - Mutually exclusive with I(lines) and I(parents).
      - The path can be absolute on the controller or relative to the playbook/role.
    type: path
  before:
    description:
      - Commands to push on the command stack before making any changes.
    type: list
    elements: str
  after:
    description:
      - Commands to append to the command stack after you make changes.
    type: list
    elements: str
  match:
    description:
      - How to compare the provided commands to the device config.
    type: str
    choices: [line, strict, exact, none]
    default: line
  backup:
    description:
      - Create a backup of the current configuration.
    type: bool
    default: false
  backup_options:
    description:
      - Backup configuration options.
    type: dict
    suboptions:
      filename:
        description: Backup filename.
        type: str
      dir_path:
        description: Backup directory path.
        type: path
  running_config:
    description:
      - Running configuration for comparison.
    type: str
  diff_against:
    description:
      - Compare configuration against.
      - When set to C(intended), compares the device's current running configuration
        against the intended configuration supplied via I(intended_config).
        This comparison is independent of any configuration changes specified in I(lines) or I(src).
        Uses the router's onbox C(show config compare) command for accurate diff generation.
      - When set to C(running), shows the diff that would result from applying
        the configuration specified in I(lines) or I(src).
      - When set to C(startup), compares running config against startup config (not currently supported).
      - Both C(intended) and C(running) use the same mechanism - staging config to candidate
        and using the router's native diff capability, then rolling back without committing.
    type: str
    choices: [startup, intended, running]
  replace:
    description:
      - How to perform configuration on the device.
      - I(line) replaces individual lines, I(block) replaces configuration blocks,
        and I(config) replaces the entire configuration using I(src) or using
        a factory-default override if only I(lines) are provided.
    type: str
    choices: [line, block, config]
  defaults:
    description:
      - Whether to collect defaults when fetching running config. When set to C(true), uses C(show config all).
    type: bool
    default: false
  save_when:
    description:
      - Control when to copy running configuration to startup configuration.
    type: str
    choices: [always, never, modified, changed]
    default: never
  intended_config:
    description:
      - Master configuration used to validate final state (used with I(diff_against=intended)).
      - When I(diff_against=intended), this parameter specifies the intended or desired
        configuration that the device should have. The module will stage this configuration
        to the device's candidate, use the router's native C(show config compare) to generate
        an accurate diff, then rollback without committing.
      - The comparison is independent of what configuration changes are specified in I(lines) or I(src).
      - This is useful for compliance checking and drift detection.
    type: str
  commit:
    description:
      - When set to C(true), commits configuration changes. When set to C(false), changes remain staged.
    type: bool
    default: true
  comment:
    description:
      - Commit comment to record when you commit the configuration.
    type: str
  confirm:
    description:
      - Commit confirm timeout in minutes.
      - When set to C(0), performs a confirm commit without a timeout value (requires manual confirm).
    type: int
    default: 0
  confirm_commit:
    description:
      - Confirm a previously issued C(commit confirm) (in other words, finalize the pending commit).
    type: bool
    default: false
  cancel_pending_commit:
    description:
      - Cancel a pending C(commit confirm). This triggers automatic rollback of the pending commit.
    type: bool
    default: false
  rollback:
    description:
      - Roll back to the specified identifier. Use C(0) to roll back to the most recent commit.
    type: int
  rollback_version:
    description:
      - Explicit rollback version (preferred over I(rollback)).
    type: int
  use_candidate:
    description:
      - Hint to use candidate workflow when supported (auto-detected if not set).
    type: bool
  validate_only:
    description:
      - Validate configuration (apply, commit check, then rollback) without committing.
    type: bool
    default: false
  force_commit:
    description:
      - Force commit even if device indicates no changes (when supported).
    type: bool
    default: false
  load:
    description:
      - Load configuration from a URL accessible to the device.
    type: str
    choices: [merge, override]
  url:
    description:
      - URL to load when using I(load).
      - Should be visible in C(show file config list).
    type: str
  save:
    description:
      - Filename on the device to save configuration to (no directory separators).
      - Executes prior to rollback when I(commit=false), useful for staging or testing.
    type: str
"""
EXAMPLES = r"""
- name: Configure top level configuration
  drivenets.dnos.dnos_config:
    lines: "system name {{ inventory_hostname }}"
- name: Configure interface settings
  drivenets.dnos.dnos_config:
    lines:
      - description test interface
      - mtu 9000
    parents: interfaces ge100-0/0/1
- name: Configure multiple interfaces
  drivenets.dnos.dnos_config:
    lines:
      - description "{{ item.description }}"
      - mtu {{ item.mtu }}
    parents: interfaces {{ item.name }}
  loop:
    - { name: ge100-0/0/1, description: "Uplink Port", mtu: 9000 }
    - { name: ge100-0/0/2, description: "Server Port", mtu: 1500 }
- name: Load configuration from file
  drivenets.dnos.dnos_config:
    src: dnos_template.cfg
    backup: true
- name: Render a template and apply configuration
  drivenets.dnos.dnos_config:
    src: "{{ lookup('template', 'dnos_template.j2') }}"
- name: Save running to startup when modified
  drivenets.dnos.dnos_config:
    save_when: modified
- name: Configuring policy route with exact match
  drivenets.dnos.dnos_config:
    lines:
      - set protocol static route 192.168.1.0/24 next-hop 10.0.0.1
      - set protocol static route 192.168.2.0/24 next-hop 10.0.0.2
    match: exact
- name: Configure BGP AS with before and after
  drivenets.dnos.dnos_config:
    lines:
      - router-id 1.1.1.1
      - neighbor 192.168.1.1 remote-as 65001
    parents: protocol bgp 65000
    before: no protocol bgp 65000
    after: commit comment "BGP configuration update"
    replace: block
- name: Check configuration against intended state (compliance check)
  drivenets.dnos.dnos_config:
    diff_against: intended
    intended_config: "{{ lookup('file', 'intended.cfg') }}"
  # This compares running config vs. intended config only, does not apply any changes
- name: Configure with rollback on error
  drivenets.dnos.dnos_config:
    lines:
      - permit ip any any
    parents: access-lists ipv4 TEST
    commit: true
    confirm: 5
  rescue:
    - name: Rollback to previous configuration
      drivenets.dnos.dnos_config:
        rollback: 0
- name: Configure without auto-commit
  drivenets.dnos.dnos_config:
    lines:
      - description "Staged configuration"
    parents: interfaces ge100-0/0/1
    commit: false
- name: Later commit the changes
  drivenets.dnos.dnos_config:
    commit: true
    comment: "Committing staged changes"
- name: Load configuration from device local file system
  drivenets.dnos.dnos_config:
    load: override
    url: "{{ configuration_file }}"
- name: Save current running configuration to file
  drivenets.dnos.dnos_config:
    save: my_config_file
- name: Configure interface and save to file
  drivenets.dnos.dnos_config:
    lines:
      - description test interface
      - mtu 9000
    parents: interfaces ge100-0/0/1
    save: backup_config
- name: Apply config, save it, then rollback (useful for testing)
  drivenets.dnos.dnos_config:
    lines:
      - description "Test configuration"
    parents: interfaces ge100-0/0/1
    commit: false
    save: test_config_backup
"""
RETURN = r"""
commands:
  description: The set of commands that will be pushed to the remote device.
  returned: always
  type: list
  sample: ['interfaces ge100-0/0/1', 'description test interface', 'mtu 9000']
updates:
  description: The set of commands that will be pushed to the remote device.
  returned: always
  type: list
  sample: ['interfaces ge100-0/0/1', 'description test interface', 'mtu 9000']
backup_path:
  description: The full path to the backup file.
  returned: when backup is yes
  type: str
  sample: /playbooks/ansible/backup/dnos_config.2016-07-16@22:28:34
"""

import re
import time
import traceback

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import ConnectionError
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import (
    get_config,
    get_connection,
)
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.errors import (
    BACKUP_CREATE_FAILED_MSG,
    CONFIGURATION_COMMIT_FAILED_MSG,
    CONFIGURATION_ERROR_MSG,
    CONFIGURATION_LOCKED_MSG,
    CONFIGURATION_ROLLBACK_FAILED_MSG,
    CONFIGURATION_SYNTAX_ERROR_MSG,
    CONFIGURATION_TIMEOUT_MSG,
    CONFIGURATION_VALIDATION_FAILED_MSG,
    CONNECTION_ERROR_MSG,
    RETRY_EXHAUSTED_MSG,
    UNEXPECTED_ERROR_MSG,
    DNOSErrorCategory,
    DNOSErrorSeverity,
    format_error_message,
)


DEFAULT_COMMIT_COMMENT = "Ansible Configuration Update"
FACTORY_DEFAULT_OVERRIDE_CMD = "load override factory-default"
SAVE_COMMAND_PREFIX = "save"
INVALID_FILENAME_CHARS = ["/", "\\"]


def classify_connection_error(error_message):
    """
    Classify a ConnectionError based on its message content to determine
    the appropriate error constant and category.

    Args:
        error_message (str): The error message from ConnectionError

    Returns:
        tuple: (error_constant, error_category, error_severity)
    """
    error_lower = str(error_message).lower()

    # Check for syntax errors
    if any(
        pattern in error_lower
        for pattern in [
            "syntax error",
            "unknown word",
            "invalid command",
            "parse error",
            "unexpected token",
        ]
    ):
        return (
            CONFIGURATION_SYNTAX_ERROR_MSG,
            DNOSErrorCategory.CONFIGURATION,
            DNOSErrorSeverity.HIGH,
        )

    # Check for locked configuration
    if any(pattern in error_lower for pattern in ["locked", "lock denied", "in use"]):
        return (CONFIGURATION_LOCKED_MSG, DNOSErrorCategory.CONFIGURATION, DNOSErrorSeverity.MEDIUM)

    # Check for commit failures
    if any(pattern in error_lower for pattern in ["commit failed", "cannot commit"]):
        return (
            CONFIGURATION_COMMIT_FAILED_MSG,
            DNOSErrorCategory.CONFIGURATION,
            DNOSErrorSeverity.HIGH,
        )

    # Check for validation failures
    if any(
        pattern in error_lower for pattern in ["validation failed", "invalid value", "out of range"]
    ):
        return (
            CONFIGURATION_VALIDATION_FAILED_MSG,
            DNOSErrorCategory.CONFIGURATION,
            DNOSErrorSeverity.HIGH,
        )

    # Check for timeout
    if any(pattern in error_lower for pattern in ["timeout", "timed out"]):
        return (CONFIGURATION_TIMEOUT_MSG, DNOSErrorCategory.TIMEOUT, DNOSErrorSeverity.MEDIUM)

    # Check for actual connection issues
    if any(
        pattern in error_lower
        for pattern in [
            "connection refused",
            "connection closed",
            "connection lost",
            "not connected",
            "connection reset",
        ]
    ):
        return (CONNECTION_ERROR_MSG, DNOSErrorCategory.CONNECTION, DNOSErrorSeverity.CRITICAL)

    # Check for authentication issues
    if any(
        pattern in error_lower
        for pattern in [
            "authentication failed",
            "permission denied",
            "access denied",
            "unauthorized",
        ]
    ):
        return (CONNECTION_ERROR_MSG, DNOSErrorCategory.CONNECTION, DNOSErrorSeverity.HIGH)

    # If it mentions "command failed" or similar, it's a configuration error
    if any(
        pattern in error_lower
        for pattern in ["command failed", "configuration failed", "failed to apply"]
    ):
        return (CONFIGURATION_ERROR_MSG, DNOSErrorCategory.CONFIGURATION, DNOSErrorSeverity.HIGH)

    # Default to configuration error if we can't determine
    return (CONFIGURATION_ERROR_MSG, DNOSErrorCategory.CONFIGURATION, DNOSErrorSeverity.HIGH)


def clean_diff_output(diff):
    """
    Clean up DNOS diff output by removing header, footer, and surrounding empty lines.

    DNOS routers return diffs with:
    - Header: '# <hostname> config-start [<timestamp>]'
    - Footer: '# <hostname> config-end'
    - Empty lines before/after the actual diff content

    This function removes these to make the output cleaner and more readable.
    For empty diffs (no changes), returns an empty list.

    Args:
        diff: List of diff lines or None
    Returns:
        list: Cleaned diff lines, or empty list if no meaningful changes
    """
    if not diff:
        return []

    if not isinstance(diff, list):
        return diff

    cleaned = []
    for line in diff:
        # Skip lines starting with # (header/footer comments)
        if line.strip().startswith("#"):
            continue
        # Keep non-empty lines
        if line.strip():
            cleaned.append(line)

    # Return empty list if no meaningful content remains
    return cleaned if cleaned else []


def clean_response_output(response):
    """
    Clean up DNOS response output by removing empty string entries and progress bars.

    DNOS routers often return empty strings in response arrays which
    clutter the output. They also return progress bars during load operations
    (e.g., [=>...] 50%). This function removes them for cleaner results.

    Args:
        response: List of response lines or None
    Returns:
        list: Cleaned response lines with empty strings and progress bars removed
    """
    if not response:
        return []

    if not isinstance(response, list):
        return response

    # Filter out empty strings, strings with only whitespace, and progress bars
    # Progress bars typically look like: "[=>...] 50%\n" or similar patterns
    cleaned = []
    for line in response:
        if not line or not line.strip():
            continue
        # Skip progress bar lines (contain pattern like "[...] N%")
        # These lines have brackets with progress indicators followed by percentage
        if re.search(r"^\[[\s=>]*\]\s+\d+%", line.strip()):
            continue
        cleaned.append(line)

    return cleaned


def get_connection_capabilities(connection):
    """
    Detect DNOS device capabilities based on connection type.
    Args:
        connection: Ansible connection object
    Returns:
        dict: Capability matrix for the connection type
    """
    try:
        # Check if NETCONF is available by testing candidate operations
        if hasattr(connection, "netconf") or connection.get_option("network_api") == "netconf":
            try:
                connection.lock(target="candidate")
                connection.unlock(target="candidate")
                return {
                    "name": "netconf",
                    "candidate_workflow": True,
                    "atomic_transactions": True,
                    "advanced_rollback": True,
                    "commit_confirm": True,
                    "session_management": True,
                }
            except Exception:
                pass
        # Default to CLI capabilities
        return {
            "name": "cli",
            "candidate_workflow": False,
            "atomic_transactions": False,
            "advanced_rollback": True,
            "commit_confirm": True,
            "session_management": False,
        }
    except Exception:
        # Fallback to basic CLI
        return {
            "name": "cli",
            "candidate_workflow": False,
            "atomic_transactions": False,
            "advanced_rollback": True,
            "commit_confirm": True,
            "session_management": False,
        }


def get_candidate_config(module):
    """Get candidate configuration from device.
    Args:
        module: AnsibleModule instance
    Returns:
        list[str]: Candidate configuration commands
    """
    candidate = []
    if module.params.get("src"):
        candidate = module.params["src"]
        if isinstance(candidate, str):
            candidate = candidate.splitlines()
    elif module.params.get("lines"):
        candidate_obj = NetworkConfig(indent=2)
        parents = module.params.get("parents", list())
        candidate_obj.add(module.params["lines"], parents=parents)
        candidate = dumps(candidate_obj, output="commands")
        if isinstance(candidate, str):
            candidate = candidate.splitlines()
        if module.params["before"]:
            candidate[:0] = module.params["before"]
        if module.params["after"]:
            candidate.extend(module.params["after"])
    return candidate


def get_running_config(module, defaults=False):
    """Get running configuration from device.
    Args:
        module: AnsibleModule instance
        defaults: Whether to include default values
    Returns:
        str: Running configuration text
    """
    flags = []
    if defaults:
        flags.append("all")
    return get_config(module, flags=flags, source="running")


def execute_configuration_safely(module, commands):
    """
    Execute configuration with proper safety measures based on connection type.
    Args:
        module: AnsibleModule instance
        commands: List of configuration commands to execute
    Returns:
        dict: Execution result
    """
    connection = get_connection(module)
    capabilities = get_connection_capabilities(connection)
    result = {
        "changed": False,
        "commands": commands,
        "connection_type": capabilities["name"],
        "capabilities": capabilities,
    }

    return execute_cli_workflow(module, connection, commands, result)


def execute_cli_workflow(module, connection, commands, result):
    """
    Execute configuration using CLI workflow with safety measures.
    Args:
        module: AnsibleModule instance
        connection: CLI connection object (drivenets.dnos.cliconf)
        commands: List of configuration commands to apply
        result: Result dictionary
    Returns:
        dict: Updated result
    """
    try:
        if module.check_mode:
            result["method"] = "cli_check_mode"
            return result

        # Validate-only path: apply → commit check → rollback (no commit)
        if module.params.get("validate_only", False):
            connection.validate_config(candidate=commands)
            result["validation"] = "passed"
            result["method"] = "cli_validate"
            return result

        # Single consolidated call via cliconf.edit_config
        commit_flag = module.params.get("commit", True)
        comment_val = module.params.get("comment")
        confirm_commit_val = module.params.get("confirm")  # allow 0 or >0

        edit_config_mapping = connection.edit_config(
            candidate=commands,
            commit=commit_flag,
            comment=comment_val,
            confirm=confirm_commit_val,
        )
        result.update(edit_config_mapping)
        result["method"] = "cli_edit_config_single_call"
        return result

    except ConnectionError as exc:
        # Best-effort cleanup without forcing prompt changes
        try:
            connection.discard_changes()
        except Exception:
            pass

        # Classify the error based on its content
        error_msg_constant, error_cat, error_sev = classify_connection_error(str(exc))

        module.fail_json(
            msg=format_error_message(
                error_msg_constant,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="cli_workflow",
            ),
            error_category=error_cat,
            error_severity=error_sev,
            **result,
        )
    except Exception as exc:
        # Best-effort cleanup without forcing prompt changes
        try:
            connection.discard_changes()
        except Exception:
            pass
        module.fail_json(
            msg=format_error_message(
                CONFIGURATION_ERROR_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="cli_workflow",
            ),
            error_category=DNOSErrorCategory.CONFIGURATION,
            error_severity=DNOSErrorSeverity.HIGH,
            exception=traceback.format_exc(),
            **result,
        )


def convert_cli_to_netconf(cli_command):
    """
    Convert CLI command to NETCONF XML format.
    Args:
        cli_command: CLI command string
    Returns:
        str: NETCONF XML configuration
    """
    # Simplified conversion placeholder
    return f"<config-items>{cli_command}</config>"


def validate_filename(module, filename):
    """
    Validate that filename doesn't contain directory path separators.

    Args:
        module: AnsibleModule instance
        filename: Filename to validate

    Returns:
        bool: True if valid, calls module.fail_json if invalid
    """
    if not filename:
        module.fail_json(
            msg="Filename cannot be empty",
            error_category=DNOSErrorCategory.VALIDATION,
        )

    for invalid_char in INVALID_FILENAME_CHARS:
        if invalid_char in filename:
            module.fail_json(
                msg=format_error_message(
                    "Invalid filename: filename cannot contain directory path separators",
                    details=f"Filename '{filename}' contains invalid character '{invalid_char}'. Only the filename is allowed, not a path.",
                    operation="validate_filename",
                ),
                error_category=DNOSErrorCategory.VALIDATION,
            )

    return True


def save_config_to_file(module, filename, result):
    """
    Save configuration to a specific file on the device.

    Args:
        module: AnsibleModule instance
        filename: Filename to save configuration to
        result: Result dictionary

    Returns:
        bool: True if saved successfully
    """
    # Validate filename first
    validate_filename(module, filename)

    result["changed"] = True

    if not module.check_mode:
        connection = get_connection(module)
        save_command = f"{SAVE_COMMAND_PREFIX} {filename}"

        try:
            # Execute save command on the device
            connection.edit_config(candidate=[save_command], commit=False)
            result["saved_to_file"] = filename
            result["save_command"] = save_command
        except ConnectionError as exc:
            error_msg_constant, error_cat, error_sev = classify_connection_error(str(exc))
            module.fail_json(
                msg=format_error_message(
                    error_msg_constant,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="save_config_to_file",
                ),
                error_category=error_cat,
                error_severity=error_sev,
                filename=filename,
            )
        except Exception as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_ERROR_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="save_config_to_file",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
                exception=traceback.format_exc(),
                filename=filename,
            )
    else:
        module.warn(f"Skipping save command '{SAVE_COMMAND_PREFIX} {filename}' due to check_mode.")
        result["saved_to_file"] = filename
        result["save_command"] = f"{SAVE_COMMAND_PREFIX} {filename}"

    return True


def save_config(module, result):
    """Save running configuration to startup configuration.
    Args:
        module: AnsibleModule instance
        result: Result dictionary
    Returns:
        bool: True if saved, False otherwise
    """
    result["changed"] = True
    if not module.check_mode:
        # DNOS uses 'save' command in config mode
        connection = get_connection(module)
        try:
            connection.edit_config(candidate=["save"], commit=False)
        except ConnectionError as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_ERROR_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="save_config",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
            )
        except Exception as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_ERROR_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="save_config",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
                exception=traceback.format_exc(),
            )
    else:
        module.warn("Skipping save command due to check_mode.")
    return True


def handle_commit_confirm_operations(module):
    """
    Handle commit confirm operations using actual DNOS commands.
    Args:
        module: AnsibleModule instance
    Returns:
        dict or None: Result if operation performed, None otherwise
    """
    connection = get_connection(module)
    resp = {}
    if module.check_mode:
        return resp
    # Confirm pending commit
    if module.params.get("confirm_commit"):
        try:
            module.log("Confirming pending commit")
            connection.commit()
            resp.update(
                {
                    "changed": True,
                    "confirmed": True,
                    "action": "commit_confirmed",
                    "message": "Pending commit has been confirmed",
                }
            )
        except ConnectionError as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_COMMIT_FAILED_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="confirm_commit",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
            )
        except Exception as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_COMMIT_FAILED_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="confirm_commit",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
                exception=traceback.format_exc(),
            )
    # Cancel pending commit (trigger rollback)
    if module.params.get("cancel_pending_commit"):
        try:
            module.log("Cancelling pending commit")
            connection.cancel_pending_commit()
            resp.update(
                {
                    "changed": True,
                    "cancelled": True,
                    "action": "commit_cancelled",
                    "message": "Pending commit has been cancelled and rolled back",
                }
            )
        except ConnectionError as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_ROLLBACK_FAILED_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="cancel_commit",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
            )
        except Exception as exc:
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_ROLLBACK_FAILED_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="cancel_commit",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
                exception=traceback.format_exc(),
            )
    return resp


def rollback(module):
    """
    Enhanced rollback with validation and safety checks.
    Args:
        module: AnsibleModule instance
    Returns:
        dict: Rollback operation result
    """
    connection = get_connection(module)
    # Determine target version
    target_version = module.params.get("rollback_version") or module.params.get("rollback")
    if target_version is None:
        module.fail_json(
            msg="No rollback version specified",
            error_category=DNOSErrorCategory.VALIDATION,
        )
    resp = {}
    try:
        if not module.check_mode:
            connection.discard_changes(
                rollback_version=target_version,
                rollback_commit_msg=f"Ansible rollback operation: rollback version {target_version}",
            )
            resp.update(
                {
                    "changed": True,
                    "rollback_completed": True,
                    "target_version": target_version,
                    "method": "rollback",
                    "message": f"Successfully rolled back to version {target_version}",
                }
            )
        return resp
    except ConnectionError as exc:
        module.fail_json(
            msg=format_error_message(
                CONFIGURATION_ROLLBACK_FAILED_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="rollback",
            ),
            error_category=DNOSErrorCategory.CONFIGURATION,
            target_version=target_version,
        )
    except Exception as exc:
        module.fail_json(
            msg=format_error_message(
                CONFIGURATION_ROLLBACK_FAILED_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="rollback",
            ),
            error_category=DNOSErrorCategory.CONFIGURATION,
            exception=traceback.format_exc(),
            target_version=target_version,
        )


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        lines=dict(aliases=["commands"], type="list", elements="str"),
        parents=dict(type="list", elements="str"),
        src=dict(type="path"),
        before=dict(type="list", elements="str"),
        after=dict(type="list", elements="str"),
        match=dict(default="line", choices=["line", "strict", "exact", "none"]),
        replace=dict(type="str", required=False, choices=["line", "block", "config"]),
        running_config=dict(type="str"),
        intended_config=dict(type="str"),
        defaults=dict(type="bool", default=False),
        backup=dict(type="bool", default=False),
        backup_options=dict(
            type="dict", options=dict(filename=dict(type="str"), dir_path=dict(type="path"))
        ),
        save_when=dict(
            type="str", choices=["always", "never", "modified", "changed"], default="never"
        ),
        diff_against=dict(type="str", choices=["startup", "intended", "running"]),
        commit=dict(type="bool", default=True),
        comment=dict(type="str"),
        confirm=dict(type="int", default=0),
        confirm_commit=dict(type="bool", default=False),
        cancel_pending_commit=dict(type="bool", default=False),
        # Enhanced rollback parameters
        rollback=dict(type="int"),
        rollback_version=dict(type="int"),
        # Advanced workflow parameters
        use_candidate=dict(type="bool"),
        validate_only=dict(type="bool", default=False),
        force_commit=dict(type="bool", default=False),
        # Load configuration from external sources
        load=dict(type="str", choices=["override", "merge"]),
        url=dict(type="str"),
        # Save configuration to file
        save=dict(type="str"),
    )
    mutually_exclusive = [
        ("lines", "src"),
        ("parents", "src"),
        ("rollback", "lines"),
        ("rollback", "src"),
        ("rollback_version", "lines"),
        ("rollback_version", "src"),
        ("confirm_commit", "cancel_pending_commit"),
        ("confirm_commit", "lines"),
        ("cancel_pending_commit", "lines"),
        ("validate_only", "commit"),
        # load: override/merge is incompatible with other configuration methods
        ("load", "lines"),
        ("load", "src"),
        ("load", "parents"),
        ("load", "before"),
        ("load", "after"),
        ("load", "replace"),
        ("load", "rollback"),
        ("load", "rollback_version"),
    ]
    required_if = [
        ("match", "strict", ["lines"]),
        ("match", "exact", ["lines"]),
        ("diff_against", "intended", ["intended_config"]),
        ("load", "override", ["url"]),
        ("load", "merge", ["url"]),
    ]
    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        required_if=required_if,
        supports_check_mode=True,
    )

    result = {"changed": False, "method": "no_changes"}
    warnings = list()

    try:
        # Handle commit confirm operations first
        commit_confirm_result = handle_commit_confirm_operations(module)
        if commit_confirm_result:
            result.update(commit_confirm_result)
            module.exit_json(**result)

        # Handle rollback operations (enhanced)
        if (
            module.params.get("rollback") is not None
            or module.params.get("rollback_version") is not None
        ):
            rollback_result = rollback(module)
            result.update(rollback_result)
            module.exit_json(**result)

        commands = get_candidate_config(module)

        # Handle replace parameter with 'config' option
        if module.params.get("replace") == "config":
            # When replace: config is specified, prepend factory-default override command
            if commands:
                if isinstance(commands, list):
                    commands.insert(0, FACTORY_DEFAULT_OVERRIDE_CMD)
                else:
                    commands = [FACTORY_DEFAULT_OVERRIDE_CMD] + list(commands)
            else:
                commands = [FACTORY_DEFAULT_OVERRIDE_CMD]
        elif module.params.get("replace"):
            # Other replace options (line, block) are not yet implemented
            module.fail_json(
                msg=f"'replace' option '{module.params.get('replace')}' is currently not implemented. Only 'config' is supported.",
                error_category=DNOSErrorCategory.GENERAL,
            )

        if module.params.get("load"):
            if not module.params.get("url"):
                module.fail_json(
                    msg="url is required when load is 'override' or 'merge'",
                    error_category=DNOSErrorCategory.VALIDATION,
                )

            if module.params.get("load") == "override":
                commands = ["load override " + module.params["url"]]
            elif module.params.get("load") == "merge":
                commands = ["load merge " + module.params["url"]]

        # Add save command to the candidate if specified
        if module.params.get("save"):
            save_filename = module.params["save"]
            # Validate filename
            validate_filename(module, save_filename)

            # Ensure commands is a list
            if commands is None:
                commands = []
            elif not isinstance(commands, list):
                commands = list(commands)

            # Append save command
            save_command = f"{SAVE_COMMAND_PREFIX} {save_filename}"
            commands.append(save_command)
            result["saved_to_file"] = save_filename
            result["save_command"] = save_command

        result["commands"] = commands
        result["updates"] = commands

        # Track whether commands were applied (to avoid double application)
        commands_applied = False

        # Apply the configuration using enhanced workflow
        if commands:
            try:
                # Use the enhanced safe configuration execution
                config_result = execute_configuration_safely(module, commands)

                # Clean up diff output by removing header, footer, and empty lines
                if "diff" in config_result:
                    config_result["diff"] = clean_diff_output(config_result["diff"])

                # Clean up response output by removing empty strings
                if "response" in config_result:
                    config_result["response"] = clean_response_output(config_result["response"])

                # Update result with config_result, but filter out diff if not requested
                # The diff should only be included when --diff flag or diff_against is used
                diff_requested = module._diff or module.params.get("diff_against")
                if not diff_requested and "diff" in config_result:
                    # Remove diff from result if it wasn't requested
                    config_result = {k: v for k, v in config_result.items() if k != "diff"}

                result.update(config_result)
                commands_applied = True
            except ConnectionError as exc:
                # Classify the error based on its content
                error_msg_constant, error_cat, error_sev = classify_connection_error(str(exc))

                module.fail_json(
                    msg=format_error_message(
                        error_msg_constant,
                        details=to_text(exc, errors="surrogate_then_replace"),
                        operation="apply_configuration",
                    ),
                    error_category=error_cat,
                    error_severity=error_sev,
                    **result,
                )

        # Handle backup
        if module.params["backup"]:
            try:
                result["__backup__"] = get_running_config(module)
            except Exception as exc:
                module.fail_json(
                    msg=format_error_message(
                        BACKUP_CREATE_FAILED_MSG,
                        details=to_text(exc, errors="surrogate_then_replace"),
                        operation="backup_config",
                    ),
                    error_category=DNOSErrorCategory.BACKUP_RESTORE,
                    exception=traceback.format_exc(),
                    **result,
                )

        # Handle save_when
        save_when = module.params["save_when"]
        if save_when == "always":
            save_config(module, result)
        elif save_when == "modified":
            running = get_running_config(module)
            startup = get_config(module, source="startup")
            if running != startup:
                save_config(module, result)
        elif save_when == "changed" and result["changed"]:
            save_config(module, result)

        # Handle diff_against parameter for config comparison
        # Note: When just --diff flag is used (module._diff=True), the diff is already
        # included in the result from edit_config() above, so we don't need to call
        # get_config_diff() again.
        # Only call get_config_diff() when diff_against is explicitly set AND
        # commands haven't been applied yet (to avoid sending commands twice).
        #
        # Both diff_against="intended" and "running" use the router's onbox comparison:
        # - Stage config to candidate (without commit)
        # - Router runs 'show config compare'
        # - Rollback/discard changes
        # The only difference is what gets staged:
        # - "intended" stages the intended_config (compliance check)
        # - "running" stages the lines/src commands (change preview)
        if module.params.get("diff_against") and not commands_applied:
            # For diff_against, we need special handling to compare configs
            # This is typically used with commit=false to just show diffs
            diff = get_config_diff(module, commands)

            # Clean up diff output by removing header, footer, and empty lines
            if "diff" in diff:
                diff["diff"] = clean_diff_output(diff["diff"])

            # Clean up response output by removing empty strings
            if "response" in diff:
                diff["response"] = clean_response_output(diff["response"])

            result.update(diff)

        # Add any warnings to the result
        if warnings:
            result["warnings"] = warnings

        module.exit_json(**result)

    except SystemExit:
        # Re-raise SystemExit to allow module.exit_json() and module.fail_json() to work
        raise
    except Exception as exc:
        # Catch any unexpected exceptions that escaped other handlers
        module.fail_json(
            msg=format_error_message(
                UNEXPECTED_ERROR_MSG,
                details=to_text(exc, errors="surrogate_then_replace"),
                operation="main",
            ),
            error_category=DNOSErrorCategory.GENERAL,
            error_severity=DNOSErrorSeverity.CRITICAL,
            exception=traceback.format_exc(),
            **result,
        )


def get_config_diff(module, candidate=None):
    """Get configuration diff between before and after.

    This function handles the diff_against parameter to compare configurations.
    Uses the router's onbox 'show config compare' command for accurate diffs.

    For both 'running' and 'intended' modes:
    1. Applies configuration to candidate (without commit)
    2. Router runs 'show config compare' to generate diff
    3. Discards changes with rollback

    This should NOT be called after commands have already been applied with commit=True,
    as that would cause commands to be sent to the device twice.

    Args:
        module: AnsibleModule instance
        candidate: Candidate configuration commands (only used when diff_against="running")
    Returns:
        dict: Diff with before and after keys
    """
    connection = get_connection(module)
    diff_against = module.params["diff_against"]

    if diff_against == "startup":
        module.fail_json(msg="diff_against 'startup' is not supported for the moment")
    elif diff_against == "intended":
        # For diff_against: intended, compare running config vs. intended config
        # Uses the SAME onbox comparison as diff_against: running
        # 1. Apply intended config (without commit)
        # 2. Device runs 'show config compare'
        # 3. Rollback/discard changes
        candidate = module.params["intended_config"]
    # else: diff_against == "running", use the provided candidate

    # Stage the candidate config, get diff using device's onbox comparison, then discard (commit=False)
    # This will: enter config mode → apply commands → show config compare → rollback
    return connection.edit_config(candidate=candidate, commit=False)


def execute_with_retry(module, operation_func, max_retries=3, retry_delay=5, *args, **kwargs):
    """
    Execute operations with automatic retry and error recovery.

    This function will retry operations on ConnectionError but will call module.fail_json()
    if all retries are exhausted. For non-connection errors, it fails immediately.

    Args:
        module: AnsibleModule instance
        operation_func: Function to execute
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        *args, **kwargs: Arguments to pass to operation_func
    Returns:
        Any: Result from operation_func (on success)
    Note:
        This function calls module.fail_json() on failure and does not return.
    """
    last_exception = None
    last_exception_traceback = None

    for attempt in range(max_retries + 1):
        try:
            return operation_func(*args, **kwargs)
        except ConnectionError as exc:
            last_exception = exc
            last_exception_traceback = traceback.format_exc()
            # If this isn't the last attempt, try recovery
            if attempt < max_retries:
                try:
                    # Attempt graceful recovery
                    connection = get_connection(module)
                    capabilities = get_connection_capabilities(connection)
                    if capabilities["candidate_workflow"]:
                        # NETCONF recovery
                        try:
                            connection.discard_changes()
                            connection.unlock(target="candidate")
                        except Exception:
                            pass
                    else:
                        # CLI recovery - exit config mode and rollback if needed
                        try:
                            connection.edit_config(candidate=["rollback", "exit"])
                        except Exception:
                            pass
                    # Wait before retry
                    time.sleep(retry_delay)
                except Exception:
                    pass  # Recovery failed, but continue to retry
        except Exception as exc:
            # For non-connection errors, don't retry - fail immediately
            module.fail_json(
                msg=format_error_message(
                    CONFIGURATION_ERROR_MSG,
                    details=to_text(exc, errors="surrogate_then_replace"),
                    operation="retry_operation",
                ),
                error_category=DNOSErrorCategory.CONFIGURATION,
                error_severity=DNOSErrorSeverity.HIGH,
                exception=traceback.format_exc(),
            )

    # All retries exhausted - classify error and fail with appropriate message
    error_msg_constant, error_cat, error_sev = classify_connection_error(str(last_exception))

    module.fail_json(
        msg=format_error_message(
            RETRY_EXHAUSTED_MSG,
            details=to_text(last_exception, errors="surrogate_then_replace"),
            operation="retry_operation",
        ),
        error_category=error_cat,
        error_severity=DNOSErrorSeverity.CRITICAL,
        max_retries=max_retries,
        last_error=str(last_exception),
        original_error_type=error_msg_constant,
        exception=last_exception_traceback,
    )


if __name__ == "__main__":
    main()
