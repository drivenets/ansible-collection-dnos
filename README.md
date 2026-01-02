# DriveNets DNOS Collection

[![CI](https://github.com/ansible-collections/drivenets.dnos/actions/workflows/tests.yml/badge.svg?branch=main&event=schedule)](https://github.com/ansible-collections/drivenets.dnos/actions/workflows/tests.yml)
[![Codecov](https://codecov.io/gh/ansible-collections/drivenets.dnos/branch/main/graph/badge.svg)](https://codecov.io/gh/ansible-collections/drivenets.dnos)

The Ansible DriveNets DNOS collection includes a variety of Ansible content to help automate the management of DriveNets Network Operating System (DNOS) network appliances.

This collection has been tested against DriveNets DNOS version 25.2.x

## Support

As a community-supported collection, this collection is provided on a best-effort basis. Community support is available through various channels outlined in the Communication section below.

For enterprise deployments and commercial support inquiries, please contact DriveNets directly through their [official channels](https://drivenets.com/contact-us/).

## Communication

We're here to help! We encourage you to join the Ansible community and participate in discussions:

* **Questions about drivenets.dnos?** Please use the [**network** tag](https://forum.ansible.com/tag/network) when posting on the Ansible Forum.

* Join the Ansible forum:
  * [Get Help](https://forum.ansible.com/c/help/6): Get help with drivenets.dnos or help others. **Please tag your posts with 'network'.**
  * [Posts tagged with 'network'](https://forum.ansible.com/tag/network): Subscribe to participate in network automation discussions, including drivenets.dnos topics.
  * [Ansible Network Automation Working Group](https://forum.ansible.com/g/network-wg): Join the team to automatically get subscribed to posts tagged with [network](https://forum.ansible.com/tag/network). We welcome your participation!
  * [Social Spaces](https://forum.ansible.com/c/chat/4): Gather and interact with fellow enthusiasts.
  * [News & Announcements](https://forum.ansible.com/c/news/5): Track project-wide announcements including social events.

* The Ansible [Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn): Subscribe to receive announcements about releases and important changes.

For more information about communication, see the [Ansible communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

## Requirements

### Python Version
This collection requires **Python 3.11 or higher** on the Ansible controller.

The collection is tested with:
- Python 3.11
- Python 3.12

### Ansible Version
This collection supports **Ansible Core 2.16.0 and later**.

<!--start requires_ansible-->
## Ansible version compatibility

The collection is tested and verified against:
- Ansible Core 2.16
- Ansible Core 2.17
- Ansible Core 2.18
- Ansible Core 2.19

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

### Supported connections

The DriveNets DNOS collection supports ``network_cli`` and ``netconf`` connections.

## Included content

<!--start collection content-->
### Cliconf plugins
Name | Description
--- | ---
[drivenets.dnos.dnos](docs/drivenets.dnos.dnos_cliconf.rst)|Use dnos cliconf to run command on DriveNets DNOS platform

### Netconf plugins
Name | Description
--- | ---
[drivenets.dnos.dnos](docs/drivenets.dnos.dnos_netconf.rst)|Use dnos netconf plugin to run netconf commands on DriveNets DNOS platform

### Terminal plugins
Name | Description
--- | ---
[drivenets.dnos.dnos](docs/drivenets.dnos.dnos_terminal.rst)|Use dnos terminal plugin for SSH CLI connections

### Modules
Name | Description
--- | ---
[drivenets.dnos.dnos_command](docs/drivenets.dnos.dnos_command_module.rst)|Module to run commands on remote devices.
[drivenets.dnos.dnos_config](docs/drivenets.dnos.dnos_config_module.rst)|Module to manage configuration sections.
[drivenets.dnos.dnos_facts](docs/drivenets.dnos.dnos_facts_module.rst)|Module to collect facts from remote devices.
[drivenets.dnos.dnos_reboot](docs/drivenets.dnos.dnos_reboot_module.rst)|Module to reboot DNOS devices.

<!--end collection content-->

Click the ``Content`` button to see the list of content included in this collection.

## Installing this collection

You can install the DriveNets DNOS collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install drivenets.dnos

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: drivenets.dnos
```

### Connection examples

```yaml
---
- name: DriveNets DNOS Device Management
  hosts: dnos_devices
  connection: ansible.netcommon.network_cli
  vars:
    ansible_network_os: drivenets.dnos.dnos
    ansible_user: user1
    ansible_password: password
    
  tasks:
    - name: Gather device facts
      drivenets.dnos.dnos_facts:
        gather_subset:
          - default
          - interfaces
          - hardware
```

**NOTE**: For Ansible 2.9, you may not see deprecation warnings when you run your playbooks with this collection. Use this documentation to track when a module is deprecated.

### See Also:

* [DriveNets DNOS Platform Options](https://docs.ansible.com/ansible/latest/network/user_guide/platform_dnos.html)
* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [DriveNets DNOS collection repository](https://github.com/ansible-collections/drivenets.dnos). See [Contributing to Ansible-maintained collections](https://docs.ansible.com/ansible/devel/community/contributing_maintained_collections.html#contributing-maintained-collections) for complete details.

You can also join us on:

- IRC - the ``#ansible-network`` [libera.chat](https://libera.chat/) channel
- Slack - https://ansiblenetwork.slack.com

See the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) for details on contributing to Ansible.

### Code of Conduct
This collection follows the Ansible project's
[Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).
Please read and familiarize yourself with this document.

## Versioning and Deprecation

This collection follows [Semantic Versioning](https://semver.org/):

### Version Numbers: MAJOR.MINOR.PATCH

- **PATCH** (e.g., 1.0.1): Bugfixes only, no new features or breaking changes
- **MINOR** (e.g., 1.1.0): New features, deprecations, backwards compatible
- **MAJOR** (e.g., 2.0.0): Breaking changes, removal of deprecated features

### Deprecation Policy

- Features/modules will be deprecated for at least **one major version** before removal
- Deprecation warnings will appear in:
  - Module documentation
  - Runtime warnings when the feature is used
  - Changelog under "Deprecated Features"
- Deprecated features are removed only in major releases

### Example Timeline

- v1.5.0: Feature X is deprecated (warning added)
- v1.6.0-1.9.x: Feature X still works with deprecation warning
- v2.0.0: Feature X is removed

### Backward Compatibility

We maintain backward compatibility within major versions. This collection follows [Ansible's semantic versioning rules](https://docs.ansible.com/ansible/latest/community/collection_contributors/collection_requirements.html#semantic-versioning) for collections included in the Ansible community package.

## Release notes

Release notes are available in [CHANGELOG.rst](https://github.com/ansible-collections/drivenets.dnos/blob/main/CHANGELOG.rst) or via `changelogs/changelog.yaml`.

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.