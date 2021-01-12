@issue
Feature: Issue #309 -- behave --lang-list fails on Python3

  . When I type "behave --lang-list", the following error occurs on Python 3.4:
  .
  .   Traceback (most recent call last):
  .     File "/usr/local/bin/behave", line 11, in <module>
  .       sys.exit(main())
  .     File "/usr/local/lib/python3.4/dist-packages/behave/__main__.py", line 65, in main
  .       iso_codes.sort()
  .   AttributeError: 'dict_keys' object has no attribute 'sort'
  .
  . ADDITIONAL PROBLEM: On Python2 you may get an UnicodeDecodeError
  .   Traceback (most recent call last):
  .     ...
  .   Languages available:
  .     File "/Users/jens/se/behave_main.fix/behave/__main__.py", line 70, in main
  .       print(u'%s: %s / %s' % (iso_code, native, name))
  .   UnicodeEncodeError: 'ascii' codec can't encode characters in position 4-10: ordinal not in range(128)
  .
  . RELATED FEATURES:
  .  * features/cmdline.lang_list.feature
  .


  @problematic
  @not.with_os=win32
  Scenario: Use behave --lang-list
    When I run "behave --lang-list"
    Then it should pass with:
        """
        Languages available:
          af: Afrikaans / Afrikaans
          am: հայերեն / Armenian
          an: Aragonés / Aragonese
          ar: العربية / Arabic
          ast: asturianu / Asturian
          az: Azərbaycanca / Azerbaijani
          bg: български / Bulgarian
          bm: Bahasa Melayu / Malay
          bs: Bosanski / Bosnian
          ca: català / Catalan
          cs: Česky / Czech
          cy-GB: Cymraeg / Welsh
          da: dansk / Danish
          de: Deutsch / German
          el: Ελληνικά / Greek
          em: 😀 / Emoji
          en: English / English
        """
    And the command output should contain:
        """
        sv: Svenska / Swedish
        ta: தமிழ் / Tamil
        te: తెలుగు / Telugu
        th: ไทย / Thai
        tlh: tlhIngan / Klingon
        tr: Türkçe / Turkish
        tt: Татарча / Tatar
        uk: Українська / Ukrainian
        ur: اردو / Urdu
        uz: Узбекча / Uzbek
        vi: Tiếng Việt / Vietnamese
        zh-CN: 简体中文 / Chinese simplified
        zh-TW: 繁體中文 / Chinese traditional
        """
    But the command output should not contain "Traceback"
