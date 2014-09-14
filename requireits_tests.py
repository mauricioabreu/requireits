"""requireits tests.

To run these tests you shoud have py.test installed.
Use py.test requireits_tests.py

All tests should pass.
"""

import tempfile

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
        ignored_packages = ['Django']
        pkgs = requireits.get_packages([f.name], ignored_packages)
    assert len(pkgs) == 2


def test_outdated_pkg():
    """Test if package is outdated."""
    req = requireits.Requirement('Django', '1.6.7', '1.7.0')
    assert req.is_outdated() is True


def test_valid_package():
    """Test if package is valid."""
    req = requireits.Requirement('requireits', None, None)
    assert req.is_valid_package() is False
