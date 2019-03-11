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
          en-Scouse: Scouse / Scouse
          en-au: Australian / Australian
          en-lol: LOLCAT / LOLCAT
          en-old: Englisc / Old English
          en-pirate: Pirate / Pirate
          eo: Esperanto / Esperanto
          es: español / Spanish
          et: eesti keel / Estonian
          fa: فارسی / Persian
          fi: suomi / Finnish
          fr: français / French
        """
    And the command output should contain:
        """
        sv: Svenska / Swedish
        ta: தமிழ் / Tamil
        th: ไทย / Thai
        tl: తెలుగు / Telugu
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
