# -*- coding: utf-8 -*
"""
Setup script for behave.

USAGE:
    python setup.py install
    python setup.py behave_test     # -- XFAIL on Windows (currently).
    python setup.py nosetests
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
BEHAVE4CMD0 = os.path.join(HERE, "behave4cmd0")
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
    version="1.2.6.dev0",
    description="behave is behaviour-driven development, Python style",
    long_description=description,
    author="Jens Engel, Benno Rice and Richard Jones",
    author_email="behave-users@googlegroups.com",
    url="http://github.com/behave/behave",
    provides = ["behave", "behave4cmd0", "setuptools_behave"],
    packages = find_packages_by_root_package(BEHAVE) + \
               find_packages_by_root_package(BEHAVE4CMD0),
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
    # SUPPORT: python2.6, python2.7, python3.3 (or higher)
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*",
    install_requires=[
        "parse >= 1.8.2",
        "parse_type >= 0.4.2",
        "six >= 1.11",
        "argparse; python_version < '2.7'",
        "importlib; python_version < '2.7'",
        "ordereddict; python_version < '2.7'",
        "traceback2; python_version < '3.0'",
        "enum34; python_version < '3.4'",
    ],
    test_suite="nose.collector",
    tests_require=[
        "pytest >= 3.0",
        "nose >= 1.3",
        "mock >= 1.1",
        "PyHamcrest >= 1.8",
        "path.py >= 10.1"
    ],
    cmdclass = {
        "behave_test": behave_test,
    },
    extras_require={
        'docs': ["sphinx >= 1.6", "sphinx_bootstrap_theme >= 0.6"],
        'develop': [
            "coverage", "pytest >= 3.0", "pytest-cov", "tox",
            "invoke >= 0.21.0", "path.py >= 8.1.2", "pycmd",
            "pathlib",  # python_version <= '3.4'
            "modernize >= 0.5",
            "pylint",
        ],
    },
    # MAYBE-DISABLE: use_2to3
    use_2to3= bool(python_version >= 3.0),
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: Jython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: BSD License",
    ],
    zip_safe = True,
)


