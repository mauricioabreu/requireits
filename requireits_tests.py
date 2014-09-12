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
    with tempfile.NamedTemporaryFile('w') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        pkgs = requireits.get_packages([f.name])
    assert len(pkgs) == 3


def test_multiple_requirement_files():
    with tempfile.NamedTemporaryFile('w') as f1:
        f1.write(TEST_REQUIREMENTS_PKGS)
        f1.flush()
        with tempfile.NamedTemporaryFile('w') as f2:
            f2.write(MORE_TEST_REQUIREMENTS_PKGS)
            f2.flush()
            pkgs = requireits.get_packages([f1.name, f2.name])
    assert len(pkgs) == 4


def test_ignored_pkgs():
    with tempfile.NamedTemporaryFile('w+r') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        ignored_packages = ['Django']
        pkgs = requireits.get_packages([f.name], ignored_packages)
    assert len(pkgs) == 2
