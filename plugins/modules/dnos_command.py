#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for dnos_command
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = r"""
---
module: dnos_command
short_description: Run commands on remote DNOS devices
description:
  - Sends arbitrary commands to a DriveNets DNOS device and returns the results
    read from the device. This module includes an argument that causes the
    module to wait for a specific condition before returning or timing out if
    the condition is not met.
  - This module does not support running commands in configuration mode.
    Use M(drivenets.dnos.dnos_config) to configure DNOS devices.
  - This module only supports CLI command execution and does not support NETCONF.
    For device configuration using NETCONF, use other DNOS configuration modules.
version_added: '1.0.0'
author:
  - Abishek Suresh Kumar (@askumar-dn)
  - Gennady Mescheryakov (@gennadym-dn)
  - Dragos Lazar (@dlazar-dn)
notes:
  - Tested against DNOS 25.2.0
  - This module works with connection C(network_cli).
  - This module is designed for operational command execution and information gathering
options:
  commands:
    description:
      - List of commands to send to the remote DNOS device over the
        configured provider. Returns the resulting output from the command.
        When you provide the I(wait_for) argument, the
        module waits until the condition is satisfied or
        the number of retries has expired.
      - The I(commands) module argument accepts formatting options
        that allow you to pass arguments to the command.
    required: true
    type: list
    elements: raw
  wait_for:
    description:
      - List of conditions to evaluate against the output of the
        command. The task waits for each condition to be true
        before moving forward. If a conditional is not true
        within the configured number of I(retries), the task fails.
        See examples.
    type: list
    elements: str
  match:
    description:
      - Use the I(match) argument in conjunction with the
        I(wait_for) argument to specify the match policy. Valid
        values are C(all) or C(any). When set to C(all),
        all conditionals in the wait_for must be satisfied. When
        set to C(any), only one of the values must be
        satisfied.
    default: all
    type: str
    choices: ['any', 'all']
  retries:
    description:
      - Specifies the number of retries a command should be tried
        before it is considered failed. The command runs on the
        target device every retry and is evaluated against the
        I(wait_for) conditions.
    default: 10
    type: int
  interval:
    description:
      - Configures the interval in seconds to wait between retries
        of the command. If the command does not pass the specified
        conditions, the interval indicates how long to wait before
        trying the command again.
    default: 1
    type: int
  cli_timestamp:
    description:
      - Controls whether to enable CLI timestamp for this command session.
      - When set to C(true), executes 'set cli-timestamp' before running commands.
      - When set to C(false), executes 'unset cli-timestamp' before running commands.
      - When set to C(none) (default), does not modify the timestamp setting.
      - This is a session-level setting that overrides the system configuration.
    type: bool
    required: false
"""
EXAMPLES = r"""
# Execute show commands
- name: Run show version on remote devices
  drivenets.dnos.dnos_command:
    commands: show system version
- name: Run show version and check to see if output contains DNOS
  drivenets.dnos.dnos_command:
    commands: show system version
    wait_for: result[0] contains DNOS
- name: Run multiple commands on remote nodes
  drivenets.dnos.dnos_command:
    commands:
      - show system version
      - show system uptime
      - show interfaces
- name: Run multiple commands and evaluate the output
  drivenets.dnos.dnos_command:
    commands:
      - show interfaces ge100-0/0/1
      - show isis neighbors
    wait_for:
      - result[0] contains "Operational State: Up"
      - result[1] contains "UP"
- name: Run commands that require answering a prompt
  drivenets.dnos.dnos_command:
    commands:
      - command: 'clear counters all'
        prompt: 'Clear all counters? [y/N]:'
        answer: 'y'
- name: Run commands with complex formatting
  drivenets.dnos.dnos_command:
    commands:
      - command: "run ping {{ ip_address }} count 5"
- name: Wait for interface to be up
  drivenets.dnos.dnos_command:
    commands:
      - show interfaces ge100-0/0/1
    wait_for:
      - result[0] contains "Admin State: Enabled"
      - result[0] contains "Operational State: Up"
    retries: 20
    interval: 2
# Enable CLI timestamp for debugging
- name: Run commands with timestamp enabled for troubleshooting
  drivenets.dnos.dnos_command:
    commands:
      - show system uptime
      - show interfaces
      - show bgp summary
    cli_timestamp: true
# Disable CLI timestamp explicitly
- name: Run commands with timestamp disabled for clean output
  drivenets.dnos.dnos_command:
    commands:
      - show config
    cli_timestamp: false
# Use cli_timestamp with variables for dynamic control
- name: Debug network issues with conditional timestamps
  drivenets.dnos.dnos_command:
    commands:
      - show interfaces ge100-0/0/1
      - show interfaces ge100-0/0/1 counters
    cli_timestamp: "{{ enable_debug_timestamps | default(true) }}"
  register: interface_output
- name: Check BGP neighbor state with custom wait
  drivenets.dnos.dnos_command:
    commands:
      - show bgp neighbors {{ neighbor_ip }}
    wait_for:
      - result[0] contains "BGP state: Established"
    match: all
    retries: 30
    interval: 5
"""
RETURN = r"""
stdout:
  description: The set of responses from the commands
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: |
    [
      "System Name: DN-SA-06\nVersion: DNOS [25.2.0] build [411]",
      "System Name: DN-SA-06\nCurrent Time: 26-Aug-2025 00:15:30 UTC\nSystem Uptime: 24 days, 12:15:30"
    ]
stdout_lines:
  description: The value of stdout split into a list
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: |
    [
      [
        "System Name: DN-SA-06",
        "Version: DNOS [25.2.0] build [411]"
      ],
      [
        "System Name: DN-SA-06",
        "Current Time: 26-Aug-2025 00:15:30 UTC",
        "System Uptime: 24 days, 12:15:30"
      ]
    ]
failed_conditions:
  description: The list of conditionals that have failed
  returned: failed
  type: list
  sample: ['result[0] contains "BGP state: Established"', 'result[1] contains "Operational State: Up"']
warnings:
  description: List of warnings if any
  returned: when warnings are present
  type: list
  sample: ['CLI timestamp enabled for session', 'Command execution completed with timestamps']
"""

import time
import traceback

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import (
    Conditional,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    ComplexList,
)

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import get_connection
from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.errors import (
    COMMAND_EXECUTION_ERROR_MSG,
    TIMEOUT_WAITING_FOR_CONDITION_MSG,
    UNEXPECTED_ERROR_MSG,
    DNOSErrorCategory,
    DNOSErrorSeverity,
    format_error_message,
)


def parse_commands(module, warnings):
    """Parse and validate commands.
    Args:
        module: AnsibleModule instance
        warnings: List to collect warnings
    Returns:
        list: Parsed commands
    """
    command_parser = ComplexList(
        dict(
            command=dict(key=True),
            prompt=dict(),
            answer=dict(),
            newline=dict(type="bool", default=True),
            sendonly=dict(type="bool", default=False),
            check_all=dict(type="bool", default=False),
        ),
        module,
    )
    # Get commands from module params
    commands = module.params["commands"]
    # Transform commands to the required format
    parsed_commands = command_parser(commands)
    return parsed_commands


def to_cli(commands):
    """Convert commands to CLI format.
    Args:
        commands: List of command dicts
    Returns:
        list: Commands formatted for CLI
    """
    cli_commands = []
    for cmd in commands:
        if isinstance(cmd, dict):
            cli_commands.append(cmd)
        else:
            cli_commands.append({"command": cmd})
    return cli_commands


def run_commands(module, commands, check_rc=True, cli_timestamp=None):
    """Run commands on the device.
    Args:
        module: AnsibleModule instance
        commands: List of commands to run
        check_rc: Whether to check return codes
        cli_timestamp: Whether to set/unset cli-timestamp for session
    Returns:
        list: Command responses
    """
    connection = get_connection(module)
    responses = []
    # Handle cli_timestamp setting for the session
    if cli_timestamp is not None:
        timestamp_cmd = "set cli-timestamp" if cli_timestamp else "unset cli-timestamp"
        try:
            connection.send_command(timestamp_cmd)
        except Exception:
            # Silently ignore if the command fails (might not be supported in all versions)
            pass
    for cmd in commands:
        if isinstance(cmd, dict):
            command = cmd["command"]
            prompt = cmd.get("prompt")
            answer = cmd.get("answer")
            newline = cmd.get("newline", True)
            sendonly = cmd.get("sendonly", False)
        else:
            command = cmd
            prompt = None
            answer = None
            newline = True
            sendonly = False
        # Skip configuration commands
        if command.startswith(("config", "configure")):
            module.fail_json(
                msg="dnos_command does not support running config mode commands. "
                "Please use dnos_config instead",
                error_category=DNOSErrorCategory.VALIDATION,
                command=command,
            )
        try:
            if sendonly:
                connection.send(
                    command, prompt=prompt, answer=answer, newline=newline, sendonly=True
                )
                responses.append(None)
            else:
                out = connection.get(command, prompt=prompt, answer=answer, newline=newline)
                responses.append(to_text(out, errors="surrogate_or_strict"))
        except Exception as exc:
            if check_rc:
                module.fail_json(
                    msg=format_error_message(
                        COMMAND_EXECUTION_ERROR_MSG,
                        details=to_text(exc, errors="surrogate_or_strict"),
                        operation="run_command",
                    ),
                    error_category=DNOSErrorCategory.COMMAND,
                    error_severity=DNOSErrorSeverity.HIGH,
                    command=command,
                    exception=traceback.format_exc(),
                )
            else:
                responses.append(None)
    return responses


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        commands=dict(type="list", elements="raw", required=True),
        wait_for=dict(type="list", elements="str"),
        match=dict(default="all", choices=["all", "any"]),
        retries=dict(default=10, type="int"),
        interval=dict(default=1, type="int"),
        cli_timestamp=dict(type="bool", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    warnings = []
    result = {"changed": False, "warnings": warnings}

    try:
        # Parse commands
        commands = module.params["commands"]
        wait_for = module.params["wait_for"] or []
        match = module.params["match"]
        retries = module.params["retries"]
        interval = module.params["interval"]
        cli_timestamp = module.params.get("cli_timestamp")

        # Parse and validate commands
        commands = parse_commands(module, warnings)
        commands = to_cli(commands)

        # Create conditionals
        conditionals = [Conditional(c) for c in wait_for]

        # Run commands with retry logic
        while retries > 0:
            responses = run_commands(module, commands, cli_timestamp=cli_timestamp)

            # Check conditionals
            satisfied_conditionals = []
            for item in conditionals:
                condition_result = item(responses)
                if condition_result:
                    satisfied_conditionals.append(item)
                    if match == "any":
                        conditionals = []
                        break

            # Remove satisfied conditionals for "all" match
            if match == "all":
                for satisfied in satisfied_conditionals:
                    if satisfied in conditionals:
                        conditionals.remove(satisfied)

            if not conditionals:
                break

            retries -= 1
            if retries <= 0:
                break

            if interval > 0:
                time.sleep(interval)

        if conditionals:
            failed_conditions = [item.raw for item in conditionals]
            module.fail_json(
                msg=format_error_message(
                    TIMEOUT_WAITING_FOR_CONDITION_MSG,
                    details=f"Failed conditions: {', '.join(failed_conditions)}",
                ),
                error_category=DNOSErrorCategory.TIMEOUT,
                error_severity=DNOSErrorSeverity.MEDIUM,
                failed_conditions=failed_conditions,
            )

        # Prepare results
        result.update(
            {"stdout": responses, "stdout_lines": [r.split("\n") if r else [] for r in responses]}
        )
        module.exit_json(**result)

    except SystemExit:
        # Re-raise SystemExit to allow module.exit_json() and module.fail_json() to work
        raise
    except Exception as exc:
        # Catch any unexpected exceptions that escaped other handlers
        module.fail_json(
            msg=format_error_message(
                UNEXPECTED_ERROR_MSG,
                details=to_text(exc, errors="surrogate_or_strict"),
                operation="main",
            ),
            error_category=DNOSErrorCategory.GENERAL,
            error_severity=DNOSErrorSeverity.CRITICAL,
            exception=traceback.format_exc(),
            **result,
        )


if __name__ == "__main__":
    main()
