# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = r"""
---
author:
  - Abishek Suresh Kumar (@askumar-dn)
  - Gennady Mescheryakov (@gennadym-dn)
  - Dragos Lazar (@dlazar-dn)
name: dnos
short_description: Use dnos cliconf to run command on DNOS platform
description:
  - This dnos plugin provides low level abstraction APIs for sending and receiving CLI
    commands from DNOS network devices.
version_added: "0.1.0"
options:
  config_commands:
    description:
      - Specifies a list of commands that can make configuration changes
        to the target device.
      - When C(ansible_network_single_user_mode) is enabled, if a command sent
        to the device is present in this list, the existing cache is invalidated.
    version_added: "0.1.0"
    type: list
    elements: str
    default: []
    vars:
      - name: ansible_dnos_config_commands
"""

import json
import logging
import re
import time

from contextlib import contextmanager

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible.plugins.cliconf import CliconfBase
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list


logger = logging.getLogger(__name__)


class Cliconf(CliconfBase):
    __rpc__ = CliconfBase.__rpc__ + [
        "commit",
        "discard_changes",
        "run_commands",
    ]

    def __init__(self, *args, **kwargs):
        super(Cliconf, self).__init__(*args, **kwargs)
        self._device_info = {}

    def get_device_info(self):
        if not self._device_info:
            device_info = {}

            device_info["network_os"] = "dnos"
            reply = self.get("show system")
            data = to_text(reply, errors="surrogate_or_strict").strip()

            match = re.search(r"Version:\s*(.*)", data)
            if match:
                device_info["network_os_version"] = match.group(1)

            match = re.search(r"System Type:\s*(\S+)", data)
            if match:
                device_info["network_os_model"] = match.group(1)

            reply = self.get("show system name")
            data = to_text(reply, errors="surrogate_or_strict").strip()

            match = re.search(r"System name:\s*(.*)", data)
            if match:
                device_info["network_os_hostname"] = match.group(1)

            self._device_info = device_info

        return self._device_info

    def get_config(self, flags=None, format="text"):
        if format:
            option_values = self.get_option_values()
            if format not in option_values["format"]:
                raise ValueError(
                    "'format' value %s is invalid. Valid values of format are %s"
                    % (format, ", ".join(option_values["format"]))
                )

        if not flags:
            flags = []

        command = "show config "
        command += " ".join(to_list(flags))
        command = command.strip()

        out = self.send_command(command)
        return out

    def _is_config_mode(self):
        prompt = to_text(self._connection.get_prompt(), errors="surrogate_or_strict")
        return "(cfg" in prompt

    @contextmanager
    def config_mode(self):
        """
        Context manager to enter and exit configuration mode.
        Ensures that 'exit' is sent to leave config mode on exit.
        """
        try:
            logger.debug("Entering config_mode()")
            if not self._is_config_mode():
                self.send_command("configure")
            yield
        finally:
            if self._is_config_mode():
                self.send_command("exit")
            timeout = 3  # seconds
            start_time = time.monotonic()
            while time.monotonic() - start_time < timeout:
                if not self._is_config_mode():
                    break
                self.send_command("exit")
            if not self._is_config_mode():
                logger.debug("Exited config_mode()")
            else:
                logger.warning("Failed to exit config_mode()")
                prompt = to_text(self._connection.get_prompt(), errors="surrogate_or_strict")
                raise AnsibleConnectionFailure(
                    "Failed to exit config_mode(). Device prompt: %s" % prompt
                )

    def _validate_config_command_result(self, command, output):
        """
        Validate a single configuration command result.
        - Treat presence of 'ERROR: Unknown word' as failure
        - Ensure prompt remains in configuration mode (matches cfg.*)#)
        """
        out_text = to_text(output, errors="surrogate_or_strict")
        if re.search(r"(?i)\bERROR:\s*Unknown\s+word\b", out_text):
            raise AnsibleConnectionFailure(
                "Configuration command failed: '%s' -> %s" % (command, out_text)
            )
        prompt_text = to_text(self._connection.get_prompt(), errors="surrogate_or_strict")
        if not re.search(r"\(cfg.*\)", prompt_text):
            raise AnsibleConnectionFailure(
                "Unexpected prompt after command '%s': %s" % (command, prompt_text)
            )

    # Match the base class signature; use kwargs to accept optional extras (e.g. comment)
    def edit_config(self, candidate=None, commit=None, replace=None, confirm=None, **kwargs):
        comment = kwargs.get("comment")
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(operations, candidate, commit, replace, comment)

        results = []
        requests = []
        if not self._is_config_mode():
            self.send_command("configure")
        if isinstance(candidate, str) and "\n" in candidate:
            candidate = candidate.splitlines()
        for cmd in to_list(candidate):
            if not isinstance(cmd, Mapping):
                cmd = {"command": cmd}
            cmd_out = to_text(self.send_command(**cmd))
            self._validate_config_command_result(cmd["command"], cmd_out)
            results.append(cmd_out)
            raw_prompt = to_text(self._connection.get_prompt())
            logger.info("edit_config() cmd %s cmd_out: %s raw_prompt: %s", cmd, cmd_out, raw_prompt)
            requests.append(cmd["command"])

        out = self.get("show config compare")
        out = to_text(out, errors="surrogate_or_strict")
        diff_config = out.splitlines() if out else None

        if diff_config:
            if commit:
                try:
                    resp.update(self.commit(comment=comment, confirm=confirm))
                except AnsibleConnectionFailure as e:
                    msg = "commit failed: %s" % getattr(e, "message", str(e))
                    self.discard_changes()
                    raise AnsibleConnectionFailure(msg)
                else:
                    self.send_command("exit")
            else:
                self.discard_changes()
        else:
            self.send_command("exit")
            if (
                to_text(self._connection.get_prompt(), errors="surrogate_or_strict")
                .strip()
                .endswith("#")
            ):
                self.discard_changes()

        if diff_config:
            resp["diff"] = diff_config
        resp["response"] = results
        resp["request"] = requests
        return resp

    def validate_config(self, candidate):
        COMMIT_CHECK_SUCCESS_MESSAGE = "Commit check passed successfully"
        COMMIT_CHECK_FAILURE_PREFIX = "ERROR:"
        ROLLBACK_COMMAND = "rollback 0"

        logger.info("validate_config() called with %s commands", len(to_list(candidate)))
        candidate_list = to_list(candidate)

        try:
            with self.config_mode():
                for idx, cmd in enumerate(candidate_list, start=1):
                    if not isinstance(cmd, Mapping):
                        cmd = {"command": cmd}

                    logger.info(
                        "validate_config() validating command %s/%s: %s",
                        idx,
                        len(candidate_list),
                        cmd["command"],
                    )
                    out = to_text(self.send_command(**cmd))
                    self._validate_config_command_result(cmd["command"], out)

                # Validate commit check succeeded
                logger.info("validate_config() running 'commit check' command")
                check_out = to_text(self.send_command(command="commit check"))

                if COMMIT_CHECK_SUCCESS_MESSAGE not in check_out:
                    error_lines = [
                        line.strip()
                        for line in check_out.splitlines()
                        if COMMIT_CHECK_FAILURE_PREFIX in line
                    ]
                    error_message = "\n".join(error_lines) if error_lines else check_out.strip()

                    logger.error("validate_config() commit check failed: %s", error_message)
                    logger.info("validate_config() discarding changes due to commit check failure")
                    self.send_command(ROLLBACK_COMMAND)
                    raise AnsibleConnectionFailure(
                        "Configuration validation failed during commit check:\n%s" % error_message
                    )

                logger.info("validate_config() commit check passed successfully")
                logger.info("validate_config() discarding changes after successful validation")
                self.send_command(ROLLBACK_COMMAND)

        except AnsibleConnectionFailure:
            raise
        except Exception as e:
            logger.error("validate_config() unexpected error: %s", str(e))
            try:
                self.send_command(ROLLBACK_COMMAND)
            except Exception:
                pass
            raise AnsibleConnectionFailure("Configuration validation failed: %s" % str(e))

        logger.info("validate_config() completed successfully")

    # Match base class signature to satisfy pylint
    def get(self, command=None, prompt=None, answer=None, output=None, newline=None, **kwargs):
        if not command:
            raise ValueError("must provide value of command to execute")
        if output:
            raise ValueError("'output' value %s is not supported for get" % output)

        return self.send_command(
            command=command, prompt=prompt, answer=answer, newline=newline, **kwargs
        )

    def commit(self, comment=None, confirm=None, ignore_empty_commit=True):
        COMMIT_SUCCEEDED = "Commit succeeded"
        COMMIT_CONFIRMED = "Commit confirmed"
        COMMIT_CONFIRM = "Commit confirm will be automatically rolled back"
        EMPTY_COMMIT = "NOTICE: commit action is not applicable. no configuration changes were made"
        COMMIT_PATTERN = (COMMIT_SUCCEEDED, COMMIT_CONFIRMED)
        resp = {}
        commit_cmd = "commit"
        if comment:
            comment = comment.replace('"', "")
            comment = f'"{comment}"'
            commit_cmd += f" log {comment}"
        if confirm:
            commit_cmd = "commit confirm"
            COMMIT_PATTERN = (COMMIT_CONFIRM,)
        if confirm is not None and int(confirm) > 0:
            commit_cmd = f"commit confirm {confirm}"
        commit_cmd = {"command": commit_cmd}
        out = None
        if not self._is_config_mode():
            with self.config_mode():
                out = to_text(self.send_command(**commit_cmd))
        else:
            out = to_text(self.send_command(**commit_cmd))
        err_msg = "Commit operation Failed.\n"
        err_msg += "user commit: <" + commit_cmd["command"] + ">\n"
        kwargs = {
            "comment": comment,
            "confirm": confirm,
            "ignore_empty_commit": ignore_empty_commit,
        }
        err_msg += "commit options: " + str(kwargs) + "\n"
        err_msg += "commit output: <" + out + ">\n"

        if EMPTY_COMMIT in out:
            if ignore_empty_commit is False:
                raise AnsibleConnectionFailure(err_msg)
        else:
            for pattern in COMMIT_PATTERN:
                if pattern in out:
                    resp["changed"] = True
                    break
            else:
                raise AnsibleConnectionFailure(err_msg)
        return resp

    def discard_changes(self, rollback_version=None, rollback_commit_msg=None):
        resp = {}
        with self.config_mode():
            rollback_cmd = f"rollback {rollback_version}" if rollback_version else "rollback"

            out = to_text(self.send_command(rollback_cmd))
            if out.strip() and "rollback complete" not in out:
                raise AnsibleConnectionFailure(
                    "Rollback failed or returned unexpected output: %s" % out
                )

            if rollback_version:
                resp.update(self.commit(comment=rollback_commit_msg))
        return resp

    def cancel_pending_commit(self):
        with self.config_mode():
            out = to_text(self.send_command(command="clear system commit"))
            if out.strip() and not re.search(
                r"(?i)Configuration commit confirm rollbacked by", out
            ):
                raise AnsibleConnectionFailure(
                    "Clear system commit failed or returned unexpected output: %s" % out
                )

    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {"command": cmd}

            output = cmd.pop("output", None)
            if output:
                raise ValueError("'output' value %s is not supported for run_commands" % output)

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, "err", e)

            responses.append(out)

        return responses

    def get_device_operations(self):
        return {
            "supports_diff_replace": False,
            "supports_commit": True,
            "supports_rollback": True,
            "supports_defaults": False,
            "supports_onbox_diff": False,
            "supports_commit_comment": True,
            "supports_multiline_delimiter": False,
            "supports_diff_match": True,
            "supports_diff_ignore_lines": False,
            "supports_generate_diff": True,
            "supports_replace": False,
        }

    def get_option_values(self):
        return {
            "format": ["text"],  # show config displays output as text only
            "diff_match": [],
            "diff_replace": [],
            "output": [],
        }

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result["device_operations"] = self.get_device_operations()
        result.update(self.get_option_values())
        return json.dumps(result)

    def set_cli_prompt_context(self):
        """
        Make sure we are in the operational cli mode
        :return: None
        """
        if self._connection.connected:
            prompt = self._connection.get_prompt()

            if re.search(
                r"cfg.*\)#",
                to_text(prompt, errors="surrogate_then_replace").strip(),
            ):
                self._connection.queue_message(
                    "vvvv", "configuration context, discarding changes and sending end to device"
                )
                self._connection.send_command("rollback")
                self._connection.send_command("end")
