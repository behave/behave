@issue
Feature: Issue #159: output stream is wrapped twice in the codecs.StreamWriter

  @setup
  Scenario: Feature Setup
    Given a new working directory
    And   a file named "features/steps/steps.py" with:
      """
      # -*- coding: utf-8 -*-
      from behave import step

      @step('firstname is "{name}"')
      def step_impl(context, name):
          pass

      @step(u'full name is Loïc "{name}"')
      def step_impl(context, name):
          pass
      """

  Scenario: Single feature, pass (a)
    Given a file named "features/issue159_stream_writer.feature" with:
      """
      Feature:
        Scenario:
          When firstname is "Loïc"
      """
    When I run "behave -f plain features/"
    Then it should pass


  Scenario: Single feature, pass (b)
    Given a file named "features/issue159_stream_writer.feature" with:
      """
      Feature:
        Scenario:
          When full name is Loïc "Dupont"
      """
    When I run "behave -f plain features/"
    Then it should pass


  Scenario: Two features, FAIL (a)
    Given a file named "features/issue159_stream_writer.feature" with:
      """
      Feature:
        Scenario:
          When full name is Loïc "Dupont"
      """
    And   a file named "features/issue159_stream_writer_again.feature" with:
      """
      Feature:
        Scenario:
          When full name is Loïc "Dupond"
      """
    When I run "behave -f plain features/"
    Then it should pass


  Scenario: Two features, FAIL (b)
    Given a file named "features/issue159_stream_writer.feature" with:
      """
      Feature:
        Scenario:
          When firstname is "Loïc"
      """
    And   a file named "features/issue159_stream_writer_again.feature" with:
      """
      Feature:
        Scenario:
          When firstname is "Loïc"
      """
    When I run "behave -f plain features/"
    Then it should pass
