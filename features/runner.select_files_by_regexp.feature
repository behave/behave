@sequential
Feature: Select feature files by using regular expressions

  As a tester
  I want to include/exclude feature files into/from a test run by using wildcards
  To be more flexible and avoid to specify all feature files

  . SPECIFICATION:
  .  * behave provides --include and --exclude command line options
  .  * --include option selects a subset of all files that should be included
  .  * --exclude option is applied after include option is applied
  .
  . EXAMPLE:
  .     behave --include="features/ali.*\.feature" ...
  .     behave --exclude="features/ali.*" ...


    Background:
        Given behave has the following feature fileset:
            """
            features/alice.feature
            features/bob.feature
            features/barbi.feature
            """

    Scenario: Include only feature files
        When behave includes feature files with "features/a.*"
        And  behave excludes no feature files
        Then the following feature files are selected:
            """
            features/alice.feature
            """

    Scenario: Include more than one feature file
        When behave includes feature files with "features/b.*"
        Then the following feature files are selected:
        """
        features/bob.feature
        features/barbi.feature
        """


    Scenario: Exclude only feature files
        When behave excludes feature files with "features/a.*"
        And  behave includes all feature files
        Then the following feature files are selected:
            """
            features/bob.feature
            features/barbi.feature
            """

    Scenario: Exclude more than one feature file
        When behave excludes feature files with "features/b.*"
        Then the following feature files are selected:
        """
        features/alice.feature
        """

    Scenario: Include and exclude feature files

      Ensure that exclude file pattern is applied after include file pattern.

        When behave includes feature files with "features/.*a.*\.feature"
        And  behave excludes feature files with ".*/barbi.*"
        Then the following feature files are selected:
            """
            features/alice.feature
            """

    Scenario: Include and exclude feature files (in 2 steps)

      Show how file inclusion/exclusion works by emulating the two steps.

        When behave includes feature files with "features/.*a.*\.feature"
        Then the following feature files are selected:
            """
            features/alice.feature
            features/barbi.feature
            """
        When behave excludes feature files with ".*/barbi.*"
        Then the following feature files are selected:
            """
            features/alice.feature
            """
