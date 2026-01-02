# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
DNOS NETCONF Plugin with Enhanced YANG Support

Logging Configuration:
- Set ANSIBLE_DEBUG=1 to enable console logging
- Set DNOS_NETCONF_LOG=/path/to/logfile to specify log file location (default: /tmp/dnos_netconf.log)
- Logs include function names, line numbers, and timestamps for debugging
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = r"""
---
author:
  - Abishek Suresh Kumar (@askumar-dn)
  - Gennady Mescheryakov (@gennadym-dn)
  - Dragos Lazar (@dlazar-dn)
name: dnos
short_description: Use dnos netconf plugin to run NETCONF commands on DriveNets DNOS
description:
  - This dnos plugin provides low level abstraction APIs for sending and receiving
    NETCONF commands from DriveNets DNOS network devices.
  - Enhanced with comprehensive YANG model support for DNOS protocols.
version_added: "1.0.0"
options:
  ncclient_device_handler:
    type: str
    default: default
    description:
      - Specifies the ncclient device handler name for DriveNets DNOS network OS.
      - Refer to the ncclient documentation for valid device handlers.
"""
EXAMPLES = r"""
- name: Use DNOS netconf transport
  hosts: dnos_devices
  connection: ansible.netcommon.netconf
  vars:
    ansible_network_os: drivenets.dnos.dnos
  tasks:
    - name: Get device capabilities (example)
      ansible.builtin.debug:
        msg: "NETCONF session established"
"""

import json
import logging
import os
import re

from xml.etree import ElementTree as ET

from ansible.module_utils._text import to_native, to_text
from ansible.plugins.netconf import NetconfBase
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.netconf import (
    remove_namespaces,
)


try:
    from ncclient.operations import RPCError
    from ncclient.xml_ import to_xml

    HAS_NCCLIENT = True
except (
    ImportError,
    AttributeError,
):  # paramiko and gssapi are incompatible and raise AttributeError not ImportError
    HAS_NCCLIENT = False


# Custom logger setup for DNOS NETCONF plugin
def _setup_logger():
    """Setup custom logger for DNOS NETCONF plugin"""
    logger = logging.getLogger("dnos_netconf")

    # Only setup if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create console handler with a higher log level if ANSIBLE_DEBUG is set
        if os.environ.get("ANSIBLE_DEBUG", "").lower() in ("true", "1", "yes"):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "[%(asctime)s] %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Create file handler for persistent logging
        try:
            log_file = os.environ.get("DNOS_NETCONF_LOG", "/tmp/dnos_netconf.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "[%(asctime)s] %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError):
            # If file logging fails, continue without it
            pass

    return logger


# Initialize logger
_logger = _setup_logger()

# Constants
DNOS_RPC_NAMESPACE = "http://drivenets.com/ns/yang/dn-rpc"
SHOW_SYSTEM_RPC = "show-system"


class Netconf(NetconfBase):
    def get_capabilities(self):
        result = dict()
        result["rpc"] = self.get_base_rpc() + [
            "commit",
            "discard-changes",
            "validate",
            "lock",
            "unlock",
            "rollback",
        ]
        result["network_api"] = "netconf"
        result["device_info"] = self.get_device_info()
        result["server_capabilities"] = list(self.m.server_capabilities)
        result["client_capabilities"] = list(self.m.client_capabilities)
        result["session_id"] = self.m.session_id
        result["device_operations"] = self.get_device_operations(
            result["server_capabilities"],
        )
        _logger.debug("Device operations: %s", result["device_operations"])
        return json.dumps(result)

    def get_device_info(self):
        """
        Retrieve device information by executing the show-system RPC.

        Parses the response to extract:
        - network_os_hostname: System Name
        - network_os_version: DNOS version
        - network_os_model: System Type

        :return: Dictionary containing device information
        """
        device_info = dict()
        device_info["network_os"] = "dnos"
        _logger.info("Getting device info")

        try:
            # Build the show-system RPC request as an Element
            rpc_request = ET.Element(SHOW_SYSTEM_RPC)
            rpc_request.set("xmlns", DNOS_RPC_NAMESPACE)

            # Convert Element to XML string
            rpc_xml_string = ET.tostring(rpc_request, encoding="unicode")
            _logger.debug("RPC request XML: %s", rpc_xml_string)
            _logger.debug("RPC request type: %s", type(rpc_request))

            # Execute the RPC using dispatch with XML string
            _logger.debug("Executing %s RPC", SHOW_SYSTEM_RPC)
            try:
                # Try using to_ele to convert string to proper format
                from ncclient.xml_ import to_ele

                rpc_element = to_ele(rpc_xml_string)
                _logger.debug("Converted to_ele type: %s", type(rpc_element))
                response = self.m.dispatch(rpc_element)
            except Exception as dispatch_error:
                _logger.error("Dispatch error: %s", to_native(dispatch_error))
                raise

            _logger.debug("Response type: %s", type(response))
            _logger.debug(
                "Response XML length: %d", len(response.xml) if hasattr(response, "xml") else 0
            )

            # Parse the XML response
            response_xml = ET.fromstring(response.xml)

            # Find the result element (contains the show system output)
            result_elem = response_xml.find(f".//{{{DNOS_RPC_NAMESPACE}}}result")

            if result_elem is not None and result_elem.text:
                output_text = result_elem.text
                _logger.debug("Received show-system output: %s", output_text[:200])

                # Parse hostname from "System Name: cdnos1, System-Id: ..."
                hostname_match = re.search(r"System Name:\s+(\S+)", output_text, re.MULTILINE)
                if hostname_match:
                    device_info["network_os_hostname"] = hostname_match.group(1).strip(",")
                    _logger.debug("Extracted hostname: %s", device_info["network_os_hostname"])

                # Parse version from "Version: DNOS [25.2.0] build [500_dev], ..."
                version_match = re.search(
                    r"Version:\s+DNOS\s+\[([^\]]+)\]", output_text, re.MULTILINE
                )
                if version_match:
                    device_info["network_os_version"] = version_match.group(1)
                    _logger.debug("Extracted version: %s", device_info["network_os_version"])

                # Parse model from "System Type: SA-VR, Family: NCR"
                model_match = re.search(r"System Type:\s+([^,\n]+)", output_text, re.MULTILINE)
                if model_match:
                    device_info["network_os_model"] = model_match.group(1).strip()
                    _logger.debug("Extracted model: %s", device_info["network_os_model"])
            else:
                _logger.warning("No result element found in show-system response")
            _logger.debug("Device info: %s", device_info)

        except Exception as exc:
            _logger.error("Failed to retrieve device info: %s", to_native(exc))
            # Set default values if RPC fails
            device_info["network_os_version"] = "unknown"
            device_info["network_os_hostname"] = "unknown"
            device_info["network_os_model"] = "unknown"
            _logger.debug("Device info: %s", device_info)

        return device_info

    def get_config(self, source=None, filter=None):
        """
        Retrieve all or part of a specified configuration
        (by default entire configuration is retrieved).
        :param source: Name of the configuration datastore being queried, defaults to running datastore
        :param filter: This argument specifies the portion of the configuration data to retrieve
        :return: Returns xml string containing the RPC response received from remote host
        """
        if isinstance(filter, list):
            filter = tuple(filter)

        if not source:
            source = "running"
        _logger.debug("Getting config from source '%s' with filter: %s", source, filter)
        resp = self.m.get_config(source=source, filter=filter)
        return resp.xml

    def get(self, filter=None, with_defaults=None):
        """
        Retrieve device configuration and state information.
        :param filter: This argument specifies the portion of the state data to retrieve
                       (by default entire state data is retrieved)
        :param with_defaults: defines an explicit method of retrieving default values
                              from the configuration
        :return: Returns xml string containing the RPC response received from remote host
        """
        if isinstance(filter, list):
            filter = tuple(filter)
        _logger.debug("Getting data with filter: %s, with_defaults: %s", filter, with_defaults)
        resp = self.m.get(filter=filter, with_defaults=with_defaults)
        return resp.xml

    def get_device_operations(self, server_capabilities):
        """Returns a dict of supported operations"""
        operations = {
            "supports_commit": True,
            "supports_rollback": True,
            "supports_defaults": True,
            "supports_commit_label": False,
            "supports_commit_confirmed": True,
            "supports_confirm_commit": True,
            "supports_startup": False,
            "supports_xpath": True,
            "supports_writable_running": False,
            "supports_validate": True,
            "supports_lock": False,
            "supports_unlock": False,
            "supports_candidate": True,
            "supports_commit_comment": False,
            "supports_discard_changes": True,
            "supports_yang": True,
            "supports_yang_library": True,
        }

        return operations

    def edit_config(
        self,
        config=None,
        format="xml",
        target="candidate",
        default_operation=None,
        test_option=None,
        error_option=None,
    ):
        """Loads the configuration on DNOS device"""
        if config is None:
            raise ValueError("config must be provided")
        if format != "xml":
            # Convert to XML if needed
            config = to_xml(config)
        kwargs = {
            "target": target,
            "config": config,
        }
        if default_operation is not None:
            kwargs["default_operation"] = default_operation
        if test_option is not None:
            kwargs["test_option"] = test_option
        # Only rollback-on-error is supported by DNOS
        if error_option == "rollback-on-error":
            kwargs["error_option"] = error_option

        return self.m.edit_config(**kwargs).xml

    def commit(
        self,
        confirmed=False,
        timeout=None,
        persist=None,
        remove_ns=False,
    ):
        try:
            _logger.debug(
                "Commit request: %s with timeout %s and persist %s", confirmed, timeout, persist
            )
            timeout = to_text(timeout, errors="surrogate_or_strict")
            resp = self.m.commit(
                confirmed=confirmed,
                timeout=timeout,
                persist=persist,
            )

            if remove_ns:
                response = remove_namespaces(resp)
            else:
                response = resp.data_xml if hasattr(resp, "data_xml") else resp.xml
            _logger.debug("Response: %s", response)
            return response
        except RPCError as exc:
            raise Exception(to_xml(exc.xml))

    def reboot(self):
        """reboot the device"""
        return self.m.reboot().data_xml
