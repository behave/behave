import os
import os.path

from setuptools import find_packages, setup

setup(
    name='behave',
    version='1.0',
    description='A Cucumber-like BDD tool',
    author='Benno Rice',
    author_email='benno@jeamland.net',
    url='http://github.com/jeamland/behave',
    packages=find_packages(),
    package_data={'behave': ['languages.yml']},
    scripts=['bin/behave'],
    install_requires=['pyparsing>=1.5.0', 'PyYAML'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
)
