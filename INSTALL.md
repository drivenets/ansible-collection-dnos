Drivenets DNOS Ansible Collection - Local Install Guide

This guide documents a reproducible local install in the workspace virtual environment, including the `ansible.netcommon` dependency, and how to verify that Ansible sees the DNOS collection and plugins. We will keep this file updated as we iterate.

Prerequisites
- Python 3.9+ on macOS (zsh)
- This workspace path: `/Users/abisheksureshkumar/Cursor Local/Ansible`

1) Create and activate a virtual environment
```bash
cd "/Users/abisheksureshkumar/Cursor Local/Ansible"
python3 -m venv .venv
source .venv/bin/activate
python -V
pip install --upgrade pip
```

2) Install Ansible Core in the venv (fresh install)
- Clean slate: remove any existing Ansible packages first
```bash
pip freeze | grep -i ansible | xargs pip uninstall -y || echo "No ansible packages to remove"
pip install --upgrade pip
pip install "ansible-core>=2.15,<2.16"
ansible --version
```

3) Prepare a local collections path
```bash
export ANSIBLE_COLLECTIONS_PATHS="$(pwd)/collections"
mkdir -p "$ANSIBLE_COLLECTIONS_PATHS"
```

4) Install ansible.netcommon into the local collections path
- Online:
```bash
ansible-galaxy collection install ansible.netcommon -p "$ANSIBLE_COLLECTIONS_PATHS"
```
- Offline (when you have the tarball):
```bash
ansible-galaxy collection install /path/to/ansible-netcommon-<ver>.tar.gz -p "$ANSIBLE_COLLECTIONS_PATHS"
```

5) Build and install the Drivenets DNOS collection locally
```bash
# Build (optional if you already have the tarball in drivenets.dnos-main/)
ansible-galaxy collection build ./drivenets.dnos-main

# Install the built tarball
ansible-galaxy collection install ./drivenets.dnos-main/drivenets-dnos-1.0.0.tar.gz \
  -p "$ANSIBLE_COLLECTIONS_PATHS" --force
```

6) Verify installation and discovery
```bash
# Confirm ansible and collection paths
ansible --version
ansible-galaxy collection list | grep -E "(drivenets.dnos|ansible.netcommon)"

# Verify modules and plugins are visible
ansible-doc -t module -l | grep -i "drivenets.dnos.dnos_config"
ansible-doc -t cliconf -l | grep -i dnos     # should list: drivenets.dnos.dnos
ansible-doc -t netconf  -l | grep -i dnos     # should list: drivenets.dnos.dnos
```

7) Network OS name and basic usage
- Use this exact network OS string in inventories and playbooks: `drivenets.dnos.dnos`
- Minimal inventory example (network_cli):
```ini
[dnos_devices]
router1 ansible_host=192.0.2.10 \
  ansible_user=dnroot ansible_password=dnroot \
  ansible_connection=ansible.netcommon.network_cli \
  ansible_network_os=drivenets.dnos.dnos
```

- Minimal playbook example (CLI) – change hosts/credentials as needed:
```yaml
---
- name: DNOS quick verification
  hosts: dnos_devices
  gather_facts: false
  tasks:
    - name: Show version (example)
      drivenets.dnos.dnos_command:
        commands:
          - show system version
```

Offline notes
- For strictly offline installs, place all required tarballs in a known folder and replace the Galaxy URLs with local paths in step 4 and 5.
- Keep `ANSIBLE_COLLECTIONS_PATHS` exported in the shell where you run Ansible commands, so the locally installed collections are discovered.

Troubleshooting
- If you see warnings about version support, they are usually non-fatal. You can adjust `ansible-core` (e.g., 2.14.x or 2.16.x) if needed.
- If a plugin is listed by `ansible-doc -l` but `ansible-doc <FQCN>` does not render, the plugin still loads; this is typically a documentation block formatting issue and does not affect runtime.

## Verified Installation Status

✅ Collection Build: SUCCESS  
✅ Collection Install: SUCCESS  
✅ Plugin Discovery: SUCCESS (cliconf, netconf)  
✅ Module Documentation: SUCCESS  
✅ Compile Sanity Tests: SUCCESS (0 errors)  
⚠️  Minor warnings: duplicate dict keys in some modules (non-blocking)

## Next Steps

1. Create inventory files for DNOS devices
2. Set up connection variables (ansible_network_os: drivenets.dnos.dnos)
3. Write playbooks using the available modules
4. Test with actual DNOS devices or simulators
5. Optional: Install `ansible.netcommon` tarball for fully offline setup

