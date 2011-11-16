import os
import os.path

from setuptools import find_packages, setup

setup(
    name='behave',
    version='1.0',
    packages=find_packages(),
    scripts=['bin/behave'],
)
