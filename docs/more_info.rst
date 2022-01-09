.. _id.appendix.more_info:

More Information about Behave
==============================================================================


Tutorials
------------------------------------------------------------------------------

For new users, that want to read, understand and explore the concepts in Gherkin
and `behave`_ (after reading the behave documentation):

* "`Behave by Example <http://behave.github.io/behave.example/>`_"
  (on `github <https://github.com/behave/behave.example>`_)

The following small tutorials provide an introduction how you use `behave`_
in a specific testing domain:

* Phillip Johnson, `Getting Started with Behavior Testing in Python with Behave`_, 2015-10-15.
* Nicole Harris, `Beginning BDD with Django`_ (part 1 and 2), 2015-03-16.
* TestingBot, `Bdd with Python, Behave and WebDriver`_
* Wayne Witzel III, `Using Behave with Pyramid`_, 2014-01-10.

.. _`Getting Started with Behavior Testing in Python with Behave`: https://semaphoreci.com/community/tutorials/getting-started-with-behavior-testing-in-python-with-behave
.. _`Beginning BDD with Django`: https://whoisnicoleharris.com/2015/03/16/bdd-part-one.html
.. _`Bdd with Python, Behave and WebDriver`: https://testingbot.com/support/getting-started/behave.html
.. _`Using Behave with Pyramid`: https://active6.blogspot.com/2014/01/using-behave-with-pyramid.html

.. warning::

    A word of caution if you are new to **"behaviour-driven development" (BDD)**.
    In general, you want to avoid "user interface" (UI) details in your
    scenarios, because they describe **how something is implemented**
    (in this case the UI itself), like:

    * ``press this button``
    * then ``enter this text into the text field``
    * ...

    In **BDD** (or testing in general), you should describe **what should be done**
    (meaning the intention). This will make your scenarios much more robust
    and stable because you can change the underlying implementation of:

    * the "system under test" (SUT) or
    * the test automation layer, that interacts with the SUT.

    without changing the scenarios.


Books
------------------------------------------------------------------------------

`Behave`_ is covered in the following books:

..

    [TDD-Python] Harry Percival,
    `Test-Driven Web Development with Python`_, O'Reilly, June 2014,
    `Appendix E: BDD <http://chimera.labs.oreilly.com/books/1234000000754/ape.html>`_
    (covers behave)

.. _`Test-Driven Web Development with Python`: http://chimera.labs.oreilly.com/books/1234000000754


Presentation Videos
------------------------------------------------------------------------------

* Benno Rice: `Making Your Application Behave`_ (30min),
  2012-08-12, PyCon Australia.

* Selenium: `First behave python tutorial with selenium`_ (8min), 2015-01-28,
  http://www.seleniumframework.com/python-basic/first-behave-gherkin/

* Jessica Ingrasselino: `Automation with Python and Behave`_ (67min), 2015-12-16

* `Selenium Python Webdriver Tutorial - Behave (BDD)`_ (14min), 2016-01-21

* `Front-end integration testing with splinter`_ (30min), 2017-08-05


.. hidden:

    PREPARED:
    ---------------------

    .. ifconfig:: not supports_video

        * Benno Rice: `Making Your Application Behave`_ (30min),
          PyCon Australia, 2012-08-12

        * Selenium: `First behave python tutorial with selenium`_ (8min), 2015-01-28,
          http://www.seleniumframework.com/python-basic/first-behave-gherkin/

        * Jessica Ingrasselino: `Automation with Python and Behave`_ (67min), 2015-12-16

        * `Selenium Python Webdriver Tutorial - Behave (BDD)`_ (14min), 2016-01-21

        * `Front-end integration testing with splinter`_ (30min), 2017-08-05


        .. hint::

            Manually install `sphinxcontrib-youtube`_
            (from "youtube" subdirectory in sphinx-extensions bundle)
            to have embedded videos on this page (when this page is build).


    .. ifconfig:: supports_video

        Benno Rice: `Making Your Application Behave`_
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        :Conference: PyCon Australia
        :Date: 2012-08-12
        :Duration: 30min

        ..  youtube:: u8BOKuNkmhg
            :width: 600
            :height: 400

        Selenium: `First behave python tutorial with selenium`_
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        :Date: 2015-01-28
        :Duration: 8min

        ..  youtube:: D24_QrGUCFk
            :width: 600
            :height: 400

        RELATED: http://www.seleniumframework.com/python-basic/what-is-python/

        Jessica Ingrasselino: `Automation with Python and Behave`_
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        :Date: 2015-12-16
        :Duration: 67min

        ..  youtube:: e78c7h6DRDQ
            :width: 600
            :height: 400

        `Selenium Python Webdriver Tutorial - Behave (BDD)`_
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        :Date: 2016-01-21
        :Duration: 14min

        ..  youtube:: mextSo0UExc
            :width: 600
            :height: 400

        Nick Coghlan: `Front-end integration testing with splinter`_
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        :Date: 2017-08-05
        :Duration: 30min

        ..  youtube:: HY0_RtTUfUg
            :width: 600
            :height: 400


.. _`Making Your Application Behave`: https://www.youtube.com/watch?v=u8BOKuNkmhg
.. _`First behave python tutorial with selenium`: https://www.youtube.com/watch?v=D24_QrGUCFk
.. _`Automation with Python and Behave`: https://www.youtube.com/watch?v=e78c7h6DRDQ
.. _`Selenium Python Webdriver Tutorial - Behave (BDD)`: https://www.youtube.com/watch?v=mextSo0UExc
.. _`Front-end integration testing with splinter`: https://pyvideo.org/pycon-au-2017/front-end-integration-testing-with-splinter.html

.. _sphinxcontrib-youtube: https://bitbucket.org/birkenfeld/sphinx-contrib


Tool-oriented Tutorials
------------------------------------------------------------------------------

JetBrains PyCharm:

* Blog: `In-Depth Screencast on Testing`_ (2016-04-11; video offset=2:10min)
* Docs: `BDD Testing Framework Support in PyCharm 2016.1
  <https://www.jetbrains.com/help/pycharm/2016.1/bdd-testing-framework.html>`_


.. _`Getting Started with PyCharm`: https://www.youtube.com/playlist?list=PLQ176FUIyIUZ1mwB-uImQE-gmkwzjNLjP
.. _`PyCharm In-Depth: Testing`: https://youtu.be/nmBbR97Vsv8?list=PLQ176FUIyIUZ1mwB-uImQE-gmkwzjNLjP
.. _`In-Depth Screencast on Testing`: https://blog.jetbrains.com/pycharm/2016/04/in-depth-screencast-on-testing/



Find more Information
------------------------------------------------------------------------------

.. seealso::

    * google:`python-behave examples <https://www.google.com/?q=python-behave%20examples>`_
    * google:`python-behave tutorials <https://www.google.com/?q=python-behave%20tutorials>`_
    * google:`python-behave videos <https://www.google.com/?q=python-behave%20videos>`_


.. _Behave:     https://github.com/behave/behave
.. _behave:     https://github.com/behave/behave
.. _Selenium:   http://docs.seleniumhq.org/
.. _behave4cmd:     https://github.com/behave/behave4cmd
.. _behave-django: https://github.com/behave/behave-django
