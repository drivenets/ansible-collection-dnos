# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The reboot class for dnos_reboot
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type

import time

from ansible.module_utils.connection import ConnectionError

from ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos import get_connection


# Constants
RESTART_COMMAND = "request system restart"
RESTART_CONFIRMATION = "yes"
EXPECTED_PROMPT_REGEX = r".*Are you sure.*\?"
REBOOT_VERIFICATION_DELAY = 2


class RebootModule:
    """
    The dnos_reboot operational class
    """

    def __init__(self, module):
        self._module = module

    def execute_reboot(self):
        """Execute the reboot operation"""
        if not self._module.params["reboot"]:
            return {
                "changed": False,
                "failed": False,
                "rebooted": False,
                "commands": [],
                "msg": "No reboot requested",
            }

        self._module.log("executing device reboot operation")
        connection = get_connection(self._module)

        # Commands that will be executed
        commands = [RESTART_COMMAND, RESTART_CONFIRMATION]

        try:
            # Send the reboot command with prompt/answer to handle the confirmation automatically
            # The send_command will wait for the prompt and automatically respond with the answer
            self._module.log(f"Sending command: {RESTART_COMMAND} with interactive confirmation")

            try:
                response = connection.send_command(
                    command=RESTART_COMMAND,
                    prompt=EXPECTED_PROMPT_REGEX,
                    answer=RESTART_CONFIRMATION,
                )
                self._module.log(f"Restart command sent, response: {response}")
            except (ConnectionError, EOFError, BrokenPipeError) as e:
                # Connection lost during or after confirmation - this is expected!
                # The device receives "yes" and immediately starts rebooting
                self._module.log(f"Connection lost as expected during reboot: {str(e)}")
                return {
                    "changed": True,
                    "failed": False,
                    "rebooted": True,
                    "commands": commands,
                    "msg": "Device reboot initiated successfully",
                }

            # If we get here, the command completed without connection loss
            # Give the device time to process the reboot before verifying connectivity
            time.sleep(REBOOT_VERIFICATION_DELAY)

            try:
                # Attempt to receive any pending data to verify connection status
                test_response = connection.receive()

                # Check if we actually got a meaningful response
                if test_response is None or test_response == "":
                    # No response - connection likely lost, device is rebooting
                    return {
                        "changed": True,
                        "failed": False,
                        "rebooted": True,
                        "commands": commands,
                        "msg": "Device reboot initiated successfully",
                    }

                # Device is still responding with actual data - reboot may not have occurred
                return {
                    "changed": True,
                    "failed": True,
                    "rebooted": False,
                    "commands": commands,
                    "msg": "Device is still responsive after reboot command, reboot may not have been initiated",
                }
            except Exception:
                # Connection loss confirmed - device is rebooting
                return {
                    "changed": True,
                    "failed": False,
                    "rebooted": True,
                    "commands": commands,
                    "msg": "Device reboot initiated successfully",
                }

        except ConnectionError as e:
            # Connection error during initial command - unexpected
            self._module.fail_json(
                msg=f"Connection error while sending reboot command: {str(e)}",
                changed=False,
                failed=True,
                rebooted=False,
                commands=commands,
            )
        except Exception as e:
            # Other unexpected errors
            self._module.fail_json(
                msg=f"Failed to execute reboot command: {str(e)}",
                changed=False,
                failed=True,
                rebooted=False,
                commands=commands,
            )
