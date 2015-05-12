"""requireits setup."""

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test

TestCommand = test


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


install_requires = [
    'caniusepython3==2.2.0',
    'click==3.3',
    'requests==2.4.1',
    'requirements-parser==0.0.6',
]

dev_requires = [
    'flake8==2.2.3',
]

tests_require = [
    'mock==1.0.1',
    'pytest==2.6.2',
]

setup(
    name="requireits",
    version="0.0.1.dev0",
    packages=find_packages(),
    author="Mauricio de Abreu Antunes",
    author_email="mauricio.abreua@gmail.com",
    description="Check your requirements the easy way",
    long_description=open('README.rst').read(),
    url="https://github.com/mauricioabreu/requireits",
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
        'dev': dev_requires,
    },
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ]
)
