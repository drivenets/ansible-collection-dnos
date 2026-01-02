.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.21.0

.. Anchors

.. _ansible_collections.drivenets.dnos.dnos_cliconf:

.. Anchors: short name for ansible.builtin

.. Title

drivenets.dnos.dnos cliconf -- Use dnos cliconf to run command on DNOS platform
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This cliconf plugin is part of the `drivenets.dnos collection <https://galaxy.ansible.com/ui/repo/published/drivenets/dnos/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install drivenets.dnos`.

    To use it in a playbook, specify: :code:`drivenets.dnos.dnos`.

.. version_added

.. rst-class:: ansible-version-added

New in drivenets.dnos 0.1.0

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- This dnos plugin provides low level abstraction APIs for sending and receiving CLI commands from DNOS network devices.


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
        <div class="ansibleOptionAnchor" id="parameter-config_commands"></div>

      .. _ansible_collections.drivenets.dnos.dnos_cliconf__parameter-config_commands:

      .. rst-class:: ansible-option-title

      **config_commands**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-config_commands" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      :ansible-option-versionadded:`added in drivenets.dnos 0.1.0`





      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Specifies a list of commands that can make configuration changes to the target device.

      When :literal:`ansible\_network\_single\_user\_mode` is enabled, if a command sent to the device is present in this list, the existing cache is invalidated.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`[]`

      .. rst-class:: ansible-option-line

      :ansible-option-configuration:`Configuration:`

      - Variable: ansible\_dnos\_config\_commands


      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples



.. Facts


.. Return values


..  Status (Presently only deprecated)


.. Authors


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
