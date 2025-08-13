.. _id.appendix.runners:

========================
Runners
========================

:pypi:`behave` provides an extension point for builtin and user-defined test runners.

The following runners are currently supported:

======= =========================== ================================================================
Name    Runner Class                Description
======= =========================== ================================================================
default ``behave.runner:Runner``    The default test runner provided by :pypi:`behave`.
help    `---`                       Shows which runners are currently available in your context.
======= =========================== ================================================================

You specify a runner by using the ``-r <RUNNER>`` or ``--runner=<RUNNER>`` command-line option.
A ``<RUNNER>`` option value can be:

* a runner alias, defined in ``[behave.runners]`` section in the ``behave.ini`` config-file
* a scoped class name, like: ``<SCOPED_MODULE_NAME>:<RUNNER_CLASS_NAME>``

.. attention::

    If you provide an own test runner, you are in the inner parts of :pypi:`behave`:

    * You should know what you are doing.
    * Inner parts of :pypi:`behave` may change without notice.
    * While it is not intended to break your test runner implementation,
      changes in the inner parts of :pypi:`behave` may occur,
      that will break parts of your implementation.


User-Defined Runners
-----------------------

:pypi:`behave` allows you to provide your own test runner (class):

.. code-block:: bash
    :caption: SHELL

    # USING COMMAND-LINE OPTION: -r/--runner=<RUNNER>
    $ behave --runner=behave.runner:Runner ...

The usage of a user-defined runner can be simplified by providing an
alias name for it in the configuration file:

.. code-block:: ini
    :caption: FILE: behave.ini

    # ALIAS SUPPORTS: behave -r default ...
    [behave.runners]
    default = behave.runner:Runner

Use ``behave --runner=help`` to:

* Inspect which runners are currently defined/supported in your workspace
* Check if the runner definitions have a problem, like: `ModuleNotFoundError`

.. code-block:: shell
    :caption: SHELL

    $ behave --runner=help
    AVAILABLE RUNNERS:
      default  = behave.runner:Runner


DESIGN CONSTRAINTS:

* A runner class must implement the :class:`behave.api.runner.ITestRunner` :this_repo:`interface <behave/api/runner.py>`

.. tip::

    See also :this_repo:`features/runner.use_runner_class.feature` for more information.


Failure Syndromes with User-Defined Runners
---------------------------------------------

======================= =================== ==========================================================================
Exception               Failure Kinde       Description
======================= =================== ==========================================================================
``ModuleNotFoundError`` User Error          Python package with runner is probably not installed yet.
``ClassNotFoundError``  User or Devel Error Python package is installed but class is not found (maybe: misspelled).
``InvalidClassError``   Developer Error     Runner class is not valid (for one of several reaons).
======================= =================== ==========================================================================

There are a number of reasons why the ``InvalidClassError`` exception occurs, like:

* The :class:`~behave.api.runner.ITestRunner` interface is not implemented.
* The :class:`~behave.api.runner.ITestRunner` interface contract is broken.
* The :class:`~behave.api.runner.ITestRunner` interface is only partially.

.. tip::

    See also :this_repo:`features/runner.use_runner_class.feature` for more information
    and the different failure syndromes that may occur.
