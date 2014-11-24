"""requireits tests.

To run these tests you shoud have py.test installed.
Use py.test requireits_tests.py

All tests should pass.
"""

import json
import tempfile

from click.testing import CliRunner

from mock import patch

import pytest

import requests

import requireits


TEST_REQUIREMENTS_PKGS = """
        Django==1.6.7
        south==0.8.4
        git+https://github.com/jeffkistler/django-decorator-include.git@1cce01ee0130156e8fde5c46e61287bea37c5c7f#egg=django-decorator-include
    """

MORE_TEST_REQUIREMENTS_PKGS = """
        requests==2.2.1
    """

PIP_IGNORE_PKGS = """
        Django
    """

REQUIREITS_JSON = """
{
    "Django": {
        "ignore": true
    },
    "click": {
        "ignore": false,
        "changelog": "http://click.pocoo.org/3/changelog/"
    }
}
"""


def test_check_count_pkgs():
    """Test if total of checked packages are equal to reported packages."""
    with tempfile.NamedTemporaryFile('w') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        pkgs = requireits.get_packages([f.name])
    assert len(pkgs) == 3


def test_multiple_requirement_files():
    """Test requireits using multiple files."""
    with tempfile.NamedTemporaryFile('w') as f1:
        f1.write(TEST_REQUIREMENTS_PKGS)
        f1.flush()
        with tempfile.NamedTemporaryFile('w') as f2:
            f2.write(MORE_TEST_REQUIREMENTS_PKGS)
            f2.flush()
            pkgs = requireits.get_packages([f1.name, f2.name])
    assert len(pkgs) == 4


def test_ignored_pkgs():
    """Test if ignored packages are being considered."""
    with tempfile.NamedTemporaryFile('w+r') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        extra_info = json.loads(REQUIREITS_JSON)
        pkgs = requireits.get_packages([f.name], extra_info)
    assert len(pkgs) == 2


def test_outdated_pkg():
    """Test if package is outdated."""
    req = requireits.Requirement('Django', '1.6.7', '1.7.0')
    assert req.is_outdated() is True


def test_valid_pkg():
    """Test if package is valid."""
    req = requireits.Requirement('requireits', None, None)
    assert req.is_valid() is False


def test_pypi_connection_error():
    """Test pypi connection error."""
    with patch.object(requests, 'get') as mock_method:
        mock_method.side_effect = requests.exceptions.ConnectionError
        assert requireits.load_package_info('requests') is None


def test_unknown_latest_version():
    """Test for unknown latest version.

    Some packace versions can not be found.
    """
    pkg_latest_version = requireits.get_latest_version(None)
    assert pkg_latest_version == (None, None)


def test_pkg_not_found():
    """Test for packages not found.

    If FAIL_SILENTLY is set to True, get_package_info should just return None.
    In case of FAIL_SILENTLY is set to False then the program should stop
    raising PackageNotFound exception.
    """
    requireits.FAIL_SILENTLY = False
    with pytest.raises(requireits.PackageNotFound):
        requireits.get_package_info('this.package.should.not.exist')


def test_cli():
    """Test command line interface."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile('w') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        result = runner.invoke(requireits.report, [f.name])
    assert result.exit_code == 0
