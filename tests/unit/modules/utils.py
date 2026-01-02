from __future__ import absolute_import, division, print_function


__metaclass__ = type
import json

from unittest import TestCase
from unittest.mock import patch

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


cur_context = None


def set_module_args(args):
    # Add common defaults
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = "/tmp"
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    # Clean up any previous context manager if it exists
    if cur_context is not None:
        try:
            cur_context.__exit__(None, None, None)
        except Exception:
            pass

    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


class ModuleTestCase(TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
        )
        self.mock_module_helper.start()
        # Add patch method to mock_module_helper for compatibility
        self.mock_module_helper.patch = patch
        # set module default args
        set_module_args({})

    def tearDown(self):
        global cur_context
        self.mock_module_helper.stop()
        # Clean up any previous context manager if it exists
        if cur_context is not None:
            try:
                cur_context.__exit__(None, None, None)
            except Exception:
                pass
            cur_context = None

    def execute_module(self, changed=False, failed=False, commands=None, exit_json=True):
        """Execute the module with exception handling"""
        if failed:
            result = self.failed()
            self.assertTrue(result["failed"], result)
        else:
            result = self.changed(changed)
            self.assertEqual(result["changed"], changed, result)
            if commands is not None:
                if "commands" in result:
                    self.assertEqual(
                        result["commands"],
                        commands,
                        f"Commands mismatch: expected {commands}, got {result.get('commands')}",
                    )
                else:
                    self.assertEqual([], commands, f"Expected no commands but got {commands}")
        return result

    def failed(self):
        """Handle module failure"""
        with self.assertRaises(AnsibleFailJson) as exc:
            self.module.main()
        result = exc.exception.args[0]
        return result

    def changed(self, changed=False):
        """Handle module success"""
        with self.assertRaises(AnsibleExitJson) as exc:
            self.module.main()
        result = exc.exception.args[0]
        return result
