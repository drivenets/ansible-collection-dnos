# -*- coding: utf-8 -*-
# Copyright 2025 Drivenets
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
Error handling constants and utilities for DNOS modules.

This module provides standardized error messages and error handling patterns
to ensure consistent behavior across all DNOS modules, particularly for
integration with Ansible core error-handling directives like ignore_errors
and any_errors_fatal.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type

# =============================================================================
# CONNECTION ERROR MESSAGES
# =============================================================================

CONNECTION_ERROR_MSG = "Failed to connect to DNOS device"
CONNECTION_LOST_MSG = "Connection to DNOS device was lost"
CONNECTION_TIMEOUT_MSG = "Connection to DNOS device timed out"
CONNECTION_REFUSED_MSG = "Connection to DNOS device was refused"
CONNECTION_AUTH_FAILED_MSG = "Authentication to DNOS device failed"
CONNECTION_CLOSED_MSG = "Connection to DNOS device was closed unexpectedly"

# =============================================================================
# CONFIGURATION ERROR MESSAGES
# =============================================================================

CONFIGURATION_ERROR_MSG = "Configuration operation failed"
CONFIGURATION_SYNTAX_ERROR_MSG = "Configuration contains syntax errors"
CONFIGURATION_COMMIT_FAILED_MSG = "Failed to commit configuration changes"
CONFIGURATION_ROLLBACK_FAILED_MSG = "Failed to rollback configuration"
CONFIGURATION_VALIDATION_FAILED_MSG = "Configuration validation failed"
CONFIGURATION_LOCKED_MSG = "Configuration is locked by another session"
CONFIGURATION_CONFLICT_MSG = "Configuration conflict detected"
CONFIGURATION_TIMEOUT_MSG = "Configuration operation timed out"
CONFIGURATION_INCOMPLETE_MSG = "Configuration changes incomplete"

# =============================================================================
# COMMAND EXECUTION ERROR MESSAGES
# =============================================================================

COMMAND_EXECUTION_ERROR_MSG = "Command execution failed"
COMMAND_SYNTAX_ERROR_MSG = "Command contains syntax errors"
COMMAND_NOT_FOUND_MSG = "Command not found on device"
COMMAND_TIMEOUT_MSG = "Command execution timed out"
COMMAND_PERMISSION_DENIED_MSG = "Permission denied for command execution"
COMMAND_INVALID_MODE_MSG = "Command cannot be executed in current mode"

# =============================================================================
# VALIDATION ERROR MESSAGES
# =============================================================================

VALIDATION_ERROR_MSG = "Validation failed"
VALIDATION_PARAMETER_MISSING_MSG = "Required parameter missing"
VALIDATION_PARAMETER_INVALID_MSG = "Invalid parameter value"
VALIDATION_MUTUALLY_EXCLUSIVE_MSG = "Mutually exclusive parameters specified"
VALIDATION_CONDITIONAL_FAILED_MSG = "Conditional validation failed"

# =============================================================================
# DEVICE CAPABILITY ERROR MESSAGES
# =============================================================================

CAPABILITY_ERROR_MSG = "Device capability check failed"
CAPABILITY_NOT_SUPPORTED_MSG = "Operation not supported by device"
CAPABILITY_DETECTION_FAILED_MSG = "Failed to detect device capabilities"
NETCONF_NOT_AVAILABLE_MSG = "NETCONF is not available on this device"
CLI_NOT_AVAILABLE_MSG = "CLI is not available on this device"

# =============================================================================
# TIMEOUT ERROR MESSAGES
# =============================================================================

TIMEOUT_ERROR_MSG = "Operation timed out"
TIMEOUT_WAITING_FOR_RESPONSE_MSG = "Timed out waiting for device response"
TIMEOUT_WAITING_FOR_CONDITION_MSG = "Timed out waiting for condition"
TIMEOUT_WAITING_FOR_COMMIT_MSG = "Timed out waiting for commit confirmation"

# =============================================================================
# DEVICE STATE ERROR MESSAGES
# =============================================================================

DEVICE_STATE_ERROR_MSG = "Device state error"
DEVICE_BUSY_MSG = "Device is busy, please retry"
DEVICE_RELOADING_MSG = "Device is reloading"
DEVICE_UNRESPONSIVE_MSG = "Device is unresponsive"
DEVICE_MAINTENANCE_MODE_MSG = "Device is in maintenance mode"

# =============================================================================
# FILE OPERATION ERROR MESSAGES
# =============================================================================

FILE_ERROR_MSG = "File operation failed"
FILE_NOT_FOUND_MSG = "Configuration file not found"
FILE_READ_ERROR_MSG = "Failed to read configuration file"
FILE_WRITE_ERROR_MSG = "Failed to write configuration file"
FILE_PERMISSION_ERROR_MSG = "Permission denied for file operation"
FILE_INVALID_FORMAT_MSG = "Invalid file format"

# =============================================================================
# BACKUP/RESTORE ERROR MESSAGES
# =============================================================================

BACKUP_ERROR_MSG = "Backup operation failed"
BACKUP_CREATE_FAILED_MSG = "Failed to create configuration backup"
BACKUP_PATH_INVALID_MSG = "Invalid backup directory path"
RESTORE_ERROR_MSG = "Restore operation failed"
RESTORE_FILE_INVALID_MSG = "Invalid backup file for restore"

# =============================================================================
# NETCONF SPECIFIC ERROR MESSAGES
# =============================================================================

NETCONF_ERROR_MSG = "NETCONF operation failed"
NETCONF_LOCK_FAILED_MSG = "Failed to lock NETCONF candidate configuration"
NETCONF_UNLOCK_FAILED_MSG = "Failed to unlock NETCONF candidate configuration"
NETCONF_DISCARD_FAILED_MSG = "Failed to discard NETCONF candidate changes"
NETCONF_GET_CONFIG_FAILED_MSG = "Failed to get configuration via NETCONF"
NETCONF_EDIT_CONFIG_FAILED_MSG = "Failed to edit configuration via NETCONF"
NETCONF_RPC_FAILED_MSG = "NETCONF RPC operation failed"
NETCONF_SESSION_ERROR_MSG = "NETCONF session error"

# =============================================================================
# CLI SPECIFIC ERROR MESSAGES
# =============================================================================

CLI_ERROR_MSG = "CLI operation failed"
CLI_MODE_ERROR_MSG = "Failed to enter/exit CLI mode"
CLI_CONFIG_MODE_ERROR_MSG = "Failed to enter configuration mode"
CLI_EXEC_MODE_ERROR_MSG = "Failed to enter exec mode"
CLI_PROMPT_DETECTION_FAILED_MSG = "Failed to detect CLI prompt"
CLI_COMMAND_OUTPUT_ERROR_MSG = "Failed to capture CLI command output"

# =============================================================================
# RETRY AND RECOVERY ERROR MESSAGES
# =============================================================================

RETRY_EXHAUSTED_MSG = "Operation failed after maximum retry attempts"
RECOVERY_FAILED_MSG = "Failed to recover from error condition"
CLEANUP_FAILED_MSG = "Failed to cleanup after error"

# =============================================================================
# GENERAL ERROR MESSAGES
# =============================================================================

UNEXPECTED_ERROR_MSG = "An unexpected error occurred"
OPERATION_FAILED_MSG = "Operation failed"
INVALID_STATE_MSG = "Invalid module state"
NOT_IMPLEMENTED_MSG = "Feature not implemented"
INTERNAL_ERROR_MSG = "Internal module error"

# =============================================================================
# ERROR HANDLING UTILITIES
# =============================================================================


def format_error_message(base_message, details=None, device=None, operation=None):
    """
    Format a standardized error message with additional context.

    Args:
        base_message (str): Base error message constant
        details (str, optional): Additional error details
        device (str, optional): Device identifier
        operation (str, optional): Operation being performed

    Returns:
        str: Formatted error message

    Example:
        >>> format_error_message(
        ...     CONNECTION_ERROR_MSG,
        ...     details="Connection refused",
        ...     device="router1",
        ...     operation="get_config"
        ... )
        'Failed to connect to DNOS device: Connection refused (device: router1, operation: get_config)'
    """
    message_parts = [base_message]

    if details:
        message_parts.append(f": {details}")

    context_parts = []
    if device:
        context_parts.append(f"device: {device}")
    if operation:
        context_parts.append(f"operation: {operation}")

    if context_parts:
        message_parts.append(f" ({', '.join(context_parts)})")

    return "".join(message_parts)


def get_error_context(exception):
    """
    Extract context information from an exception.

    Args:
        exception: The exception object

    Returns:
        dict: Dictionary containing error context
    """
    context = {
        "error_type": type(exception).__name__,
        "error_message": str(exception),
    }

    # Extract additional context from common exception types
    if hasattr(exception, "errno"):
        context["error_code"] = exception.errno

    if hasattr(exception, "strerror"):
        context["system_error"] = exception.strerror

    return context


class DNOSErrorCategory:
    """
    Error categories for DNOS modules to help with error classification
    and handling.
    """

    CONNECTION = "connection"
    CONFIGURATION = "configuration"
    COMMAND = "command"
    VALIDATION = "validation"
    CAPABILITY = "capability"
    TIMEOUT = "timeout"
    DEVICE_STATE = "device_state"
    FILE_OPERATION = "file_operation"
    BACKUP_RESTORE = "backup_restore"
    NETCONF = "netconf"
    CLI = "cli"
    RETRY_RECOVERY = "retry_recovery"
    GENERAL = "general"


# =============================================================================
# ERROR SEVERITY LEVELS
# =============================================================================


class DNOSErrorSeverity:
    """
    Error severity levels to help prioritize error handling and logging.
    """

    CRITICAL = "critical"  # System-level failures requiring immediate attention
    HIGH = "high"  # Significant failures affecting operation
    MEDIUM = "medium"  # Recoverable errors with workarounds
    LOW = "low"  # Minor issues with minimal impact
    INFO = "info"  # Informational, not actual errors


# =============================================================================
# ERROR CODE MAPPINGS
# =============================================================================

# HTTP-style error codes for NETCONF/RESTCONF operations
NETCONF_ERROR_CODES = {
    "in-use": NETCONF_LOCK_FAILED_MSG,
    "invalid-value": CONFIGURATION_SYNTAX_ERROR_MSG,
    "too-big": "Configuration too large",
    "missing-attribute": VALIDATION_PARAMETER_MISSING_MSG,
    "bad-attribute": VALIDATION_PARAMETER_INVALID_MSG,
    "unknown-attribute": VALIDATION_PARAMETER_INVALID_MSG,
    "missing-element": VALIDATION_PARAMETER_MISSING_MSG,
    "bad-element": VALIDATION_PARAMETER_INVALID_MSG,
    "unknown-element": VALIDATION_PARAMETER_INVALID_MSG,
    "unknown-namespace": "Unknown XML namespace",
    "access-denied": COMMAND_PERMISSION_DENIED_MSG,
    "lock-denied": NETCONF_LOCK_FAILED_MSG,
    "resource-denied": DEVICE_BUSY_MSG,
    "rollback-failed": CONFIGURATION_ROLLBACK_FAILED_MSG,
    "data-exists": CONFIGURATION_CONFLICT_MSG,
    "data-missing": "Required configuration data missing",
    "operation-not-supported": CAPABILITY_NOT_SUPPORTED_MSG,
    "operation-failed": OPERATION_FAILED_MSG,
    "partial-operation": CONFIGURATION_INCOMPLETE_MSG,
}

# CLI error pattern mappings
CLI_ERROR_PATTERNS = {
    "syntax error": COMMAND_SYNTAX_ERROR_MSG,
    "invalid": VALIDATION_PARAMETER_INVALID_MSG,
    "permission denied": COMMAND_PERMISSION_DENIED_MSG,
    "not found": COMMAND_NOT_FOUND_MSG,
    "timeout": TIMEOUT_ERROR_MSG,
    "connection refused": CONNECTION_REFUSED_MSG,
    "connection closed": CONNECTION_CLOSED_MSG,
    "authentication failed": CONNECTION_AUTH_FAILED_MSG,
    "locked": CONFIGURATION_LOCKED_MSG,
    "conflict": CONFIGURATION_CONFLICT_MSG,
    "busy": DEVICE_BUSY_MSG,
    "unresponsive": DEVICE_UNRESPONSIVE_MSG,
}


def get_error_message_for_pattern(error_output):
    """
    Match error output against known patterns and return appropriate message.

    Args:
        error_output (str): Error output from device

    Returns:
        str: Standardized error message or original output if no match
    """
    if not error_output:
        return UNEXPECTED_ERROR_MSG

    error_lower = error_output.lower()

    for pattern, message in CLI_ERROR_PATTERNS.items():
        if pattern in error_lower:
            return message

    return error_output
