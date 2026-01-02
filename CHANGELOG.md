# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-08-14

### Added
- Initial release of the DriveNets DNOS Ansible Collection
- CLI and NETCONF connection plugins for DNOS devices
- Terminal plugin for DNOS device interaction
- Core module suite including:
  - System configuration (dnos_banner, dnos_reboot)
  - Device management (dnos_command, dnos_config)
  - Interface management (dnos_interfaces)
  - Monitoring and facts (dnos_facts)
- Comprehensive documentation and examples
- Unit and integration test suites
- Support for both check mode and diff mode operations

### Technical Details
- Requires Ansible Core >= 2.15.0
- Compatible with ansible.netcommon >= 5.0.0, < 9.0.0
- Supports Python 3.9+
- Full FQCN and short name module routing
- Production-ready for Ansible Galaxy publishing

### Security
- Apache 2.0 license
- No known security vulnerabilities
- Follows Ansible security best practices
