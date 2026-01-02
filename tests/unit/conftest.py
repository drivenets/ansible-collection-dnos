"""
DNOS Test Isolation Configuration
Helps reduce test pollution by cleaning up state between tests
"""

import os
import sys

from unittest.mock import patch

import pytest


# Ensure Ansible collections path is available during test collection
collection_root = os.path.expanduser("~/.ansible/collections")
if collection_root not in sys.path:
    sys.path.insert(0, collection_root)


@pytest.fixture(autouse=True)
def dnos_test_isolation():
    """Automatic test cleanup to reduce test pollution"""
    yield

    # Post-test cleanup to reduce pollution
    try:
        # Stop any lingering patches
        patch.stopall()
    except BaseException:
        pass


def pytest_configure(config):
    """Configure DNOS test environment"""
    config.addinivalue_line("markers", "dnos: DNOS module tests")
