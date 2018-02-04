# -*- coding: UTF-8 -*-
# pylint: disable=wrong-import-position, wrong-import-order
"""
Invoke build script.
Show all tasks with::

    invoke -l

.. seealso::

    * http://pyinvoke.org
    * https://github.com/pyinvoke/invoke
"""

from __future__ import absolute_import

# -----------------------------------------------------------------------------
# BOOTSTRAP PATH: Use provided vendor bundle if "invoke" is not installed
# -----------------------------------------------------------------------------
from . import _setup    # pylint: disable=wrong-import-order
INVOKE_MINVERSION = "0.14.0"
_setup.setup_path()
_setup.require_invoke_minversion(INVOKE_MINVERSION)

# -----------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------
import sys
from invoke import Collection

# -- TASK-LIBRARY:
from . import clean
from . import docs
from . import test
from . import release

# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
# None


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection()
namespace.add_task(clean.clean)
namespace.add_task(clean.clean_all)
namespace.add_collection(Collection.from_module(docs))
namespace.add_collection(Collection.from_module(test))
namespace.add_collection(Collection.from_module(release))

# -- INJECT: clean configuration into this namespace
namespace.configure(clean.namespace.configuration())
if sys.platform.startswith("win"):
    # -- OVERRIDE SETTINGS: For platform=win32, ... (Windows)
    from ._compat_shutil import which
    run_settings = dict(echo=True, pty=False, shell=which("cmd"))
    namespace.configure({"run": run_settings})
