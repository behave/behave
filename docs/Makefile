# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
UPDATE        = ./update_behave_rst.py
SPHINXBUILD   = $(UPDATE) && sphinx-build
PAPER         =
LANGUAGE      = en
BUILDDIR      = ../build/docs
# BUILDDIR      = ../build/docs/$(LANGUAGE)

# -D language=en

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
LANGOPT = -D language=$(LANGUAGE)
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees/$(LANGUAGE) $(PAPEROPT_$(PAPER)) $(LANGOPT) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html dirhtml singlehtml pickle json htmlhelp qthelp devhelp epub latex latexpdf text man changes linkcheck doctest gettext

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  dirhtml    to make HTML files named index.html in directories"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  pickle     to make pickle files"
	@echo "  json       to make JSON files"
	@echo "  htmlhelp   to make HTML files and a HTML help project"
	@echo "  qthelp     to make HTML files and a qthelp project"
	@echo "  devhelp    to make HTML files and a Devhelp project"
	@echo "  epub       to make an epub"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  text       to make text files"
	@echo "  man        to make manual pages"
	@echo "  texinfo    to make Texinfo files"
	@echo "  info       to make Texinfo files and run them through makeinfo"
	@echo "  gettext    to make PO message catalogs"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck  to check all external links for integrity"
	@echo "  doctest    to run all doctests embedded in the documentation (if enabled)"

clean:
	-rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html/$(LANGUAGE)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html/$(LANGUAGE)."

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml/$(LANGUAGE)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml/$(LANGUAGE)."

singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml/$(LANGUAGE)
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml/$(LANGUAGE)."

pickle:
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) $(BUILDDIR)/pickle/$(LANGUAGE)
	@echo
	@echo "Build finished; now you can process the pickle files."

json:
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(BUILDDIR)/json/$(LANGUAGE)
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) $(BUILDDIR)/htmlhelp/$(LANGUAGE)
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in $(BUILDDIR)/htmlhelp/$(LANGUAGE)."

qthelp:
	$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS) $(BUILDDIR)/qthelp/$(LANGUAGE)
	@echo
	@echo "Build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in $(BUILDDIR)/qthelp/$(LANGUAGE), like this:"
	@echo "# qcollectiongenerator $(BUILDDIR)/qthelp/$(LANGUAGE)/behave.qhcp"
	@echo "To view the help file:"
	@echo "# assistant -collectionFile $(BUILDDIR)/qthelp/$(LANGUAGE)/behave.qhc"

devhelp:
	$(SPHINXBUILD) -b devhelp $(ALLSPHINXOPTS) $(BUILDDIR)/devhelp/$(LANGUAGE)
	@echo
	@echo "Build finished."
	@echo "To view the help file:"
	@echo "# mkdir -p $$HOME/.local/share/devhelp/behave/$(LANGUAGE)"
	@echo "# ln -s $(BUILDDIR)/devhelp/$(LANGUAGE) $$HOME/.local/share/devhelp/behave/$(LANGUAGE)"
	@echo "# devhelp"

epub:
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) $(BUILDDIR)/epub/$(LANGUAGE)
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub/$(LANGUAGE)."

latex:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex/$(LANGUAGE)
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex/$(LANGUAGE)."
	@echo "Run \`make' in that directory to run these through (pdf)latex" \
	      "(use \`make latexpdf' here to do that automatically)."

latexpdf:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex/$(LANGUAGE)
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex/$(LANGUAGE) all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex/$(LANGUAGE)."

text:
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text/$(LANGUAGE)
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text/$(LANGUAGE)."

man:
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(BUILDDIR)/man
	@echo
	@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

texinfo:
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS) $(BUILDDIR)/texinfo/$(LANGUAGE)
	@echo
	@echo "Build finished. The Texinfo files are in $(BUILDDIR)/texinfo/$(LANGUAGE)."
	@echo "Run \`make' in that directory to run these through makeinfo" \
	      "(use \`make info' here to do that automatically)."

info:
	$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS) $(BUILDDIR)/texinfo/$(LANGUAGE)
	@echo "Running Texinfo files through makeinfo..."
	make -C $(BUILDDIR)/texinfo/$(LANGUAGE) info
	@echo "makeinfo finished; the Info files are in $(BUILDDIR)/texinfo/$(LANGUAGE)."

gettext:
	$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale/$(LANGUAGE)
	@echo
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale/$(LANGUAGE)."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes/$(LANGUAGE)
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes/$(LANGUAGE)."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck/$(LANGUAGE)
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck//$(LANGUAGE)/output.txt."

doctest:
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest/$(LANGUAGE)
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest//$(LANGUAGE)/output.txt."
