.. _id.appendix.environment_variables:

==============================================================================
Environment Variables
==============================================================================

`behave`_ uses the following environment variables:

=========================================== ===============================================================================
Environment Variable                        Description
=========================================== ===============================================================================
BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON      Gherkin parser strips trailing colon from steps in Gherkin file (if enabled).
                                            This is only the case, if a step has a text/table section.
=========================================== ===============================================================================


=========================================== =========== ================ =======================
Environment Variable                        Type        Values           Default Value
=========================================== =========== ================ =======================
BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON      bool        ``yes``, ``no``  ``no``
=========================================== =========== ================ =======================


.. include:: _common_extlinks.rst
