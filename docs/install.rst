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


Using a Source Distribution
---------------------------

After unpacking the :pypi:`behave` source distribution,
enter the newly created directory "behave-<version>" and run::

    python setup.py install

    # OR:
    pip install .


Using the GitHub Repository
---------------------------

:Category: Bleeding edge
:Precondition: :pypi:`pip` is installed

Run the following command
to install the newest version from the `GitHub repository`_::

    pip install git+https://github.com/behave/behave

To install a tagged version from the `GitHub repository`_, use::

    pip install git+https://github.com/behave/behave@<TAG>

where <TAG> is the placeholder for an `existing tag`_.

When installing extras, use ``<TAG>#egg=behave[...]``, e.g.::

    pip install git+https://github.com/behave/behave@v1.2.7.dev5#egg=behave[toml]

.. _`GitHub repository`: https://github.com/behave/behave
.. _`existing tag`:      https://github.com/behave/behave/tags


Optional Dependencies
---------------------

If needed, additional dependencies ("extras") can be installed using
``pip install`` with one of the following installation targets.

======================= ===================================================================
Installation Target     Description
======================= ===================================================================
``behave[docs]``        Include packages needed for building Behave's documentation.
``behave[develop]``     Optional packages helpful for local development.
``behave[formatters]``  Install formatters from `behave-contrib`_ to extend the list of
                        :ref:`formatters <id.appendix.formatters>` provided by default.
``behave[toml]``        Optional toml package to configure behave from 'toml' files,
                        like 'pyproject.toml' from `pep-518`_.
======================= ===================================================================

.. _`behave-contrib`: https://github.com/behave-contrib
.. _`pep-518`: https://peps.python.org/pep-0518/#tool-table


Specify Dependency to "behave"
------------------------------

Use the following recipe in the ``"pyproject.toml"`` config-file if:

* your project depends on `behave`_ and
* you use a ``version`` from the git-repository (or a ``git branch``)

EXAMPLE:

.. code-block:: toml

    # -- FILE: my-project/pyproject.toml
    # SCHEMA: Use "behave" from git-repository (instead of: https://pypi.org/ )
    #   "behave @ git+https://github.com/behave/behave.git@<TAG>"
    #   "behave @ git+https://github.com/behave/behave.git@<BRANCH>"
    #   "behave[VARIANT] @ git+https://github.com/behave/behave.git@<TAG>" # with VARIANT=develop, docs, ...
    # SEE: https://peps.python.org/pep-0508/

    [project]
    name = "my-project"
    ...
    dependencies = [
        "behave @ git+https://github.com/behave/behave.git@v1.2.7.dev5",
        # OR: "behave[develop] @ git+https://github.com/behave/behave.git@main",
        ...
    ]

.. _behave: https://github.com/behave/behave
