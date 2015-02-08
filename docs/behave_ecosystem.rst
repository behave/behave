.. _id.appendix.behave_ecosystem:

Behave Ecosystem
==============================================================================

The following tools and extensions try to simplify the work with `behave`_.

.. _behave: https://github.com/behave/behave

.. seealso::

    * `Are there any non-developer tools for writing Gherkin files ?
      <http://stackoverflow.com/questions/8275026/are-there-any-non-developer-tools-to-edit-gherkin-files>`_
      (``*.feature`` files)


IDE Plugins
------------------------------------------------------------------------------

=============== =================== ======================================================================================
IDE             Plugin              Description
=============== =================== ======================================================================================
`PyCharm`_      `PyCharm BDD`_      PyCharm 4 (Professional edition) has **built-in support** for `behave`_.
`PyCharm`_      Gherkin             PyCharm/IDEA editor support for Gherkin.
`Eclipse`_      `Cucumber-Eclipse`_ Plugin contains editor support for Gherkin.
`VisualStudio`_ `cuke4vs`_          VisualStudio plugin with editor support for Gherkin.
=============== =================== ======================================================================================

.. _PyCharm:        http://www.jetbrains.com/pycharm/
.. _Eclipse:        http://eclipse.org/
.. _VisualStudio:   http://www.visualstudio.com/

.. _`PyCharm BDD`:  http://www.jetbrains.com/pycharm/whatsnew/#BDD
.. _`PyCharm BDD details`: http://blog.jetbrains.com/pycharm/2014/09/feature-spotlight-behavior-driven-development-in-pycharm/
.. _`Cucumber-Eclipse`: http://cucumber.github.io/cucumber-eclipse/
.. _cuke4vs:        https://github.com/henritersteeg/cuke4vs




Editors and Editor Plugins
------------------------------------------------------------------------------

=================== ======================= =============================================================================
Editor              Plugin                  Description
=================== ======================= =============================================================================
`gedit`_            `gedit_behave`_         `gedit`_ plugin for jumping between feature and step files.
`Gherkin editor`_   ---                     An editor for writing ``*.feature`` files.
`Notepad++`_        `NP++ gherkin`_         Notepad++ editor syntax highlighting for Gherkin.
`Sublime Text`_     `Cucumber (ST Bundle)`_ Gherkin editor support, table formatting.
`Sublime Text`_     `Behave Step Finder`_   Helps to navigate to steps in behave.
`vim`_              `vim-behave`_           `vim`_ plugin: Port of `vim-cucumber`_ to Python `behave`_.
=================== ======================= =============================================================================

.. _`Notepad++`: http://www.notepad-plus-plus.org
.. _gedit:  https://wiki.gnome.org/Apps/Gedit
.. _vim:    http://www.vim.org/
.. _`Sublime Text`:    http://www.sublimetext.com

.. _`Gherkin editor`: http://gherkineditor.codeplex.com
.. _gedit_behave:   https://gitorious.org/cucutags/gedit_behave
.. _`NP++ gherkin`: http://productive.me/develop/cucumbergherkin-syntax-highlighting-for-notepad
.. _vim-behave:     https://gitorious.org/cucutags/vim-behave
.. _vim-cucumber:   https://github.com/tpope/vim-cucumber
.. _`Cucumber (ST Bundle)`:    https://packagecontrol.io/packages/Cucumber
.. _Behave Step Finder: https://packagecontrol.io/packages/Behave%20Step%20Finder


Tools
------------------------------------------------------------------------------

=========================== ===========================================================================
Tool                        Description
=========================== ===========================================================================
`cucutags`_                 Generate `ctags`_-like information (cross-reference index)
                            for Gherkin feature files and behave step definitions.
=========================== ===========================================================================

.. _cucutags:   https://gitorious.org/cucutags/cucutags/
.. _ctags:      http://ctags.sourceforge.net/

