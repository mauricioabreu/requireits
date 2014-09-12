import json
import logging
import os.path
from pkg_resources import parse_version
import os
import sys
import tempfile

import requests
import requirements


PYPI_URL = 'https://pypi.python.org/pypi/{0}/json'

FAIL_SILENTLY = False

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

logger = logging.getLogger('check_requirements')
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setFormatter(logging.Formatter('%(message)s'))
logger_handler.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.addHandler(logger_handler)


class PackageNotFound(Exception):
    pass


class Requirement(object):

    def __init__(self, name, installed_version, latest_version):
        self.name = name
        self.installed_version = installed_version
        self.latest_version = latest_version

    def is_outdated(self):
        return self.installed_version != self.latest_version:

    def is_valid_package(self):
        return bool(self.installed_version)


def parse_requirements(req_files):
    """Parse a list of requirement file and return a set of packages"""
    reqs = []

    for req_file in req_files:
        with open(req_file) as f:
            for req in requirements.parse(f):
                reqs.append(req)

    return set(reqs)


def load_pkg_info(pkg_name):
    "Load package info given a package name"
    try:
        url_req = requests.get(PYPI_URL.format(pkg_name))
    except requests.exceptions.ConnectionError:
        return

    if url_req.status_code == 200:
        pkg_info = url_req.text
        return json.loads(pkg_info.decode('utf-8'))


def get_pkg_info(pkg_name):
    pkg_info = load_pkg_info(pkg_name)
    if not pkg_info and not FAIL_SILENTLY:
        raise PackageNotFound('{0} not found.'.format(pkg_name))
    return pkg_info


def get_latest_version(pkg_info):
    """Return latest version of a package"""
    if not pkg_info:
        return None, None
    version = pkg_info['info']['version']
    return parse_version(version), version


def get_ignored_packages():
    """Return a list of ignored packages described inside .pipignopre"""
    ignored_packages = []
    if os.path.isfile('.pipignore'):
        with open('.pipignore') as f:
            ignored_packages = f.read().strip().splitlines()
    return ignored_packages


def get_packages(req_files, ignored_packages=None):
    """Get packages to be reported

    Examples
    --------

    req_files = ['requirements/base.txt', ]
    pkgs = get_packages(req_files)

    for pkg in pkgs:
        if pkg.is_valid_package():
            if pkg.is_outdated:
                print 'Package {0} is outdated.'.format(pkg.name)
            else:
                print 'Package {0} is up-to-date.'.format(pkg.name)
        else:
            print 'No information found for {0}.'.format(pkg.name)

    """
    requirements_pkgs = parse_requirements(req_files)

    reported_pkgs = []

    for pkg in requirements_pkgs:
        installed_version = None
        latest_version = None

        if not ignored_packages:
            ignored_packages = get_ignored_packages()

        if not pkg.name in ignored_packages:
            pkg_versions = get_latest_version(get_pkg_info(pkg.name))

            if pkg:
                try:
                    installed_version = pkg.specs[0][1]
                    latest_version = pkg_versions[1]
                except IndexError:
                    logger.debug(
                        'No information found for {0}.'.format(pkg.name))
                finally:
                    req = Requirement(pkg.name,
                                      installed_version,
                                      latest_version)

                # Add Requirement objects to the list
                reported_pkgs.append(req)

    return reported_pkgs


def test_check_count_pkgs():
    with tempfile.NamedTemporaryFile('w') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        pkgs = get_packages([f.name])
    assert len(pkgs) == 3


def test_multiple_requirement_files():
    with tempfile.NamedTemporaryFile('w') as f1:
        f1.write(TEST_REQUIREMENTS_PKGS)
        f1.flush()
        with tempfile.NamedTemporaryFile('w') as f2:
            f2.write(MORE_TEST_REQUIREMENTS_PKGS)
            f2.flush()
            pkgs = get_packages([f1.name, f2.name])
    assert len(pkgs) == 4


def test_ignored_pkgs():
    with tempfile.NamedTemporaryFile('w+r') as f:
        f.write(TEST_REQUIREMENTS_PKGS)
        f.flush()
        ignored_packages = ['Django']
        pkgs = get_packages([f.name], ignored_packages)
    assert len(pkgs) == 2
