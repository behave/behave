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
import os.path
import sys
INVOKE_MINVERSION = "1.4.0"
_setup.setup_path()
_setup.require_invoke_minversion(INVOKE_MINVERSION)

TOPDIR = os.path.join(os.path.dirname(__file__), "..")
TOPDIR = os.path.abspath(TOPDIR)
sys.path.insert(0, TOPDIR)

# -----------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------
import sys
from invoke import Collection

# -- TASK-LIBRARY:
# PREPARED: import invoke_cleanup as cleanup
from . import invoke_cleanup as cleanup
from . import docs
from . import test
from . import release
from . import develop


# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
# None


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.add_collection(Collection.from_module(docs))
namespace.add_collection(Collection.from_module(test))
namespace.add_collection(Collection.from_module(release))
namespace.add_collection(Collection.from_module(develop))

# -- ENSURE: python cleanup is used for this project.
cleanup.cleanup_tasks.add_task(cleanup.clean_python)

# -- INJECT: clean configuration into this namespace
namespace.configure(cleanup.namespace.configuration())
namespace.configure(test.namespace.configuration())
if sys.platform.startswith("win"):
    # -- OVERRIDE SETTINGS: For platform=win32, ... (Windows)
    from ._compat_shutil import which
    run_settings = dict(echo=True, pty=False, shell=which("cmd"))
    namespace.configure({"run": run_settings})
else:
    namespace.configure({"run": dict(echo=True, pty=True)})
