# -*- coding: UTF-8 -*
"""
Setup script for behave.

USAGE:
    python setup.py install
    python setup.py behave_test     # -- XFAIL on Windows (currently).
    python setup.py nosetests

REQUIRES:
* setuptools >= 36.2.0

SEE ALSO:
* https://setuptools.readthedocs.io/en/latest/history.html
"""

import sys
import os.path

HERE0 = os.path.dirname(__file__) or os.curdir
os.chdir(HERE0)
HERE = os.curdir
sys.path.insert(0, HERE)

from setuptools import find_packages, setup
from setuptools_behave import behave_test


# -----------------------------------------------------------------------------
# CONFIGURATION:
# -----------------------------------------------------------------------------
python_version = float("%s.%s" % sys.version_info[:2])
BEHAVE = os.path.join(HERE, "behave")
README = os.path.join(HERE, "README.rst")
description = "".join(open(README).readlines()[4:])


# -----------------------------------------------------------------------------
# UTILITY:
# -----------------------------------------------------------------------------
def find_packages_by_root_package(where):
    """
    Better than excluding everything that is not needed,
    collect only what is needed.
    """
    root_package = os.path.basename(where)
    packages = [ "%s.%s" % (root_package, sub_package)
                 for sub_package in find_packages(where)]
    packages.insert(0, root_package)
    return packages


# -----------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------
setup(
    name="behave",
    version="1.2.7.dev2",
    description="behave is behaviour-driven development, Python style",
    long_description=description,
    author="Jens Engel, Benno Rice and Richard Jones",
    author_email="behave-users@googlegroups.com",
    url="http://github.com/behave/behave",
    provides = ["behave", "setuptools_behave"],
    packages = find_packages_by_root_package(BEHAVE),
    py_modules = ["setuptools_behave"],
    entry_points={
        "console_scripts": [
            "behave = behave.__main__:main"
        ],
        "distutils.commands": [
            "behave_test = setuptools_behave:behave_test"
        ]
    },
    # -- REQUIREMENTS:
    # SUPPORT: python2.7, python3.3 (or higher)
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*",
    install_requires=[
        "cucumber-tag-expressions >= 4.1.0",
        "enum34; python_version < '3.4'",
        "parse >= 1.18.0",
        "parse_type >= 0.6.0",
        "six >= 1.15.0",
        "traceback2; python_version < '3.0'",

        # -- PREPARED:
        "win_unicode_console; python_version <= '3.9'",
        "contextlib2;  python_version < '3.5'",
        # DISABLED: "contextlib2 >= 21.6.0;  python_version < '3.5'",
        "colorama >= 0.3.7",
    ],
    tests_require=[
        "pytest <  5.0; python_version <  '3.0'", # >= 4.2
        "pytest >= 5.0; python_version >= '3.0'",
        "pytest-html >= 1.19.0,<2.0; python_version <  '3.0'",
        "pytest-html >= 2.0;         python_version >= '3.0'",
        "mock  <  4.0;   python_version <  '3.6'",
        "mock  >= 4.0;   python_version >= '3.6'",
        "PyHamcrest >= 2.0.2; python_version >= '3.0'",
        "PyHamcrest <  2.0;   python_version <  '3.0'",

        # -- HINT: path.py => path (python-install-package was renamed for python3)
        "path >= 13.1.0;         python_version >= '3.5'",
        "path.py >=11.5.0,<13.0; python_version <  '3.5'",
        # -- PYTHON2 BACKPORTS:
        "pathlib;    python_version <= '3.4'",
    ],
    cmdclass = {
        "behave_test": behave_test,
    },
    extras_require={
        "docs": [
            "sphinx >= 1.6",
            "sphinx_bootstrap_theme >= 0.6"
        ],
        "develop": [
            "coverage",
            "pytest >=4.2,<5.0; python_version <  '3.0' # pytest >= 4.2",
            "pytest >= 5.0; python_version >= '3.0'",
            "pytest-html >= 1.19.0,<2.0; python_version <  '3.0'",
            "pytest-html >= 2.0;         python_version >= '3.0'",
            "mock  <  4.0;   python_version <  '3.6'",
            "mock  >= 4.0;   python_version >= '3.6'",
            "PyHamcrest >= 2.0.2; python_version >= '3.0'",
            "PyHamcrest <  2.0;   python_version <  '3.0'",
            "pytest-cov",
            "tox",
            "invoke >= 1.4.0",
            # -- HINT: path.py => path (python-install-package was renamed for python3)
            "path >= 13.1.0;    python_version >= '3.5'",
            "path.py >= 11.5.0; python_version <  '3.5'",
            "pycmd",
            "pathlib; python_version <= '3.4'",
            "modernize >= 0.5",
            "pylint",
        ],
        'formatters': [
            "behave-html-formatter",
        ],
        'toml': [  # Enable pyproject.toml support.
            "tomli>=1.1.0; python_version >=  '3.0' and python_version < '3.11'",
            "toml>=0.10.2; python_version <  '3.0'",  # py27 support
        ],
    },
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: Jython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: BSD License",
    ],
    zip_safe = True,
)
