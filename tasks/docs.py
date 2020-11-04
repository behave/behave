# -*- coding: UTF-8 -*-
"""
Provides tasks to build documentation with sphinx, etc.
"""

from __future__ import absolute_import, print_function
import os
import sys
from invoke import task, Collection
from invoke.util import cd
from path import Path

# -- TASK-LIBRARY:
# PREPARED: from invoke_cleanup import cleanup_tasks, cleanup_dirs
from .invoke_cleanup import cleanup_tasks, cleanup_dirs


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
SPHINX_LANGUAGE_DEFAULT = os.environ.get("SPHINX_LANGUAGE", "en")


# -----------------------------------------------------------------------------
# UTILTITIES:
# -----------------------------------------------------------------------------
def _sphinxdoc_get_language(ctx, language=None):
    language = language or ctx.config.sphinx.language or SPHINX_LANGUAGE_DEFAULT
    return language


def _sphinxdoc_get_destdir(ctx, builder, language=None):
    if builder == "gettext":
        # -- CASE: not LANGUAGE-SPECIFIC
        destdir = Path(ctx.config.sphinx.destdir or "build")/builder
    else:
        # -- CASE: LANGUAGE-SPECIFIC:
        language = _sphinxdoc_get_language(ctx, language)
        destdir = Path(ctx.config.sphinx.destdir or "build")/builder/language
    return destdir


# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
@task
def clean(ctx, dry_run=False):
    """Cleanup generated document artifacts."""
    basedir = ctx.sphinx.destdir or "build/docs"
    cleanup_dirs([basedir], dry_run=dry_run)


@task(help={
    "builder": "Builder to use (html, ...)",
    "language": "Language to use (en, ...)",
    "options": "Additional options for sphinx-build",
})
def build(ctx, builder="html", language=None, options=""):
    """Build docs with sphinx-build"""
    language = _sphinxdoc_get_language(ctx, language)
    sourcedir = ctx.config.sphinx.sourcedir
    destdir = _sphinxdoc_get_destdir(ctx, builder, language=language)
    destdir = destdir.abspath()
    with cd(sourcedir):
        destdir_relative = Path(".").relpathto(destdir)
        command = "sphinx-build {opts} -b {builder} -D language={language} {sourcedir} {destdir}" \
                    .format(builder=builder, sourcedir=".",
                            destdir=destdir_relative,
                            language=language,
                            opts=options)
        ctx.run(command)


@task(help={
    "builder": "Builder to use (html, ...)",
    "language": "Language to use (en, ...)",
    "options": "Additional options for sphinx-build",
})
def rebuild(ctx, builder="html", language=None, options=""):
    """Rebuilds the docs.
    Perform the steps: clean, build
    """
    clean(ctx)
    build(ctx, builder=builder, language=None, options=options)


@task(aliases=["auto", "watch"],
    help={
        "builder": "Builder to use (html, ...)",
        "language": "Language to use (en, ...)",
        "options": "Additional options for sphinx-build",
})
def autobuild(ctx, builder="html", language=None, options=""):
    """Build docs with sphinx-build"""
    language = _sphinxdoc_get_language(ctx, language)
    sourcedir = ctx.config.sphinx.sourcedir
    destdir = _sphinxdoc_get_destdir(ctx, builder, language=language)
    destdir = destdir.abspath()
    with cd(sourcedir):
        destdir_relative = Path(".").relpathto(destdir)
        command = "sphinx-autobuild {opts} -b {builder} -D language={language} {sourcedir} {destdir}" \
                    .format(builder=builder, sourcedir=".",
                            destdir=destdir_relative,
                            language=language,
                            opts=options)
        ctx.run(command)


@task
def linkcheck(ctx):
    """Check if all links are corect."""
    build(ctx, builder="linkcheck")


@task(aliases=["open"],
    help={"language": "Language to use (en, ...)"}
)
def browse(ctx, language=None):
    """Open documentation in web browser."""
    output_dir = _sphinxdoc_get_destdir(ctx, "html", language=language)
    page_html = Path(output_dir)/"index.html"
    if not page_html.exists():
        build(ctx, builder="html")
    assert page_html.exists()
    open_cmd = "open"   # -- WORKS ON: MACOSX
    if sys.platform.startswith("win"):
        open_cmd = "start"
    ctx.run("{open} {page_html}".format(open=open_cmd, page_html=page_html))
    # ctx.run('python -m webbrowser -t {page_html}'.format(page_html=page_html))
    # -- DISABLED:
    # import webbrowser
    # print("Starting webbrowser with page=%s" % page_html)
    # webbrowser.open(str(page_html))


@task(help={
    "dest": "Destination directory to save docs",
    "format": "Format/Builder to use (html, ...)",
    "language": "Language to use (en, ...)",
})
# pylint: disable=redefined-builtin
def save(ctx, dest="docs.html", format="html", language=None):
    """Save/update docs under destination directory."""
    print("STEP: Generate docs in HTML format")
    build(ctx, builder=format, language=language)

    print("STEP: Save docs under %s/" % dest)
    source_dir = Path(_sphinxdoc_get_destdir(ctx, format, language=language))
    Path(dest).rmtree_p()
    source_dir.copytree(dest)

    # -- POST-PROCESSING: Polish up.
    for part in [".buildinfo", ".doctrees"]:
        partpath = Path(dest)/part
        if partpath.isdir():
            partpath.rmtree_p()
        elif partpath.exists():
            partpath.remove_p()


@task(help={
    "language": 'Language to use, like "en" (default: "all" to build all).',
})
def update_translation(ctx, language="all"):
    """Update sphinx-doc translation(s) messages from the "English" docs.

    * Generates gettext *.po files in "build/docs/gettext/" directory
    * Updates/generates gettext *.po per language in "docs/LOCALE/{language}/"

    .. note:: Afterwards, the missing message translations can be filled in.

    :param language: Indicate which language messages to update (or "all").

    REQUIRES:

    * sphinx
    * sphinx-intl >= 0.9

    .. seealso:: https://github.com/sphinx-doc/sphinx-intl
    """
    if language == "all":
        # -- CASE: Process/update all support languages (translations).
        DEFAULT_LANGUAGES = os.environ.get("SPHINXINTL_LANGUAGE", None)
        if DEFAULT_LANGUAGES:
            # -- EXAMPLE: SPHINXINTL_LANGUAGE="de,ja"
            DEFAULT_LANGUAGES = DEFAULT_LANGUAGES.split(",")
        languages = ctx.config.sphinx.languages or DEFAULT_LANGUAGES
    else:
        # -- CASE: Process only one language (translation use case).
        languages = [language]

    # -- STEP: Generate *.po/*.pot files w/ sphinx-build -b gettext
    build(ctx, builder="gettext")

    # -- STEP: Update *.po/*.pot files w/ sphinx-intl
    if languages:
        gettext_build_dir = _sphinxdoc_get_destdir(ctx, "gettext").abspath()
        docs_sourcedir = ctx.config.sphinx.sourcedir
        languages_opts = "-l "+ " -l ".join(languages)
        with ctx.cd(docs_sourcedir):
            ctx.run("sphinx-intl update -p {gettext_dir} {languages}".format(
                    gettext_dir=gettext_build_dir.relpath(docs_sourcedir),
                    languages=languages_opts))
    else:
        print("OOPS: No languages specified (use: SPHINXINTL_LANGUAGE=...)")


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection(clean, rebuild, linkcheck, browse, save, update_translation)
namespace.add_task(build, default=True)
namespace.add_task(autobuild)
namespace.configure({
    "sphinx": {
        # -- FOR TASKS: docs.build, docs.rebuild, docs.clean, ...
        "language": SPHINX_LANGUAGE_DEFAULT,
        "sourcedir": "docs",
        "destdir": "build/docs",
        # -- FOR TASK: docs.update_translation
        "languages": None,  # -- List of language translations, like: de, ja, ...
    }
})

# -- ADD CLEANUP TASK:
cleanup_tasks.add_task(clean, "clean_docs")
cleanup_tasks.configure(namespace.configuration())
