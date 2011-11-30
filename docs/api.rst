====================
behave API reference
====================


Step File Decorators
--------------------

Environment File Functions
--------------------------

The environment.py module may define code to run before and after certain
events during your testing:

**before_step(context, step), after_step(context, step)**
  These run before and after every step.
**before_scenario(context, scenario), after_scenario(context, scenario)**
  These run before and after each scenario is run.
**before_feature(context, feature), after_feature(context, feature)**
  These run before and after each feature file is exercised.
**before_tag(context, tag), after_tag(context, tag)**
  These run before and after a section tagged with the given name. They are
  invoked for each tag encountered in the order they're found in the
  feature file. See  `controlling things with tags`_.
**before_all(context), after_all(context)**
  These run before and after the whole shooting match.


Model Objects
-------------

The feature, scenario and step objects represent the information parsed
from the feature file. They have a number of common attributes:

**keyword**
  "Feature", "Scenario", "Given", etc.
**name**
  The name of the step (the text after the keyword.)
**filename** and **line**
  The file name (or "<string>") and line number of the statement.

The structure of model objects parsed from a *feature file* will typically
be:

.. parsed-literal::

    :class:`~behave.model.Feature` 
        :class:`~behave.model.Tag` 
        :class:`~behave.model.Background` 
        :class:`~behave.model.Scenario` 
           :class:`~behave.model.Tag` 
           :class:`~behave.model.Step` 
              :class:`~behave.model.Table` 
        :class:`~behave.model.ScenarioOutline` 
           :class:`~behave.model.Tag` 
           :class:`~behave.model.Examples` 
              :class:`~behave.model.Table` 
           :class:`~behave.model.Step` 
              :class:`~behave.model.Table` 

.. autoclass:: behave.model.Feature

.. autoclass:: behave.model.Background

.. autoclass:: behave.model.Scenario

.. autoclass:: behave.model.ScenarioOutline

.. autoclass:: behave.model.Examples

.. autoclass:: behave.model.Step

Tables may be associated with either Examples or Steps:

.. autoclass:: behave.model.Table

.. autoclass:: behave.model.Tag

.. _`controlling things with tags`: tutorial.html#controlling-things-with-tags

