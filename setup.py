import os
import os.path
import sys

from setuptools import find_packages, setup
# DISABLED, use VERSION.txt now: from behave.version import VERSION
VERSION = open("VERSION.txt").read().strip()

requirements = ['parse>=1.3.3', "distribute" ]
major, minor = sys.version_info[:2]
if major == 2 and minor < 7:
    requirements.append('argparse')
if major == 2 and minor < 6:
    requirements.append('simplejson')

description = ''.join(open('README.rst').readlines()[6:])

setup(
    name='behave',
    version=VERSION,
    description='behave is behaviour-driven development, Python style',
    long_description=description,
    author='Benno Rice and Richard Jones, patched by JE',
    author_email='behave-users@googlegroups.com',
    url='http://github.com/jeamland/behave',
    packages=find_packages(),
    # -- DISABLED: Use console_scripts for platform independence (Windows, ...)
    # scripts=['bin/behave'],
    entry_points={
        'console_scripts': [
            'behave = behave.main:main',
        ]
    },
    install_requires=requirements,
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: Jython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: BSD License",
    ],
)
