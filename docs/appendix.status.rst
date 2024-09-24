.. _id.appendix.status:

==============================================================================
Status Values
==============================================================================

The :class:`behave.model_core.Status` enum-class provides

====================== ===============================================================================
Status                  Description
====================== ===============================================================================
`untested`              INITIAL VALUE (before test if executed).
`untested_pending`      RESERVED: Pending steps can not be detected in dry-run mode.
`untested_undefined`    Used for undefined steps, detected in dry-run mode.
`skipped`               Used if a model element is skipped (not part of the run set).
`passed`                Used if a model element has passed successfully.
`failed`                Used if a failure occurred: assert-mismatch.
`error`                 Used if an error occurs, normally a unexpected exception is raised.
`hook_error`            Used if a hook fails (with exception or assert-mismatch).
`pending`               Used for pending steps (as error).
`pending_warn`          Used for pending steps (as passed step with `@wip` tag).
`undefined`             Used for undefined steps (as error).
====================== ===============================================================================


Common Status Values
------------------------

The following status values are used for:

* Features
* Rules
* Scenarios
* Steps

====================== ========= ========
Status                  Error?   Failed?
====================== ========= ========
`untested`                no
`skipped`                 no
`passed`                  no
`failed`                  no        yes
`error`                   yes
`hook_error`              yes
====================== ========= ========


Specific Status Values for Steps
---------------------------------

The following status values are only used for steps.

====================== ========= ========= ========= ============
Status                  Error?   Untested? Pending?  Undefined?
====================== ========= ========= ========= ============
`untested_pending`        no        yes      yes        no
`untested_undefined`      no        yes      no         yes
`pending`                 yes       no       yes        no
`pending_warn`            no        no       yes        no
`undefined`               yes       no       no         yes
====================== ========= ========= ========= ============


From Inner Status to Outer Status
---------------------------------

The following table provides an overview how the outer status is derived
from the status of contained model elements.

EXAMPLE:

* `hook_error` on a step leads to `error` in scenario.

====================== =============== ===============================================================
Inner Status           Outer Status     Description
====================== =============== ===============================================================
`untested`              `untested`      If no `passed` occurs.
`untested_pending`      `untested`      Like `untested`.
`untested_undefined`    `untested`      Like `untested`.
`skipped`               `skipped`       Same.
`passed`                `passed`        Same.
`failed`                `failed`        Same.
`error`                 `error`         Same.
`hook_error`            `error`
`pending`               `error`
`pending_warn`          `passed`
`undefined`             `error`
====================== ===============================================================================


.. include:: _common_extlinks.rst
