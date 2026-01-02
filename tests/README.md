# DNOS Ansible Collection Testing Guide

This directory contains the testing infrastructure for the DNOS Ansible collection. It includes both unit tests and integration tests to ensure the reliability and functionality of all modules and plugins.

## Test Structure

```
tests/
├── unit/                   # Unit tests for modules, plugins, and utilities
│   ├── modules/           # Module unit tests
│   │   └── network/
│   │       └── dnos/      # DNOS module tests
│   ├── plugins/           # Plugin unit tests (netconf, terminal, etc.)
│   ├── conftest.py        # PyTest configuration and fixtures
│   └── utils.py           # Testing utility functions
├── integration/           # Integration tests for real device testing
│   └── README.md         # Integration testing guide
└── output/               # Test output and reports
```

## Prerequisites

### System Requirements

- **Python**: 3.10+ (required for ansible-dev-tools ecosystem)
- **Operating System**: Linux, macOS, or Windows with WSL2

### Installation

1. **Install System Dependencies** (if needed):
   ```bash
   # For RHEL/CentOS/Fedora
   sudo dnf install gcc-c++ python3-devel libssh-devel
   
   # For Ubuntu/Debian
   sudo apt-get install build-essential python3-dev libssh-dev
   
   # For macOS (with Homebrew)
   brew install libssh
   ```

2. **Install Python Dependencies**:
   ```bash
   # Install test requirements (includes runtime requirements)
   pip install -r test-requirements.txt
   
   # Or install just runtime requirements
   pip install -r requirements.txt
   ```

3. **Install Collection** (see [Local Development Setup](#local-development-setup) below for local build)

## Local Development Setup

### Building the Collection Locally

Build and install the collection without dependency on Ansible Galaxy:

#### Method 1: Direct Galaxy Build
```bash
# Build collection tarball locally
ansible-galaxy collection build

# Install from local tarball
ansible-galaxy collection install drivenets-dnos-*.tar.gz --force

# Verify installation
ansible-galaxy collection list | grep drivenets.dnos
```

#### Method 2: Development Installation
```bash
# Install in development mode (editable)
export ANSIBLE_COLLECTIONS_PATH="$(pwd)/collections"
mkdir -p collections/ansible_collections/drivenets
ln -sf "$(pwd)" collections/ansible_collections/drivenets/dnos

# Verify collection path
ansible-galaxy collection list drivenets.dnos
```

#### Method 3: Using Tox (Recommended for CI/CD)
```bash
# Build using tox automation
tox -e galaxy

# Install the built collection
ansible-galaxy collection install drivenets-dnos-*.tar.gz --force
```

### Local Installation Verification

#### Basic Verification
```bash
# Check collection is available
ansible-galaxy collection list drivenets.dnos

# Verify modules are accessible  
ansible-doc drivenets.dnos.dnos_interfaces

# Test basic module import
python -c "from ansible_collections.drivenets.dnos.plugins.modules import dnos_command; print('OK')"
```

#### Advanced Verification
```bash
# Check all modules are loadable
for module in plugins/modules/dnos_*.py; do
    module_name=$(basename "$module" .py)
    echo "Testing $module_name..."
    python -c "from ansible_collections.drivenets.dnos.plugins.modules import $module_name" || echo "FAILED: $module_name"
done

# Verify plugins
python -c "from ansible_collections.drivenets.dnos.plugins.netconf import dnos; print('NETCONF plugin OK')"
python -c "from ansible_collections.drivenets.dnos.plugins.cliconf import dnos; print('CLI plugin OK')"
```

### Collection Development Environment

#### Using Python Virtual Environment
```bash
# Create dedicated development environment
python -m venv dnos-dev
source dnos-dev/bin/activate

# Install in development mode with all dependencies
pip install -e .[dev]

# Alternative: Install test requirements only
pip install -r test-requirements.txt
```

#### Using Tox for Isolated Testing
```bash
# Test with multiple Python versions
tox -e py310,py311,py312

# Test with multiple Ansible versions
tox -e py311-ansible2.16,py311-ansible2.17

# Run linting only
tox -e linters

# Run units only
tox -e units
```

### Ansible-Test Integration

#### Running ansible-test Commands

The collection includes full `ansible-test` support for comprehensive validation:

##### Sanity Tests
```bash
# Run all sanity checks
ansible-test sanity

# Run specific sanity tests
ansible-test sanity --test validate-modules
ansible-test sanity --test pep8
ansible-test sanity --test pylint

# Test specific files
ansible-test sanity plugins/modules/dnos_interfaces.py
```

##### Unit Tests with ansible-test
```bash
# Run all unit tests
ansible-test units

# Run with coverage
ansible-test units --coverage

# Run specific test modules
ansible-test units tests/unit/modules/network/dnos/test_dnos_interfaces.py

# Run with Python version specification
ansible-test units --python 3.11

# Run in verbose mode
ansible-test units -v
```

##### Integration Tests with ansible-test
```bash
# Run integration tests (requires real devices)
ansible-test integration

# Run specific integration targets
ansible-test integration dnos_command dnos_interfaces

# Run with coverage
ansible-test integration --coverage

# Run with specific Python version
ansible-test integration --python 3.11
```

##### Network Integration Tests
```bash
# Set up inventory for network tests
cp tests/integration/inventory.networking.sample tests/integration/inventory.networking
# Edit inventory.networking with your device details

# Run network integration tests
ansible-test network-integration dnos_command

# Run all network tests
ansible-test network-integration --inventory tests/integration/inventory.networking
```

#### Collection Testing with ansible-test

##### Full Collection Validation
```bash
# Complete validation pipeline
ansible-test sanity --requirements
ansible-test units --coverage
ansible-test integration --coverage

# Generate coverage report
ansible-test coverage html
ansible-test coverage report
```

##### Testing Specific Components
```bash
# Test specific module
ansible-test sanity plugins/modules/dnos_interfaces.py
ansible-test units tests/unit/modules/network/dnos/test_dnos_interfaces.py

# Test plugin functionality
ansible-test sanity plugins/netconf/dnos.py
ansible-test sanity plugins/cliconf/dnos.py
```

#### Environment Variables for ansible-test

```bash
# Set test environment variables
export ANSIBLE_TEST_PREFER_PODMAN=1  # Use Podman instead of Docker
export ANSIBLE_TEST_DOCKER_PRIVILEGED=true  # For container tests

# Set collection paths
export ANSIBLE_COLLECTIONS_PATH="$(pwd)/collections"

# Set Python interpreter
export ANSIBLE_TEST_PYTHON_INTERPRETER=/usr/bin/python3.11
```

### Build Automation and CI/CD

#### Automated Build Pipeline
```bash
# Complete build and test pipeline
#!/bin/bash
set -e

echo "=== Building DNOS Collection ==="

# 1. Clean previous builds
rm -f drivenets-dnos-*.tar.gz

# 2. Run quality checks
echo "Running linters..."
tox -e linters

# 3. Run unit tests
echo "Running unit tests..."
tox -e units

# 4. Build collection
echo "Building collection..."
ansible-galaxy collection build

# 5. Install and verify
echo "Installing collection..."
ansible-galaxy collection install drivenets-dnos-*.tar.gz --force

# 6. Verify installation
echo "Verifying installation..."
ansible-galaxy collection list drivenets.dnos
ansible-doc drivenets.dnos.dnos_command > /dev/null

echo "=== Build Complete ==="
```

#### GitHub Actions Integration
```yaml
# Example .github/workflows/test.yml
name: Test Collection
on: [push, pull_request]

jobs:
  sanity:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        ansible-version: ['2.16', '2.17']
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install ansible-core==${{ matrix.ansible-version }}.*
        pip install -r test-requirements.txt
    
    - name: Run ansible-test sanity
      run: ansible-test sanity --requirements
    
    - name: Run ansible-test units
      run: ansible-test units --coverage
    
    - name: Build collection
      run: ansible-galaxy collection build
```

### Custom Build Configuration

#### Customizing galaxy.yml
```yaml
# Modify galaxy.yml for custom builds
namespace: drivenets
name: dnos
version: 1.0.0-dev
dependencies:
  ansible.netcommon: ">=5.0.0,<9.0.0"
  ansible.utils: ">=6.0.0"
```

#### Custom MANIFEST.in
```bash
# Add custom files to build
echo "include my_custom_config.yml" >> MANIFEST.in

# Rebuild collection
ansible-galaxy collection build
```

### Troubleshooting Local Development

#### Common Build Issues
```bash
# Clear build cache
rm -rf build/ dist/ *.egg-info/

# Clear ansible cache
rm -rf ~/.ansible/collections/ansible_collections/drivenets/dnos/

# Reset collection paths
unset ANSIBLE_COLLECTIONS_PATH
export ANSIBLE_COLLECTIONS_PATH="$(pwd)/collections"
```

#### Module Import Issues
```bash
# Debug module loading
python -c "
import sys
print('Python path:', sys.path)
try:
    from ansible_collections.drivenets.dnos.plugins.modules import dnos_command
    print('Module import: SUCCESS')
except Exception as e:
    print('Module import: FAILED -', e)
"
```

#### ansible-test Issues
```bash
# Update ansible-test requirements
ansible-test sanity --requirements --docker default

# Run with specific Docker image
ansible-test units --docker ubuntu2204

# Debug test execution
ansible-test units --explain
```

## Running Unit Tests

### Quick Start

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage reporting
pytest tests/unit/ --cov=plugins --cov-report=html --cov-report=term

# Run specific module tests
pytest tests/unit/modules/network/dnos/test_dnos_interfaces.py

# Run with verbose output
pytest tests/unit/ -v

# Run in parallel for faster execution
pytest tests/unit/ -n auto
```

**Alternative: Using ansible-test** (see [Ansible-Test Integration](#ansible-test-integration) for comprehensive testing):
```bash
# Run unit tests with ansible-test
ansible-test units --coverage

# Run specific test file with ansible-test
ansible-test units tests/unit/modules/network/dnos/test_dnos_interfaces.py
```

### Test Categories

#### Module Tests
Test individual Ansible modules for correct behavior:

```bash
# Test specific modules
pytest tests/unit/modules/network/dnos/test_dnos_command.py
pytest tests/unit/modules/network/dnos/test_dnos_interfaces.py
pytest tests/unit/modules/network/dnos/test_dnos_acls.py

# Test all modules
pytest tests/unit/modules/
```

#### Plugin Tests
Test collection plugins (netconf, terminal, cliconf):

```bash
# Test NETCONF plugin
pytest tests/unit/plugins/netconf/

# Test all plugins
pytest tests/unit/plugins/
```

### Advanced Testing Options

#### Coverage Analysis
```bash
# Generate HTML coverage report
pytest tests/unit/ --cov=plugins --cov-report=html

# View coverage in terminal
pytest tests/unit/ --cov=plugins --cov-report=term-missing

# Generate XML coverage for CI/CD
pytest tests/unit/ --cov=plugins --cov-report=xml
```

#### Parallel Execution
```bash
# Run tests in parallel (faster execution)
pytest tests/unit/ -n auto

# Specify number of parallel processes
pytest tests/unit/ -n 4
```

#### Test Filtering
```bash
# Run tests by pattern
pytest tests/unit/ -k "interfaces"

# Run tests with specific markers
pytest tests/unit/ -m "not slow"

# Run failed tests only (after a previous run)
pytest tests/unit/ --lf
```

#### Debugging Tests
```bash
# Stop on first failure
pytest tests/unit/ -x

# Drop into debugger on failure
pytest tests/unit/ --pdb

# Show local variables on failure
pytest tests/unit/ -l
```

## Test Development

### Writing Unit Tests

#### Module Test Structure
```python
# tests/unit/modules/network/dnos/test_dnos_example.py

from unittest.mock import MagicMock, patch
import pytest

from ansible_collections.drivenets.dnos.plugins.modules import dnos_example
from ansible_collections.drivenets.dnos.tests.unit.modules.utils import ModuleTestCase, set_module_args


class TestDnosExampleModule(ModuleTestCase):
    module = dnos_example

    def setUp(self):
        super(TestDnosExampleModule, self).setUp()
        
        # Mock common network connections
        self.mock_get_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def test_merged_state(self):
        """Test merged configuration state"""
        set_module_args({
            'config': [{'name': 'test1'}],
            'state': 'merged'
        })
        
        result = self.execute_module(changed=True)
        self.assertIn('commands', result)

    def test_idempotent_config(self):
        """Test configuration idempotency"""
        # Setup existing config
        self.get_config.return_value = "existing config"
        
        set_module_args({
            'config': [{'name': 'test1'}],
            'state': 'merged'
        })
        
        result = self.execute_module(changed=False)
        self.assertEqual(result['commands'], [])
```

#### Plugin Test Structure
```python
# tests/unit/plugins/test_example.py

import pytest
from unittest.mock import MagicMock, patch

from ansible_collections.drivenets.dnos.plugins.plugin_utils import example_utility


class TestExamplePlugin:
    """Test cases for example plugin"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_connection = MagicMock()

    def test_plugin_functionality(self):
        """Test core plugin functionality"""
        result = example_utility.process_data("test_input")
        assert result == "expected_output"
```

### Test Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Mocking**: Mock external dependencies (network connections, file systems, etc.)
3. **Coverage**: Aim for high test coverage, especially for critical code paths
4. **Clear Names**: Use descriptive test names that explain what is being tested
5. **Documentation**: Add docstrings to test classes and complex test methods

### Test Fixtures and Utilities

#### Available Test Utilities

- **`ModuleTestCase`**: Base class for module testing with common setup
- **`set_module_args()`**: Helper to set module arguments for testing
- **`AnsibleExitJson`**: Exception for successful module completion
- **`AnsibleFailJson`**: Exception for module failure scenarios

#### Common Mock Patterns

```python
# Mock network configuration retrieval
with patch('ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network.Config.get_config') as mock_config:
    mock_config.return_value = "interface GigabitEthernet0/0/1"

# Mock NETCONF operations
with patch('ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.netconf_utils.get_device_data') as mock_netconf:
    mock_netconf.return_value = "<interface>data</interface>"

# Mock command execution
with patch('ansible_collections.drivenets.dnos.plugins.module_utils.network.dnos.dnos.get_connection') as mock_conn:
    mock_conn.return_value.send_command.return_value = "command output"
```

## Code Quality and Linting

This project uses multiple tools to ensure code quality [[memory:7066572]]:

### Running Linters

```bash
# Format code with black
black tests/unit/

# Sort imports with isort  
isort tests/unit/

# Check code style with flake8
flake8 tests/unit/

# Run Ansible-specific linting
ansible-lint

# Run all quality checks
tox -e linters
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Continuous Integration

### Automated Testing

The collection uses automated testing with various environments:

```bash
# Run all test environments
tox

# Run specific test environment
tox -e py310
tox -e py311
tox -e py312

# Run linting environment
tox -e linters

# Run specific Ansible version
tox -e ansible-core-2.16
```

### GitHub Actions Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch  
- Scheduled nightly runs

### Test Reports

Test results are available in multiple formats:
- **HTML Coverage**: `tests/output/coverage/`
- **JUnit XML**: `tests/output/junit/`
- **Test Logs**: `tests/output/`

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure collection is properly installed
ansible-galaxy collection list | grep drivenets.dnos

# Check Python path
python -c "import ansible_collections.drivenets.dnos; print('OK')"

# Set collections path explicitly
export ANSIBLE_COLLECTIONS_PATH="$(pwd)"
```

#### Mock Issues
```bash
# Clear pytest cache
pytest --cache-clear

# Remove bytecode files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

#### Dependency Conflicts
```bash
# Update dependencies
pip install -r test-requirements.txt --upgrade

# Use virtual environment
python -m venv test_env
source test_env/bin/activate
pip install -r test-requirements.txt
```

### Debugging Test Failures

#### Verbose Output
```bash
# Show detailed test output
pytest tests/unit/ -v -s

# Show local variables on failure
pytest tests/unit/ -l --tb=long
```

#### Interactive Debugging
```bash
# Drop into debugger on failure
pytest tests/unit/ --pdb

# Set breakpoint in test code
import pdb; pdb.set_trace()
```

## Development Workflow

### Recommended Workflow

1. **Setup Development Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r test-requirements.txt
   pre-commit install
   ```

2. **Write Tests First** (TDD approach):
   ```bash
   # Create test file
   touch tests/unit/modules/network/dnos/test_dnos_newmodule.py
   
   # Write failing tests
   pytest tests/unit/modules/network/dnos/test_dnos_newmodule.py
   ```

3. **Implement Module/Plugin**:
   ```bash
   # Create module file
   touch plugins/modules/dnos_newmodule.py
   
   # Implement functionality
   # Run tests to verify
   pytest tests/unit/modules/network/dnos/test_dnos_newmodule.py
   ```

4. **Verify Quality**:
   ```bash
   # Run all tests
   pytest tests/unit/
   
   # Check code quality
   black tests/unit/
   isort tests/unit/
   flake8 tests/unit/
   ansible-lint
   ```

### Code Coverage Goals

- **Module Tests**: Aim for >90% coverage
- **Plugin Tests**: Aim for >85% coverage
- **Critical Paths**: Aim for 100% coverage (error handling, state management)

## Contributing

### Submitting Tests

1. Follow existing test patterns and structure
2. Ensure all tests pass: `pytest tests/unit/`
3. Maintain or improve code coverage
4. Run linting tools and fix any issues
5. Add documentation for complex test scenarios

### Test Requirements

- All new modules must have comprehensive unit tests
- Tests must cover all supported states and error conditions
- Plugin modifications require corresponding test updates
- Integration tests should be added for major features

## Support and Resources

### Documentation
- [Ansible Testing Guide](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
- [PyTest Documentation](https://docs.pytest.org/)
- [Ansible Collection Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)

### Community
- [DNOS Collection Issues](https://github.com/drivenets/ansible-drivenets.dnos/issues)
- [Ansible Community](https://docs.ansible.com/ansible/latest/community/)

For questions about testing or to report test-related issues, please open an issue in the project repository.
