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
          en-tx: Texas / Texas
          eo: Esperanto / Esperanto
          es: español / Spanish
          et: eesti keel / Estonian
          fa: فارسی / Persian
          fi: suomi / Finnish
          fr: français / French
          ga: Gaeilge / Irish
          gj: ગુજરાતી / Gujarati
          gl: galego / Galician
          he: עברית / Hebrew
          hi: हिंदी / Hindi
          hr: hrvatski / Croatian
          ht: kreyòl / Creole
          hu: magyar / Hungarian
          id: Bahasa Indonesia / Indonesian
          is: Íslenska / Icelandic
          it: italiano / Italian
          ja: 日本語 / Japanese
          jv: Basa Jawa / Javanese
          ka: ქართველი / Georgian
          kn: ಕನ್ನಡ / Kannada
          ko: 한국어 / Korean
          lt: lietuvių kalba / Lithuanian
          lu: Lëtzebuergesch / Luxemburgish
          lv: latviešu / Latvian
          mk-Cyrl: Македонски / Macedonian
          mk-Latn: Makedonski (Latinica) / Macedonian (Latin)
          mn: монгол / Mongolian
          mr: मराठी / Marathi
          ne: नेपाली / Nepali
          nl: Nederlands / Dutch
          no: norsk / Norwegian
          pa: ਪੰਜਾਬੀ / Panjabi
          pl: polski / Polish
          pt: português / Portuguese
          ro: română / Romanian
          ru: русский / Russian
          sk: Slovensky / Slovak
          sl: Slovenski / Slovenian
          sr-Cyrl: Српски / Serbian
          sr-Latn: Srpski (Latinica) / Serbian (Latin)
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
