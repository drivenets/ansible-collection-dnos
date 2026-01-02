.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.21.0

.. Anchors

.. _ansible_collections.drivenets.dnos.dnos_facts_module:

.. Anchors: short name for ansible.builtin

.. Title

drivenets.dnos.dnos_facts module -- Get facts about dnos devices
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `drivenets.dnos collection <https://galaxy.ansible.com/ui/repo/published/drivenets/dnos/>`_ (version 1.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install drivenets.dnos`.

    To use it in a playbook, specify: :code:`drivenets.dnos.dnos_facts`.

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

- Collects facts from network devices running the dnos operating system. This module places the facts gathered in the fact tree keyed by the respective resource name. The facts module will always collect a base set of facts from the device and can enable or disable collection of additional facts.

.. note::
    This module has a corresponding :ref:`action plugin <action_plugins>`.

.. Aliases

Aliases: facts

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
        <div class="ansibleOptionAnchor" id="parameter-gather_network_resources"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__parameter-gather_network_resources:

      .. rst-class:: ansible-option-title

      **gather_network_resources**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-gather_network_resources" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      When supplied, this argument will restrict the facts collected to a given subset. Possible values for this argument include all and the resources like interfaces, vlans etc. Can specify a list of values to include a larger subset. Values can also be used with an initial :literal:`M(!`\ ) to specify that a specific subset should not be collected.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-gather_subset"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__parameter-gather_subset:

      .. rst-class:: ansible-option-title

      **gather_subset**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-gather_subset" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      When supplied, this argument will restrict the facts collected to a given subset. Possible values for this argument include all, hardware, config, and interfaces. Can specify a list of values to include a larger subset. Values can also be used with an initial :literal:`M(!`\ ) to specify that a specific subset should not be collected.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"all"`
      - :ansible-option-choices-entry:`"min"`
      - :ansible-option-choices-entry:`"default"`
      - :ansible-option-choices-entry:`"hardware"`
      - :ansible-option-choices-entry:`"config"`
      - :ansible-option-choices-entry:`"interfaces"`
      - :ansible-option-choices-entry:`"!all"`
      - :ansible-option-choices-entry:`"!min"`
      - :ansible-option-choices-entry:`"!default"`
      - :ansible-option-choices-entry:`"!hardware"`
      - :ansible-option-choices-entry-default:`"!config"` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`"!interfaces"`


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`["!config"]`

      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: Gather all facts
      drivenets.dnos.dnos_facts:
        gather_subset: all
        gather_network_resources: all

    - name: Collect only the config and default facts
      drivenets.dnos.dnos_facts:
        gather_subset:
          - config

    - name: Do not collect hardware facts
      drivenets.dnos.dnos_facts:
        gather_subset:
          - "!hardware"



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
        <div class="ansibleOptionAnchor" id="return-ansible_net_all_ipv4_addresses"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_all_ipv4_addresses:

      .. rst-class:: ansible-option-title

      **ansible_net_all_ipv4_addresses**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_all_ipv4_addresses" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      All IPv4 addresses configured on the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when interfaces is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_all_ipv6_addresses"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_all_ipv6_addresses:

      .. rst-class:: ansible-option-title

      **ansible_net_all_ipv6_addresses**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_all_ipv6_addresses" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      All IPv6 addresses configured on the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when interfaces is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_config"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_config:

      .. rst-class:: ansible-option-title

      **ansible_net_config**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_config" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The current active config from the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when config is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_filesystems"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_filesystems:

      .. rst-class:: ansible-option-title

      **ansible_net_filesystems**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_filesystems" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      All file system names available on the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when hardware is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_gather_subset"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_gather_subset:

      .. rst-class:: ansible-option-title

      **ansible_net_gather_subset**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_gather_subset" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The list of fact subsets collected from the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_hostname"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_hostname:

      .. rst-class:: ansible-option-title

      **ansible_net_hostname**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_hostname" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The configured hostname of the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_interfaces"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_interfaces:

      .. rst-class:: ansible-option-title

      **ansible_net_interfaces**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_interfaces" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      A dictionary of all interfaces running on the system.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when interfaces is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_memfree_mb"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_memfree_mb:

      .. rst-class:: ansible-option-title

      **ansible_net_memfree_mb**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_memfree_mb" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The available free memory on the remote device in Mb.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when hardware is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_memtotal_mb"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_memtotal_mb:

      .. rst-class:: ansible-option-title

      **ansible_net_memtotal_mb**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_memtotal_mb" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The total memory on the remote device in Mb.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when hardware is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_model"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_model:

      .. rst-class:: ansible-option-title

      **ansible_net_model**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_model" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The model name returned from the device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_neighbors"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_neighbors:

      .. rst-class:: ansible-option-title

      **ansible_net_neighbors**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_neighbors" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The list of LLDP neighbors from the remote device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when interfaces is configured


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_serialnum"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_serialnum:

      .. rst-class:: ansible-option-title

      **ansible_net_serialnum**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_serialnum" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The serial number of the remote device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-ansible_net_version"></div>

      .. _ansible_collections.drivenets.dnos.dnos_facts_module__return-ansible_net_version:

      .. rst-class:: ansible-option-title

      **ansible_net_version**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_net_version" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The operating system version running on the remote device.


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


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
