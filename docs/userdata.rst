.. _docid.userdata:

==================
Userdata
==================

The userdata functionality allows a user to specify owm parameters and values
(or more complex configuration data) to the test run.

Overview
========

Userdata can be provided in three ways:

  * As command-line options: ``-D name=value`` or ``--define name=value``
  * In the behave configuration file under section ``[behave.userdata]``
  * Loaded programmatically in the ``before_all()`` hook

.. note::

    Command-line definitions take precedence over configuration file settings.
    Therefore, command-line defintions override userdata parameters in the config-file.


Basic Usage
===========

Configuration File
-------------------

Define userdata in your configuration file:

.. code-block:: ini
    :caption: FILE: behave.ini

    [behave.userdata]
    browser = firefox
    server  = asterix

Alternatively, if using ``pyproject.toml``:

.. code-block:: toml
    :caption: FILE: pyproject.toml

    [tool.behave.userdata]
    browser = "firefox"
    server = "asterix"

Command Line
------------

Override or provide userdata via command-line:

.. code-block:: bash

    # Provide specific values
    behave -D server=obelix features/
    behave --define browser=chrome features/

    # Boolean flags (value becomes "true")
    behave -D debug_mode features/

.. note::

    If the command-line contains no value part,
    like ``-D NEEDS_CLEANUP``, its value becomes ``"true"`` (as boolean value).


Accessing Userdata
-------------------

Access userdata in your hooks and steps using the ``context.config.userdata`` dictionary:

.. code-block:: python
    :caption: FILE: features/environment.py

    def before_all(context):
        browser = context.config.userdata.get("browser", "chrome")
        setup_browser(browser)

.. code-block:: python
    :caption: FILE: features/steps/userdata_example_steps.py

    @given('I setup the system with the user-specified server"')
    def step_setup_system_with_userdata_server(context):
        server_host = context.config.userdata.get("server", "beatrix")
        context.xxx_client = xxx_protocol.connect(server_host)

Other examples for user-specific data are:

* Passing a URL to an external resource that should be used in the tests
* Turning off cleanup mechanisms implemented in environment hooks, for debugging purposes.

Type Converters
===============

The userdata object provides basic type conversion methods, similar to the
`configparser <https://docs.python.org/3/library/configparser.html#module-configparser>`_ module:

* ``Userdata.getint(name, default=0)``
* ``Userdata.getfloat(name, default=0.0)``
* ``Userdata.getbool(name, default=False)``
* ``Userdata.getas(convert_func, name, default=None, ...)``

.. note::

    Type conversion may raise a ``ValueError`` exception if the conversion fails.

Example
-------------

.. code-block:: python
    :caption: FILE: features/environment.py

    def before_all(context):
        userdata = context.config.userdata
        server_name  = userdata.get("server", "beatrix")
        int_number   = userdata.getint("port", 80)
        bool_answer  = userdata.getbool("are_you_sure", True)
        float_number = userdata.getfloat("temperature_threshold", 50.0)
        ...

.. hidden:

  * :py:meth:`behave.configuration.Userdata.getint()`
  * :py:meth:`behave.configuration.Userdata.getfloat()`
  * :py:meth:`behave.configuration.Userdata.getbool()`
  * :py:meth:`behave.configuration.Userdata.getas()`

Advanced Use Cases
==================

Loading JSON Configuration
--------------------------

For complex configuration needs, you can load additional data from JSON files:

.. code-block:: python
    :caption: FILE: features/environment.py

    import json
    import os.path

    def before_all(context):
        """Load and update userdata from JSON configuration file."""
        userdata = context.config.userdata
        configfile = userdata.get("configfile", "userconfig.json")

        if os.path.exists(configfile):
            assert configfile.endswith(".json")
            with open(configfile) as f:
                more_userdata = json.load(f)
            context.config.update_userdata(more_userdata)
            # NOTE: Reapplies userdata_defines from command-line too

Create a JSON configuration file:

.. code-block:: json
    :caption: FILE: userconfig.json

    {
        "browser": "firefox",
        "server":  "asterix",
        "count":   42,
        "cleanup": true
    }

Then use it:

.. code-block:: bash
    :caption: SHELL

    behave -D configfile=userconfig.json features/




Configuration Profiles
-----------------------

Implement configuration profiles for different environments:

.. code-block:: python
    :caption: FILE: features/environment.py

    import json
    import os.path

    def before_all(context):
        profile = context.config.userdata.get("profile", "default")
        config_file = f"config/{profile}.json"

        if os.path.exists(config_file):
            with open(config_file) as f:
                profile_config = json.load(f)
            context.config.update_userdata(profile_config)

Usage:

.. code-block:: bash
    :caption: SHELL

    # -- EXAMPLE: Use different configuration profiles
    behave -D profile=staging features/
    behave -D profile=production features/
    behave -D profile=local features/
