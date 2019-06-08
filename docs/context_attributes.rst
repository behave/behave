.. _id.appendix.context_attributes:

==============================================================================
Context Attributes
==============================================================================

A context object (:class:`~behave.runner.Context`) is handed to

  * step definitions (step implementations)
  * behave hooks (:func:`before_all`, :func:`before_feature`, ..., :func:`after_all`)


Behave Attributes
-------------------------

The :pypi:`behave` runner assigns a number of attributes to the context object
during a test run.

=============== ========= ============================================= ====================================================================
Attribute Name  Layer     Type                                          Description
=============== ========= ============================================= ====================================================================
config          test run  :class:`~behave.configuration.Configuration`  Configuration that is used.
aborted         test run  bool                                          Set to true if test run is aborted by the user.
failed          test run  bool                                          Set to true if a step fails.
feature         feature   :class:`~behave.model.Feature`                Current feature.
rule            rule      :class:`~behave.model.Feature`                Current rule.
tags            feature,  list<:class:`~behave.model.Tag`>              Effective tags of current feature, rule, scenario, scenario outline.
                rule,
                scenario
active_outline  scenario  :class:`~behave.model.Row`                    Current row in a scenario outline (in examples table).
                outline
scenario        scenario  :class:`~behave.model.Scenario`               Current scenario.
log_capture     scenario  :class:`~behave.log_capture.LoggingCapture`   If logging capture is enabled.
stdout_capture  scenario  :class:`~StringIO.StringIO`                   If stdout  capture is enabled.
stderr_capture  scenario  :class:`~StringIO.StringIO`                   If stderr  capture is enabled.
table           step      :class:`~behave.model.Table`                  Contains step's table, otherwise None.
text            step      String                                        Contains step's multi-line text (unicode), otherwise None.
=============== ========= ============================================= ====================================================================

.. note::

    `Behave attributes`_ in the context object should not be modified by a user.
    See :class:`~behave.runner.Context` class description for more details.

.. hidden:

    TODO: Add rule

User Attributes
-------------------------

A user can assign (or modify) own attributes to the context object.
But these attributes will be removed again from the context object depending
where these attributes are defined.

======= =========================== ==========================
Kind    Assign Location             Lifecycle Layer (Scope)
======= =========================== ==========================
Hook    :func:`before_all`          test run
Hook    :func:`after_all`           test run
Hook    :func:`before_tags`         feature, rule or scenario
Hook    :func:`after_tags`          feature, rule or scenario
Hook    :func:`before_feature`      feature
Hook    :func:`after_feature`       feature
Hook    :func:`before_rule`         rule
Hook    :func:`after_rule`          rule
Hook    :func:`before_scenario`     scenario
Hook    :func:`after_scenario`      scenario
Hook    :func:`before_step`         scenario
Hook    :func:`after_step`          scenario
Step    Step definition             scenario
======= =========================== ==========================

