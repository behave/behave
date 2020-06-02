Installation
============

Using pip (or ...)
------------------

:Category: Stable version
:Precondition: :pypi:`pip` (or :pypi:`setuptools`) is installed

Execute the following command to install :pypi:`behave` with :pypi:`pip`:

    pip install behave

To update an already installed :pypi:`behave` version, use:

    pip install -U behave


.. hint::

    See also `pip related information`_ for installing Python packages.

.. _`pip related information`:  https://pip.pypa.io/en/latest/installing/

Using Ubuntu 20.04
------------------

sudo apt install python3-behave

Using a Source Distribution
---------------------------

After unpacking the :pypi:`behave` source distribution,
enter the newly created directory "behave-<version>" and run::

    python setup.py install

    # OR:
    pip install .


Using the Github Repository
---------------------------

:Category: Bleeding edge
:Precondition: :pypi:`pip` is installed

Run the following command
to install the newest version from the `Github repository`_::


    pip install git+https://github.com/behave/behave

To install a tagged version from the `Github repository`_, use::

    pip install git+https://github.com/behave/behave@<tag>

where <tag> is the placeholder for an `existing tag`_.

.. _`Github repository`: https://github.com/behave/behave
.. _`existing tag`:      https://github.com/behave/behave/tags
