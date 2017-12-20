Feature: Command-line options: Use behave --lang-list

  As a user
  I want to determine which languages are supported by behave
  So that I can use the language code in feature files or command lines

  @problematic
  @not.with_os=win32
  Scenario: Use behave --lang-list
    When I run "behave --lang-list"
    Then it should pass with:
        """
        Languages available:
         ar: العربية / Arabic
         bg: български / Bulgarian
         ca: català / Catalan
         cs: Česky / Czech
         cy-GB: Cymraeg / Welsh
         da: dansk / Danish
         de: Deutsch / German
         en: English / English
        """
    And the command output should contain:
        """
        sv: Svenska / Swedish
        tr: Türkçe / Turkish
        uk: Українська / Ukrainian
        uz: Узбекча / Uzbek
        vi: Tiếng Việt / Vietnamese
        zh-CN: 简体中文 / Chinese simplified
        zh-TW: 繁體中文 / Chinese traditional
        """
    But the command output should not contain "Traceback"
