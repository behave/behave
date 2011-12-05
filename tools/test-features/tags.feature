@spam
Feature: handle tags
  Tags may be set at various levels in various ways.

  Scenario: nothing changes
    Given the tag "spam" is set

  @ham @cram
  Scenario: adding the ham
    Given the tag "spam" is set
      and the tag "ham" is set
      and the tag "cram" is set

  @ham
  Scenario: adding the ham
    Given the tag "spam" is set
      and the tag "ham" is set
      and the tag "cram" is not set
