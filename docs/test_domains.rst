.. _id.appendix.test_domain:

Testing Domains
==============================================================================

Behave and other BDD frameworks allow you to provide **step libraries**
to reuse step definitions in similar projects that address the same
problem domain.

.. _behave:     https://github.com/behave/behave
.. _Selenium:   https://selenium.dev/


Step Libraries
------------------------------------------------------------------------------

Support of the following testing domains is currently known:

=============== ================= ===========================================================
Testing Domain   Name              Description
=============== ================= ===========================================================
Command-line    `behave4cmd`_     Test command-line tools, like behave, etc. (coming soon).
Web Apps        `behave-django`_  Test Django Web apps with behave (solution 1).
Web Apps        `django-behave`_  Test Django Web apps with behave (solution 2).
Web, SMS, ...   `behaving`_       Test Web Apps, Email, SMS, Personas (step library).
=============== ================= ===========================================================

.. _behave4cmd:     https://github.com/behave/behave4cmd
.. _behave-django: https://github.com/behave/behave-django
.. _behaving:       https://github.com/ggozad/behaving
.. _django-behave:  https://github.com/django-behave/django-behave



Step Usage Examples
------------------------------------------------------------------------------

This examples show how you can use `behave`_ for testing a specific problem domain.
This examples are normally not a full-blown step library (that can be reused),
but give you an example (or prototype), how the problem can be solved.

=============== ==================== ===========================================================
Testing Domain   Name                Description
=============== ==================== ===========================================================
GUI             `Squish test`_       Use `Squish and Behave`_ for GUI testing (cross-platform).
Robot Control   `behave4poppy`_      Use behave to control a robot via `pypot`_.
=============== ==================== ===========================================================

.. seealso::

    * google-search: `behave python example <https://www.google.com/?q=behave%20python%20example>`_


.. _behave4poppy:   https://github.com/chbrun/behave4poppy
.. _`Squish test`: https://www.qt.io/quality-assurance/squish
.. _`Squish and Behave`: https://qatools.knowledgebase.qt.io/squish/integrations/behave/bdd-squish-behave/
.. _pypot:          https://github.com/poppy-project/pypot
