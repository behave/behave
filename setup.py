import os
import os.path
import sys

from setuptools import find_packages, setup

requirements = ['parse>=1.1.5']
major, minor = sys.version_info[:2]
if major == 2 and minor < 7:
    requirements.append('argparse')
if major == 2 and minor < 6:
    requirements.append('simplejson')

# grab some useful information
from behave import __version__ as version
from behave import __doc__ as description
lines = description.splitlines()
summary = lines[0].strip()
description = '\n'.join(lines).strip()

setup(
    name='behave',
    version=version,
    description=summary,
    long_description=description,
    author='Benno Rice and Richard Jones',
    author_email='benno@jeamland.net',
    url='http://github.com/jeamland/behave',
    packages=find_packages(),
    scripts=['bin/behave'],
    install_requires=requirements,
    use_2to3=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
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
