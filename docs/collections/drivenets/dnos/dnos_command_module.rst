.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.21.0

.. Anchors

.. _ansible_collections.drivenets.dnos.dnos_command_module:

.. Anchors: short name for ansible.builtin

.. Title

drivenets.dnos.dnos_command module -- Run commands on remote DNOS devices
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `drivenets.dnos collection <https://galaxy.ansible.com/ui/repo/published/drivenets/dnos/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install drivenets.dnos`.

    To use it in a playbook, specify: :code:`drivenets.dnos.dnos_command`.

.. version_added

.. rst-class:: ansible-version-added

New in drivenets.dnos 1.0.0

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- Sends arbitrary commands to a DriveNets DNOS device and returns the results read from the device. This module includes an argument that will cause the module to wait for a specific condition before returning or timing out if the condition is not met.
- This module does not support running commands in configuration mode. Please use :ref:`drivenets.dnos.dnos\_config <ansible_collections.drivenets.dnos.dnos_config_module>` to configure DNOS devices.
- This module only supports CLI command execution and does not support NETCONF. For device configuration using NETCONF, use other DNOS configuration modules.

.. note::
    This module has a corresponding :ref:`action plugin <action_plugins>`.

.. Aliases

Aliases: command

.. Requirements






.. Options

Parameters
----------

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Parameter
    - Comments

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-cli_timestamp"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__parameter-cli_timestamp:

      .. rst-class:: ansible-option-title

      **cli_timestamp**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-cli_timestamp" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Controls whether to enable CLI timestamp for this command session.

      When set to :literal:`true`\ , executes 'set cli-timestamp' before running commands.

      When set to :literal:`false`\ , executes 'unset cli-timestamp' before running commands.

      When set to :literal:`none` (default), does not modify the timestamp setting.

      This is a session-level setting that overrides the system configuration.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`false`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-commands"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__parameter-commands:

      .. rst-class:: ansible-option-title

      **commands**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-commands" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=any` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of commands to send to the remote DNOS device over the configured provider. The resulting output from the command is returned. If the :emphasis:`wait\_for` argument is provided, the module is not returned until the condition is satisfied or the number of retries has expired.

      The :emphasis:`commands` module argument accepts formatting options that allow the user to pass arguments to the command.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-interval"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__parameter-interval:

      .. rst-class:: ansible-option-title

      **interval**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-interval" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Configures the interval in seconds to wait between retries of the command. If the command does not pass the specified conditions, the interval indicates how long to wait before trying the command again.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`1`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-match"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__parameter-match:

      .. rst-class:: ansible-option-title

      **match**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-match" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The :emphasis:`match` argument is used in conjunction with the :emphasis:`wait\_for` argument to specify the match policy. Valid values are :literal:`all` or :literal:`any`. If the value is set to :literal:`all` then all conditionals in the wait\_for must be satisfied. If the value is set to :literal:`any` then only one of the values must be satisfied.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"any"`
      - :ansible-option-choices-entry-default:`"all"` :ansible-option-choices-default-mark:`← (default)`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-retries"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__parameter-retries:

      .. rst-class:: ansible-option-title

      **retries**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-retries" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Specifies the number of retries a command should by tried before it is considered failed. The command is run on the target device every retry and evaluated against the :emphasis:`wait\_for` conditions.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`10`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-wait_for"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__parameter-wait_for:

      .. rst-class:: ansible-option-title

      **wait_for**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-wait_for" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of conditions to evaluate against the output of the command. The task will wait for each condition to be true before moving forward. If the conditional is not true within the configured number of :emphasis:`retries`\ , the task fails. See examples.


      .. raw:: html

        </div>


.. Attributes


.. Notes

Notes
-----

.. note::
   - Tested against DNOS 25.2.0
   - This module works with connection :literal:`network\_cli`.
   - This module is designed for operational command execution and information gathering

.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

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



.. Facts


.. Return values

Return Values
-------------
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this module:

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Key
    - Description

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-failed_conditions"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__return-failed_conditions:

      .. rst-class:: ansible-option-title

      **failed_conditions**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-failed_conditions" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The list of conditionals that have failed


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` failed

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`["result[0] contains \\"BGP state: Established\\"", "result[1] contains \\"Operational State: Up\\""]`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-stdout"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__return-stdout:

      .. rst-class:: ansible-option-title

      **stdout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-stdout" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The set of responses from the commands


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always apart from low level errors (such as action plugin)

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`["[\\n  \\"System Name: DN-SA-06\\\\nVersion: DNOS [25.2.0] build [411]\\"", "\\n  \\"System Name: DN-SA-06\\\\nCurrent Time: 26-Aug-2025 00:15:30 UTC\\\\nSystem Uptime: 24 days", " 12:15:30\\"\\n]\\n"]`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-stdout_lines"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__return-stdout_lines:

      .. rst-class:: ansible-option-title

      **stdout_lines**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-stdout_lines" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The value of stdout split into a list


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always apart from low level errors (such as action plugin)

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`["[\\n  [\\n    \\"System Name: DN-SA-06\\"", "\\n    \\"Version: DNOS [25.2.0] build [411]\\"\\n  ]", "\\n  [\\n    \\"System Name: DN-SA-06\\"", "\\n    \\"Current Time: 26-Aug-2025 00:15:30 UTC\\"", "\\n    \\"System Uptime: 24 days", " 12:15:30\\"\\n  ]\\n]\\n"]`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-warnings"></div>

      .. _ansible_collections.drivenets.dnos.dnos_command_module__return-warnings:

      .. rst-class:: ansible-option-title

      **warnings**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-warnings" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of warnings if any


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when warnings are present

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`["CLI timestamp enabled for session", "Command execution completed with timestamps"]`


      .. raw:: html

        </div>



..  Status (Presently only deprecated)


.. Authors

Authors
~~~~~~~

- Ansible Drivenets Team (@drivenets)


.. Extra links

Collection links
~~~~~~~~~~~~~~~~

.. ansible-links::

  - title: "Issue Tracker"
    url: "https://github.com/ansible-collections/drivenets.dnos/issues"
    external: true
  - title: "Repository (Sources)"
    url: "https://github.com/ansible-collections/drivenets.dnos"
    external: true


.. Parsing errors
