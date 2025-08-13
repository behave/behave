.. _id.appendix.test_domain:

Testing Domains
==============================================================================

Behave and other BDD frameworks allow you to provide **step libraries**
to reuse step definitions in similar projects that address the same
problem domain.

.. _behave:     https://github.com/behave/behave
.. _Selenium:   https://docs.seleniumhq.org/


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
Web             `pyramid_behave`_    Use `behave to test pyramid`_.
Web             `pycabara-tutorial`_ Use pycabara (with `behave`_ and `Selenium`_).
=============== ==================== ===========================================================

.. seealso::

    * google-search: `behave python example <https://www.google.com/?q=behave%20python%20example>`_


.. _behave4poppy:   https://github.com/chbrun/behave4poppy
.. _`Squish test`:  https://www.froglogic.com/squish/
.. _`Squish and Behave`: https://kb.froglogic.com/display/KB/BDD+with+Squish+and+Behave
.. _pycabara-tutorial:  https://github.com/excellaco/pycabara-tutorial
.. _pypot:          https://github.com/poppy-project/pypot
.. _pyramid_behave: https://github.com/wwitzel3/pyramid_behave
.. _`behave to test pyramid`:   https://blog.safaribooksonline.com/2014/01/10/using-behave-with-pyramid/
