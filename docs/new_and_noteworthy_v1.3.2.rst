Noteworthy in Version 1.3.2
==============================================================================

Support for Nested Step Modules
-------------------------------------------------------------------------------

Support for nested step modules inside of the ``steps`` directory was added in `behave v1.3.0`.

This functionality has caused some problems,
if Python package(s) are placed in the ``steps`` directory that uses relative-import statements.
Therefore, the loading of nested step module is disabled by default since this version.

An experienced user can enable this feature by providing:

.. code-block:: ini
    :caption: FILE: behave.ini

    [behave]
    use_nested_step_modules = true

.. seealso::

    * :this_repo:`features/runner.use_nested_step_modules.feature`
    * :this_repo:`features/runner.use_substep_dirs.feature` (RELATED: older solution)

.. hint::

    BEST PRACTICE:

    * Use a `step-library`_ instead.
    * DO NOT put Python packages in the ``steps`` directory.

    Python packages belong on the Python search path:

    * OPTION 0: Install the Python packages in a virtual environment (if ypu use one).
    * OPTION 1: Setup the Python search path by using the ``PYTHONPATH`` environment variable.
    * OPTION 2: Setup the Python search path in the ``features/environment.py`` file.

    SEE ALSO:

    * :this_repo:`features/step.use_step_library.feature`

.. _`step-library`: https://github.com/behave/behave/blob/main/features/step.use_step_library.feature

.. include:: _common_extlinks.rst
