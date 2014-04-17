# -*- coding: utf-8 -*-
"""
Deprecated module. Functionality was split-up into:

  * behave.formatter._registry  (generic core functionality)
  * behave.formatter._builtins  (registration of known, builtin formatters)

.. since:: 1.2.5a1
    Deprecated, use "behave.formatter._registry" or "behave.formatter._builtin".
"""

from behave.formatter import _registry
import warnings

warnings.simplefilter("once", DeprecationWarning)
warnings.warn("Use 'behave.formatter._registry' instead.", DeprecationWarning)

# -----------------------------------------------------------------------------
# FORMATTER REGISTRY:
# -----------------------------------------------------------------------------
def register_as(formatter_class, name):
    """
    Register formatter class with given name.

    :param formatter_class:  Formatter class to register.
    :param name:  Name for this formatter (as identifier).
    """
    warnings.warn("Use behave.formatter._registry.register_as() instead.",
                  DeprecationWarning, stacklevel=2)
    _registry.register_as(name, formatter_class)


def register(formatter_class):
    register_as(formatter_class, formatter_class.name)


def get_formatter(config, stream_openers):
    warnings.warn("Use make_formatters() instead",
                  DeprecationWarning, stacklevel=2)
    return _registry.make_formatters(config, stream_openers)


# -----------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------
def setup_formatters():
<<<<<<< HEAD
    warnings.warn("Use behave.formatter._builtins instead",
                  DeprecationWarning, stacklevel=2)
    from behave.formatter import _builtins
    _builtins.setup_formatters()
=======
    # -- NOTE: Use lazy imports for formatters (to speed up start-up time).
    _L = LazyObject
    register_as(_L("behave.formatter.plain:PlainFormatter"), "plain")
    register_as(_L("behave.formatter.pretty:PrettyFormatter"), "pretty")
    register_as(_L("behave.formatter.json:JSONFormatter"), "json")
    register_as(_L("behave.formatter.json:PrettyJSONFormatter"), "json.pretty")
    register_as(_L("behave.formatter.null:NullFormatter"), "null")
    register_as(_L("behave.formatter.progress:ScenarioProgressFormatter"),
                "progress")
    register_as(_L("behave.formatter.progress:StepProgressFormatter"),
                "progress2")
    register_as(_L("behave.formatter.progress:ScenarioStepProgressFormatter"),
                "progress3")
    register_as(_L("behave.formatter.rerun:RerunFormatter"), "rerun")
    register_as(_L("behave.formatter.tags:TagsFormatter"), "tags")
    register_as(_L("behave.formatter.tags:TagsLocationFormatter"),
                "tags.location")
    register_as(_L("behave.formatter.steps:StepsFormatter"), "steps")
    register_as(_L("behave.formatter.steps:StepsDocFormatter"), "steps.doc")
    register_as(_L("behave.formatter.steps:StepsUsageFormatter"), "steps.usage")
    register_as(_L("behave.formatter.sphinx_steps:SphinxStepsFormatter"),
                "sphinx.steps")
    register_as(_L("behave.formatter.html:HTMLFormatter"), "html")
>>>>>>> HTML Formatter


# -----------------------------------------------------------------------------
# MODULE-INIT:
# -----------------------------------------------------------------------------
# DISABLED: setup_formatters()
