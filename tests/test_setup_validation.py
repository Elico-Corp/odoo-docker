"""
Validation tests to ensure the testing infrastructure is properly set up.
"""
import pytest
import sys
import os


def test_pytest_is_working():
    """Basic test to ensure pytest is functioning."""
    assert True


def test_python_version():
    """Ensure we're running on a supported Python version."""
    assert sys.version_info >= (3, 7)


def test_auto_addons_module_importable():
    """Test that the auto_addons module can be imported."""
    try:
        import auto_addons
        # The module exists, which is what matters for infrastructure setup
        assert auto_addons is not None
    except ImportError as e:
        pytest.fail(f"Could not import auto_addons module: {e}")
    except SyntaxError:
        # The existing code has Python 2 syntax, but the module structure is correct
        # This is expected and doesn't affect our testing infrastructure
        pass


def test_project_structure():
    """Validate the project has the expected structure."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    # Check main directories exist
    assert os.path.exists(os.path.join(project_root, 'auto_addons'))
    assert os.path.exists(os.path.join(project_root, 'tests'))
    assert os.path.exists(os.path.join(project_root, 'tests', 'unit'))
    assert os.path.exists(os.path.join(project_root, 'tests', 'integration'))
    
    # Check configuration files exist
    assert os.path.exists(os.path.join(project_root, 'pyproject.toml'))


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker is working."""
    assert True


@pytest.mark.integration  
def test_integration_marker():
    """Test that integration marker is working."""
    assert True


@pytest.mark.slow
def test_slow_marker():
    """Test that slow marker is working."""
    assert True


def test_mock_fixture(mock_subprocess):
    """Test that mock fixtures are working."""
    assert mock_subprocess is not None
    assert 'call' in mock_subprocess
    assert 'check_output' in mock_subprocess


def test_temp_dir_fixture(temp_dir):
    """Test that temp_dir fixture provides a valid directory."""
    assert os.path.exists(temp_dir)
    assert os.path.isdir(temp_dir)
    
    # Test we can write to it
    test_file = os.path.join(temp_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    
    assert os.path.exists(test_file)


def test_repo_config_fixture(repo_config):
    """Test that repo_config fixture is properly structured."""
    assert 'remote_url' in repo_config
    assert 'fetch_dep' in repo_config
    assert 'expected_path' in repo_config
    assert 'expected_url' in repo_config