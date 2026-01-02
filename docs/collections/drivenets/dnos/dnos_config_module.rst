.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.21.0

.. Anchors

.. _ansible_collections.drivenets.dnos.dnos_config_module:

.. Anchors: short name for ansible.builtin

.. Title

drivenets.dnos.dnos_config module -- Manage DNOS configuration sections
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `drivenets.dnos collection <https://galaxy.ansible.com/ui/repo/published/drivenets/dnos/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install drivenets.dnos`.

    To use it in a playbook, specify: :code:`drivenets.dnos.dnos_config`.

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

- DriveNets DNOS configurations use a simple block indent file syntax for segmenting configuration into sections. This module provides an implementation for working with DNOS configuration sections in a deterministic way.

.. note::
    This module has a corresponding :ref:`action plugin <action_plugins>`.

.. Aliases

Aliases: config

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
        <div class="ansibleOptionAnchor" id="parameter-after"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-after:

      .. rst-class:: ansible-option-title

      **after**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-after" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Commands to append to the command stack after changes are made.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-backup"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-backup:

      .. rst-class:: ansible-option-title

      **backup**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-backup" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Create a backup of the current configuration.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-backup_options"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-backup_options:

      .. rst-class:: ansible-option-title

      **backup_options**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-backup_options" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Backup configuration options.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-backup_options/dir_path"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-backup_options/dir_path:

      .. rst-class:: ansible-option-title

      **dir_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-backup_options/dir_path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`path`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Backup directory path.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-backup_options/filename"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-backup_options/filename:

      .. rst-class:: ansible-option-title

      **filename**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-backup_options/filename" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Backup filename.


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-before"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-before:

      .. rst-class:: ansible-option-title

      **before**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-before" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Commands to push on the command stack before any change is made.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-cancel_pending_commit"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-cancel_pending_commit:

      .. rst-class:: ansible-option-title

      **cancel_pending_commit**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-cancel_pending_commit" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Cancel a pending :literal:`commit confirm` (triggers automatic rollback of the pending commit).


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-comment"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-comment:

      .. rst-class:: ansible-option-title

      **comment**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-comment" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Commit comment to record when committing.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-commit"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-commit:

      .. rst-class:: ansible-option-title

      **commit**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-commit" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      If true, commit configuration changes; if false, changes remain staged.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`false`
      - :ansible-option-choices-entry-default:`true` :ansible-option-choices-default-mark:`← (default)`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-confirm"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-confirm:

      .. rst-class:: ansible-option-title

      **confirm**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-confirm" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Commit confirm timeout in minutes.

      If :emphasis:`confirm=0`\ , perform a confirm commit without a timeout value (requires manual confirm).


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`0`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-confirm_commit"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-confirm_commit:

      .. rst-class:: ansible-option-title

      **confirm_commit**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-confirm_commit" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Confirm a previously issued :literal:`commit confirm` (i.e. finalize the pending commit).


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-defaults"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-defaults:

      .. rst-class:: ansible-option-title

      **defaults**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-defaults" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Whether to collect defaults when fetching running config (uses :literal:`show config all`\ ).


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-diff_against"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-diff_against:

      .. rst-class:: ansible-option-title

      **diff_against**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-diff_against" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Compare configuration against.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"startup"`
      - :ansible-option-choices-entry:`"intended"`
      - :ansible-option-choices-entry:`"running"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-force_commit"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-force_commit:

      .. rst-class:: ansible-option-title

      **force_commit**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-force_commit" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Force commit even if device indicates no changes (when supported).


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-intended_config"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-intended_config:

      .. rst-class:: ansible-option-title

      **intended_config**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-intended_config" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Master configuration used to validate final state (used with :emphasis:`diff\_against=intended`\ ).


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-lines"></div>
        <div class="ansibleOptionAnchor" id="parameter-commands"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-commands:
      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-lines:

      .. rst-class:: ansible-option-title

      **lines**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-lines" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-aliases:`aliases: commands`

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The ordered set of commands that should be configured in the section. The commands must be the exact same commands as found in the device config. Be sure to note the configuration command syntax as some commands are automatically modified by the device config parser.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-load"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-load:

      .. rst-class:: ansible-option-title

      **load**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-load" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Load configuration from a URL accessible to the device.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"merge"`
      - :ansible-option-choices-entry:`"override"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-match"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-match:

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

      How to compare the provided commands to the device config.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`"line"` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`"strict"`
      - :ansible-option-choices-entry:`"exact"`
      - :ansible-option-choices-entry:`"none"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-parents"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-parents:

      .. rst-class:: ansible-option-title

      **parents**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-parents" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The ordered set of parents that uniquely identify the section or hierarchy the commands should be checked against. If the parents argument is omitted, the commands are checked against the set of top level or global commands.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-replace"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-replace:

      .. rst-class:: ansible-option-title

      **replace**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-replace" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      How to perform configuration on the device.

      :emphasis:`line` replaces individual lines, :emphasis:`block` replaces configuration blocks, and :emphasis:`config` replaces the entire configuration using :emphasis:`src` or using a factory-default override if only :emphasis:`lines` are provided.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"line"`
      - :ansible-option-choices-entry:`"block"`
      - :ansible-option-choices-entry:`"config"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-rollback"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-rollback:

      .. rst-class:: ansible-option-title

      **rollback**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-rollback" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Roll back to the specified identifier. Use :literal:`0` for the most recent commit.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-rollback_version"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-rollback_version:

      .. rst-class:: ansible-option-title

      **rollback_version**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-rollback_version" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Explicit rollback version (preferred over :emphasis:`rollback`\ ).


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-running_config"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-running_config:

      .. rst-class:: ansible-option-title

      **running_config**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-running_config" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Running configuration for comparison.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-save"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-save:

      .. rst-class:: ansible-option-title

      **save**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-save" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Filename on the device to save configuration to (no directory separators).

      Executed prior to rollback if :emphasis:`commit=false`\ , useful for staging or testing.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-save_when"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-save_when:

      .. rst-class:: ansible-option-title

      **save_when**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-save_when" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Control when to copy running configuration to startup configuration.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"always"`
      - :ansible-option-choices-entry-default:`"never"` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`"modified"`
      - :ansible-option-choices-entry:`"changed"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-src"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-src:

      .. rst-class:: ansible-option-title

      **src**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-src" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`path`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Path to a file with configuration or a template rendered to configuration.

      Mutually exclusive with :emphasis:`lines` and :emphasis:`parents`.

      The path can be absolute on the controller or relative to the playbook/role.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-url"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-url:

      .. rst-class:: ansible-option-title

      **url**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-url" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      URL to load when using :emphasis:`load`.

      Should be visible in :literal:`show file config list`.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-use_candidate"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-use_candidate:

      .. rst-class:: ansible-option-title

      **use_candidate**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-use_candidate" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Hint to use candidate workflow when supported (auto-detected if not set).


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`false`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-validate_only"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__parameter-validate_only:

      .. rst-class:: ansible-option-title

      **validate_only**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-validate_only" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Validate configuration (apply → commit check → rollback), do not commit.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>


.. Attributes


.. Notes

Notes
-----

.. note::
   - Tested against DNOS 25.2.0
   - This module works with connection :literal:`network\_cli`.
   - This module also supports :literal:`netconf` connection for YANG model-based configuration.
   - DNOS uses a candidate configuration model. Configuration changes are applied to a candidate configuration and then committed.
   - When using NETCONF transport, the module automatically uses YANG models for configuration, when available.

.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

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
    - name: Check configuration against intended state
      drivenets.dnos.dnos_config:
        diff_against: intended
        intended_config: "{{ lookup('file', 'intended.cfg') }}"
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
        <div class="ansibleOptionAnchor" id="return-backup_path"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__return-backup_path:

      .. rst-class:: ansible-option-title

      **backup_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-backup_path" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The full path to the backup file.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when backup is yes

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"/playbooks/ansible/backup/dnos\_config.2016-07-16@22:28:34"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-commands"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__return-commands:

      .. rst-class:: ansible-option-title

      **commands**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-commands" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The set of commands that will be pushed to the remote device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`["interfaces ge100-0/0/1", "description test interface", "mtu 9000"]`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-updates"></div>

      .. _ansible_collections.drivenets.dnos.dnos_config_module__return-updates:

      .. rst-class:: ansible-option-title

      **updates**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-updates" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The set of commands that will be pushed to the remote device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`["interfaces ge100-0/0/1", "description test interface", "mtu 9000"]`


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
