Nested Steps
===============================================================================

This example is used to explore nested step modules.
Nested step modules occur if:

* The "steps" directory contains other nested directories with Python files
* The "steps" directory contains subdirectories that are Python packages

Supporting nested step modules caused the following problems:

* Python packages may contain relative-imports, like: `from . import other`
* Python packages with relative-imports are broken/do-not-work,
  if this package or modules of this package are imported as steps module.

NOTES:

* Python packages do not belong in the steps directory.
* Python package belong somewhere on the Python search path
  (either by being installed, installed in a virtual-environment or
   by using the `PYTHONPATH` environment variable to specify a Python search path).

EXAMPLE:

```
HERE/features/steps/
    +-- some_package/
    |       +-- __init__.py
    |       +-- charly_steps.py
    |       +-- other.py
    |       +-- use_relative_imports.py
    +-- alice_steps.py
    +-- bob_steps.py
    +-- use_steplib_behave4cmd0.py
```

SYNDROME:

```bash
$ ../../bin/behave features/f1.feature
USING RUNNER: behave.runner:Runner
Exception KeyError: "'__name__' not in globals"
...
```
