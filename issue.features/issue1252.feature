@issue
@use.with_python.min_version=3.9
@not.with_python.implementation=pypy
Feature: Issue #1252 -- Wrong encoding of Unicode text (czech diacritics) in html report

  . DESCRIPTION:
  .   The HTML output of features/steps in czech language are garbled,
  .   meaning the Unicode code points were wrong (in Python3)
  .   and some czech characters were no longer readable.
  .
  . SEE ALSO:
  .   * https://github.com/behave/behave/issues/1252

  Rule: Using Czech
    Background:
      Given a new working directory
      And a file named "features/steps/czech_steps.py" using encoding="UTF-8" with:
        """
        from behave import when, then

        @when(u'zadám větu "{veta}"')
        def step_impl(ctx, veta):
            pass

        @then(u'je věta zapsána v reportu správně')
        def step_impl(ctx):
            raise Exception("Diakritika v reportu není správně zapsána.")
        """
      And a file named "features/1252_czech.feature" using encoding="UTF-8" with:
        """
        # language: cs
        Požadavek: Podpora českých znaků v behave-pretty-html-formatter reportu
          Scénář: Zadání české věty s diakritikou
            Když zadám větu "Loď čeří kýlem tůň obzvlášť v Grónské úžině"
            Pak je věta zapsána v reportu správně
        """

  @use.with_os=aix
  @use.with_os=cygwin
  @use.with_os=darwin
  @use.with_os=linux
  Scenario: Syndrome on other platforms with locale="cs_cz.cp1250" (UNIX like)
    When I run "behave -f plain -o output/1252_czech.output features/1252_czech.feature" with locale="cs_cz.cp1250"
    Then it should fail with:
      """
      0 scenarios passed, 0 failed, 1 error, 0 skipped
      1 step passed, 0 failed, 1 error, 0 skipped
      """
    And the file "output/1252_czech.output" with encoding="cp1250" should contain:
      """
      Když zadám větu "Loď čeří kýlem tůň obzvlášť v Grónské úžině"
      """
    And the file "output/1252_czech.output" with encoding="cp1250" should contain:
      """
      Požadavek: Podpora českých znaků v behave-pretty-html-formatter reportu
        Scénář: Zadání české věty s diakritikou
      """
    And the file "output/1252_czech.output" with encoding="cp1250" should contain:
      """
      raise Exception("Diakritika v reportu není správně zapsána.")
      """

  @xfail
  @use.with_os=win32
  Scenario: Syndrome on Windows platform with Czech
    Given I setup the console encoding to "cp1250"
    When I run "behave -f plain -o output/1252_czech.output -f plain features/1252_czech.feature" with locale="cs_cz.cp1250"
    Then it should fail with:
      """
      0 scenarios passed, 0 failed, 1 error, 0 skipped
      1 step passed, 0 failed, 1 error, 0 skipped
      """
    And the file "output/1252_czech.output" with encoding="cp1250" should contain:
      """
      Když zadám větu "Loď čeří kýlem tůň obzvlášť v Grónské úžině"
      """
    And the file "output/1252_czech.output" with encoding="cp1250" should contain:
      """
      Požadavek: Podpora českých znaků v behave-pretty-html-formatter reportu
        Scénář: Zadání české věty s diakritikou
      """
    And the file "output/1252_czech.output" with encoding="cp1250" should contain:
      """
      raise Exception("Diakritika v reportu není správně zapsána.")
      """


  Rule: Using German
    Background:
      Given a new working directory
      And a file named "features/steps/german_steps.py" using encoding="UTF-8" with:
        """
        from behave import when, then

        @when(u'ich den Satz "{sentence}" eingebe')
        def step_when_i_enter_the_sentence(ctx, sentence):
            ctx.sentence = sentence

        # is the sentence written correctly in the report
        @then(u'ist der Satz im Report korrect geschrieben (mit Sonderzeichen: "äöüß")')
        def step_then_sentence_is_written_correctly_in_report(ctx):
            raise Exception("Diacritics Problem: {};".format(ctx.sentence))
            # The diacritics in the report are not written correctly.
        """
      # Feature: Support for Czech characters in behave-pretty-html-formatter report
      #   Scenario: Entering a Czech sentence with diacritics
      #     When I enter the sentence "A ship churns up a pool with its keel, especially in the Greenland Strait"
      #     Then the sentence is written correctly in the report
      And a file named "features/1252_german.feature" using encoding="UTF-8" with:
        """
        # language: de
        Funktionalität: Unterstützung von deutschen Sonderzeichen
          Szenario: Deutsche Sonderzeichen -- Ärger ist immer und Überall
            Wenn ich den Satz "Fränkische Bäckereien verkaufen süße Brötchen mit Zimt und Äpfeln" eingebe
            Dann ist der Satz im Report korrect geschrieben (mit Sonderzeichen: "äöüß")
        """
        # -- ALTERNATIVES:
        #   Käufer äußerten Bedenken über die Größe des hübsch möblierten Zimmers
        #   Wenn ich den Satz "Ärger mir Örebug und Jürgen's Bierfaß" eingebe

  @use.with_os=aix
  @use.with_os=cygwin
  @use.with_os=darwin
  @use.with_os=linux
  Scenario: Syndrome on other platforms with locale="de_DE.cp1250" (UNIX like)
    When I run "behave -f plain -o output/1252_german.output features/1252_german.feature" with locale="de_DE.cp1250"
    Then it should fail with:
      """
      0 scenarios passed, 0 failed, 1 error, 0 skipped
      1 step passed, 0 failed, 1 error, 0 skipped
      """
    And the file "output/1252_german.output" with encoding="cp1250" should contain:
      """
      Wenn ich den Satz "Fränkische Bäckereien verkaufen süße Brötchen mit Zimt und Äpfeln" eingebe
      """
    And the file "output/1252_german.output" with encoding="cp1250" should contain:
      """
      Funktionalität: Unterstützung von deutschen Sonderzeichen
        Szenario: Deutsche Sonderzeichen -- Ärger ist immer und Überal
      """
    And the file "output/1252_german.output" with encoding="cp1250" should contain:
      """
          raise Exception("Diacritics Problem: {};".format(ctx.sentence))
      Exception: Diacritics Problem: Fränkische Bäckereien verkaufen süße Brötchen mit Zimt und Äpfeln;
      """
    # -- DISABLED:
    # And the command output should contain:
    #   """
    #   Errored scenarios:
    #     features/1252_german.feature:3  Deutsche Sonderzeichen -- Ärger ist immer und Überall
    #   """
    # And the chardet file encoding for "output/1252_german.output" should be "cp1250"

  @xfail
  @use.with_os=win32
  Scenario: Syndrome on Windows platform with German
    Given I setup the console encoding to "cp1250"
    When I run "behave -f plain -o output/1252_german.output features/1252_german.feature" with locale="de_DE.cp1250"
    Then it should fail with:
      """
      0 scenarios passed, 0 failed, 1 error, 0 skipped
      1 step passed, 0 failed, 1 error, 0 skipped
      """
    And the file "output/1252_german.output" with encoding="cp1250" should contain:
      """
      Wenn ich den Satz "Fränkische Bäckereien verkaufen süße Brötchen mit Zimt und Äpfeln" eingebe
      """
    And the file "output/1252_german.output" with encoding="cp1250" should contain:
      """
      Funktionalität: Unterstützung von deutschen Sonderzeichen
        Szenario: Deutsche Sonderzeichen -- Ärger ist immer und Überal
      """
    And the file "output/1252_german.output" with encoding="cp1250" should contain:
      """
          raise Exception("Diacritics Problem: {};".format(ctx.sentence))
      Exception: Diacritics Problem: Fränkische Bäckereien verkaufen süße Brötchen mit Zimt und Äpfeln;
      """
