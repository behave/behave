======================
Flask Test Integration
======================

Integrating your `Flask`_ application with :pypi:`behave` is done via
boilerplate code in your ``environment.py`` file.

The `Flask documentation on testing`_ explains how to use the Werkzeug test
client for running tests in general.

.. _Flask: http://flask.pocoo.org/
.. _Flask documentation on testing: http://flask.pocoo.org/docs/1.0/testing/

Integration Example
===================

The example below is an integration boilerplate derived from the official
Flask documentation, featuring the `Flaskr sample application`_ from the Flask
tutorial.

.. code-block:: python

    # -- FILE: features/environment.py
    import os
    import tempfile
    from behave import fixture, use_fixture
    # flaskr is the sample application we want to test
    from flaskr import app, init_db

    @fixture
    def flaskr_client(context, *args, **kwargs):
        context.db, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        context.client = app.test_client()
        with app.app_context():
            init_db()
        yield context.client
        # -- CLEANUP:
        os.close(context.db)
        os.unlink(app.config['DATABASE'])

    def before_feature(context, feature):
        # -- HINT: Recreate a new flaskr client before each feature is executed.
        use_fixture(flaskr_client, context)


Taken and adapted from Ismail Dhorat's `BDD testing example on Flaskr`_.

.. _Flaskr sample application: http://flask.pocoo.org/docs/dev/tutorial/introduction/
.. _BDD testing example on Flaskr: https://github.com/ismaild/flaskr-bdd


Strategies and Tooling
======================

See :ref:`id.practicaltips` for automation libraries and implementation tips
on your BDD tests.
