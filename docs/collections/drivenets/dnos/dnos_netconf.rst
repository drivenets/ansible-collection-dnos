.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.21.0

.. Anchors

.. _ansible_collections.drivenets.dnos.dnos_netconf:

.. Anchors: short name for ansible.builtin

.. Title

drivenets.dnos.dnos netconf -- Use dnos netconf plugin to run NETCONF commands on DriveNets DNOS
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This netconf plugin is part of the `drivenets.dnos collection <https://galaxy.ansible.com/ui/repo/published/drivenets/dnos/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install drivenets.dnos`.

    To use it in a playbook, specify: :code:`drivenets.dnos.dnos`.

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

- This dnos plugin provides low level abstraction APIs for sending and receiving NETCONF commands from DriveNets DNOS network devices.
- Enhanced with comprehensive YANG model support for DNOS protocols.


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
        <div class="ansibleOptionAnchor" id="parameter-ncclient_device_handler"></div>

      .. _ansible_collections.drivenets.dnos.dnos_netconf__parameter-ncclient_device_handler:

      .. rst-class:: ansible-option-title

      **ncclient_device_handler**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-ncclient_device_handler" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`




      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Specifies the ncclient device handler name for DriveNets DNOS network OS.

      Refer to the ncclient documentation for valid device handlers.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"default"`

      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: Use DNOS netconf transport
      hosts: dnos_devices
      connection: ansible.netcommon.netconf
      vars:
        ansible_network_os: drivenets.dnos.dnos
      tasks:
        - name: Get device capabilities (example)
          ansible.builtin.debug:
            msg: "NETCONF session established"



.. Facts


.. Return values


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
