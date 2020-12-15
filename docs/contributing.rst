Contributing
============

If you find a bug you can fix or want to contribute an enhancement you're
welcome to `open an issue`_ on GitHub or create a `pull request`_ directly.

.. _open an issue: https://github.com/behave/behave/issues
.. _pull request: https://github.com/behave/behave/pulls

Using ``invoke`` for Development
--------------------------------

For most development tasks we have `invoke`_ commands.

Install all requirements for running tasks using Pip, e.g.

.. code-block:: console

    python3 -m pip install -r tasks/py.requirements.txt

Display all available ``invoke`` commands like this:

.. code-block:: console

    invoke -l

If you're curious, all ``invoke`` tasks are located in the ``tasks/``
folder.

.. _invoke: https://www.pyinvoke.org/

Update Gherkin Language Specification
-------------------------------------

An ``invoke`` command will download the latest Gherkin language
specification and update the `behave/i18n.py`_ module:

.. code-block:: console

    invoke develop.update-gherkin

If there were changes this command will have updated two files:

#. ``etc/gherkin/gherkin-languages.json`` (original Cucumber JSON spec)
#. ``behave/i18n.py`` (Python module generated from the JSON spec)

Put both under version control and open a PR to merge them.

.. _behave/i18n.py:
    https://github.com/behave/behave/blob/master/behave/i18n.py

Update Documentation
--------------------

Our documentation is written in `reStructuredText`_, and built and hosted
on `ReadTheDocs`_. Make your changes to the files in the ``docs/`` folder
and build the documentation with:

.. code-block:: console

    invoke docs

or, alternatively, using Tox:

.. code-block:: console

    tox -e docs

.. hint::

    Building the docs requires Sphinx and DocUtils. If your build fails
    because those are missing, run:

    .. code-block:: console

        python3 -m pip install -r py.requirements/docs.txt

Once the docs are built successfully, ``sphinx`` will tell you where it
generated the HTML output (typically ``build/docs/html``), which you can
then inspect locally.

.. _reStructuredText:
    https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _ReadTheDocs: https://readthedocs.org/
