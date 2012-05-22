import os
import os.path
import sys

from setuptools import find_packages, setup

requirements = ['parse>=1.3.3']
zip_safe = True
major, minor = sys.version_info[:2]
if major == 2 and minor < 7:
    requirements.append('argparse')
if major == 2 and minor < 6:
    requirements.append('simplejson')
if major == 3 and minor >= 3:
    # distribute appears to much with co_names in a way that Python 3.3
    # doesn't appreciate.
    zip_safe = False

description = ''.join(open('README.rst').readlines()[6:])

setup(
    name='behave',
    version='1.2.1',
    description='behave is behaviour-driven development, Python style',
    long_description=description,
    author='Benno Rice and Richard Jones',
    author_email='behave-users@googlegroups.com',
    url='http://github.com/jeamland/behave',
    packages=find_packages(),
    scripts=['bin/behave'],
    install_requires=requirements,
    use_2to3=True,
    zip_safe=zip_safe,
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
