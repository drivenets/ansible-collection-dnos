.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.21.0

.. Anchors

.. _ansible_collections.drivenets.dnos.dnos_reboot_module:

.. Anchors: short name for ansible.builtin

.. Title

drivenets.dnos.dnos_reboot module -- Reboot Drivenets DNOS devices
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `drivenets.dnos collection <https://galaxy.ansible.com/ui/repo/published/drivenets/dnos/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install drivenets.dnos`.

    To use it in a playbook, specify: :code:`drivenets.dnos.dnos_reboot`.

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

- This module provides the ability to reboot Drivenets DNOS network devices.
- The module sends a reboot command to the device and handles the confirmation prompt.
- After the reboot command is executed, the device will restart and the connection will be closed.


.. Aliases


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
        <div class="ansibleOptionAnchor" id="parameter-reboot"></div>

      .. _ansible_collections.drivenets.dnos.dnos_reboot_module__parameter-reboot:

      .. rst-class:: ansible-option-title

      **reboot**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-reboot" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      When set to :literal:`true`\ , the device will be rebooted.

      When set to :literal:`false`\ , no action is taken.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>


.. Attributes


Attributes
----------

.. tabularcolumns:: \X{2}{10}\X{3}{10}\X{5}{10}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Attribute
    - Support
    - Description

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="attribute-check_mode"></div>

      .. _ansible_collections.drivenets.dnos.dnos_reboot_module__attribute-check_mode:

      .. rst-class:: ansible-option-title

      **check_mode**

      .. raw:: html

        <a class="ansibleOptionLink" href="#attribute-check_mode" title="Permalink to this attribute"></a>

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      :ansible-attribute-support-label:`Support: \ `\ :ansible-attribute-support-full:`full`


      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      This module supports check mode.


      .. raw:: html

        </div>



.. Notes

Notes
-----

.. note::
   - Tested against DNOS 25.2.x
   - This module works with connection :literal:`network\_cli`.
   - The module will close the connection after sending the reboot command.
   - Use with caution as this will restart the target device.

.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    # Reboot the device
    - name: Reboot DNOS device
      drivenets.dnos.dnos_reboot:
        reboot: true

    # Check if reboot is needed (no action taken)
    - name: Check reboot status
      drivenets.dnos.dnos_reboot:
        reboot: false



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
        <div class="ansibleOptionAnchor" id="return-msg"></div>

      .. _ansible_collections.drivenets.dnos.dnos_reboot_module__return-msg:

      .. rst-class:: ansible-option-title

      **msg**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-msg" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Message describing the result.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"Device reboot initiated successfully"`


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
