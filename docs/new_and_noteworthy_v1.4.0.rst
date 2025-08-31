Noteworthy in Version 1.4.0
==============================================================================

Remove Support for Tag-Expressions v1
-------------------------------------------------------------------------------

* Tag-Expressions v1 are supersed by :ref:`Tag-Expressions v2 <id.tag_expressions>`.
* Support for Tag-Expressions v1 was removed.
* Use :ref:`Tag-Expressions v2 <id.tag_expressions>` instead.

AFFECTED: By this change

* The :option:`--tags` command-line option and config-file parameter :confval:`tags : text`
  and :confval:`default_tags : text` has now the type ``text`` (was: ``sequence<text>``).
* The :option:`--tags` command-line option can now be used only once.

.. seealso::

    SEE: :ref:`id.tag_expressions` for details.

.. include:: _common_extlinks.rst
