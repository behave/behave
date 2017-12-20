@issue
@unicode
Feature: UnicodeDecodeError in model.Step (when step fails)

  . Output of failing step contains non-ASCII characters.
  .
  . RELATED:
  .   * features/i18n.unicode_problems.feature


  @reuse.colocated_test
  Scenario:
      Given I use the current directory as working directory
      When I run "behave -f plain --tags=@setup,@problematic.output features/i18n.unicode_problems.feature"
      Then it should pass
