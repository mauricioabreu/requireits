"""requireits API."""

import json
import logging
import os.path
from pkg_resources import parse_version
import os
import sys

import click
import requests
import requirements


PYPI_URL = 'https://pypi.python.org/pypi/{0}/json'

FAIL_SILENTLY = False

logger = logging.getLogger('check_requirements')
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setFormatter(logging.Formatter('%(message)s'))
logger_handler.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.addHandler(logger_handler)


class PackageNotFound(Exception):

    """Exception raised for packages no found."""


class Requirement(object):

    """Requirement object stores package health information."""

    def __init__(self, name, installed_version, latest_version):
        """Set package information."""
        self.name = name
        self.installed_version = installed_version
        self.latest_version = latest_version

    def is_outdated(self):
        """Return whether the package is outdated."""
        return self.installed_version != self.latest_version

    def is_valid(self):
        """Return whether the package is valid."""
        return bool(self.installed_version)


def parse_requirements(req_files):
    """Parse a list of requirement file and return a set of packages."""
    reqs = []

    for req_file in req_files:
        with open(req_file) as f:
            for req in requirements.parse(f):
                reqs.append(req)

    return set(reqs)


def load_pkg_info(pkg_name):
    """Load package info given a package name."""
    try:
        url_req = requests.get(PYPI_URL.format(pkg_name))
    except requests.exceptions.ConnectionError:
        return

    if url_req.status_code == 200:
        pkg_info = url_req.text
        return json.loads(pkg_info.decode('utf-8'))


def get_pkg_info(pkg_name):
    """Get package info. Setting FAIL_SILENTLY to true should stop running."""
    pkg_info = load_pkg_info(pkg_name)
    if not pkg_info and not FAIL_SILENTLY:
        raise PackageNotFound('{0} not found.'.format(pkg_name))
    return pkg_info


def get_latest_version(pkg_info):
    """Return latest version of a package."""
    if not pkg_info:
        return None, None
    version = pkg_info['info']['version']
    return parse_version(version), version


def get_ignored_packages():
    """Return a list of ignored packages described inside .pipignopre."""
    ignored_packages = []
    if os.path.isfile('.pipignore'):
        with open('.pipignore') as f:
            ignored_packages = f.read().strip().splitlines()
    return ignored_packages


def get_packages(req_files, ignored_packages=None):
    """Get packages to be reported."""
    requirements_pkgs = parse_requirements(req_files)

    reported_pkgs = []

    for pkg in requirements_pkgs:
        installed_version = None
        latest_version = None

        if not ignored_packages:
            ignored_packages = get_ignored_packages()

        if pkg.name not in ignored_packages:
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


def generate_report(pkgs):
    """Generate packages report."""
    if not pkgs:
        raise ValueError("Could not generate report without packages.")

    for pkg in pkgs:
        if pkg.is_valid():
            if pkg.is_outdated():
                logger.info("{} is outdated.".format(pkg.name))
            else:
                logger.info("{} is up-to-date.".format(pkg.name))
        else:
            logger.info("No information found for {}.".format(pkg.name))


@click.command()
@click.argument('files', nargs=-1, type=click.Path())
def report(files):
    """Output packages report."""
    pkgs = get_packages(files)
    generate_report(pkgs)

if __name__ == '__main__':
    report()
