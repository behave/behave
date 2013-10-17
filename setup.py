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
sys.path.insert(0, os.curdir)

from setuptools import find_packages, setup
from setuptools_behave import behave_test

requirements = ['parse>=1.6.2']
zip_safe = True
major, minor = sys.version_info[:2]
if major == 2 and minor < 7:
    requirements.append('argparse')
    requirements.append('importlib')
if major == 2 and minor < 6:
    requirements.append('simplejson')

description = ''.join(open('README.rst').readlines()[5:])

setup(
    name='behave',
    version='1.2.4a1',
    description='behave is behaviour-driven development, Python style',
    long_description=description,
    author='Benno Rice, Richard Jones and Jens Engel',
    author_email='behave-users@googlegroups.com',
    url='http://github.com/behave/behave',
    packages=find_packages(exclude=[
        "test", "test.*",
        "behave4cmd0", "behave4cmd0.*"]),
    entry_points={
        'console_scripts': [
            'behave = behave.__main__:main'
        ],
        'distutils.commands': [
            'behave_test = setuptools_behave:behave_test'
        ]
    },
    install_requires=requirements,
    test_suite='nose.collector',
    tests_require=['nose>=1.3', 'mock>=1.0', 'PyHamcrest>=1.7.2'],
    cmdclass = {
        'behave_test': behave_test,
    },
    use_2to3=True,
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: Jython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: BSD License",
    ],
)


