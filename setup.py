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
requirements = ["parse>=1.6.3", "parse_type>=0.3.4", "six>=1.9"]
py26_extra = ["argparse", "importlib", "ordereddict", "enum34", "traceback2"]
py27_extra = ["enum34", "traceback2"]
py33_extra = ["enum34"]
if python_version < 2.6:
    requirements.append("simplejson")
if python_version < 2.7:
    requirements.extend(py26_extra)
if python_version < 3:
    requirements.extend(py27_extra)
if python_version >= 3.0 and python_version < 3.4:
    requirements.extend(py33_extra)

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
    version="1.2.6.dev0",
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
    install_requires=requirements,
    test_suite="nose.collector",
    tests_require=["nose>=1.3", "mock>=1.0", "PyHamcrest>=1.8", "pytest>=2.8"],
    cmdclass = {
        "behave_test": behave_test,
    },
    extras_require={
        # -- SUPPORT-WHEELS: Extra packages for Python2.6
        # SEE: https://bitbucket.org/pypa/wheel/ , CHANGES.txt (v0.24.0)
        ':python_version=="2.6"': py26_extra,
        ':python_version=="2.7"': py27_extra,
        ':python_version=="3.3"': py33_extra,
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


