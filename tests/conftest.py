import os
import tempfile
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    with patch('subprocess.call') as mock_call, \
         patch('subprocess.check_output') as mock_check_output:
        mock_call.return_value = 0
        mock_check_output.return_value = "* main\n  develop\n"
        yield {
            'call': mock_call,
            'check_output': mock_check_output
        }


@pytest.fixture
def mock_os_path():
    """Mock os.path.exists for testing."""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def sample_oca_dependencies():
    """Provide sample OCA dependencies content."""
    return """# Sample dependencies
server-tools
server-env
# Comment line
web-tools 8.0
specific-org/custom-addon 9.0"""


@pytest.fixture
def mock_file_operations():
    """Mock file read/write operations."""
    with patch('builtins.open') as mock_open:
        yield mock_open


@pytest.fixture
def mock_git_operations():
    """Mock git operations for testing repo functionality."""
    with patch('subprocess.call') as mock_call, \
         patch('subprocess.check_output') as mock_output:
        mock_call.return_value = 0
        mock_output.return_value = "* 8.0\n  7.0\n  9.0\n"
        yield {
            'call': mock_call,
            'output': mock_output
        }


@pytest.fixture
def repo_config():
    """Provide repository configuration for testing."""
    return {
        'remote_url': 'server-tools',
        'fetch_dep': True,
        'expected_path': '/opt/odoo/additional_addons/server-tools',
        'expected_url': 'https://github.com/OCA/server-tools.git'
    }


@pytest.fixture
def odoo_paths():
    """Provide Odoo-related path configurations."""
    return {
        'extra_addons': '/opt/odoo/additional_addons/',
        'odoo_addons': '/opt/odoo/sources/odoo/addons',
        'odoo_conf': '/opt/odoo/etc/odoo.conf',
        'dependencies_file': 'oca_dependencies.txt'
    }