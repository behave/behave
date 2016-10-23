# -*- coding: UTF-8 -*-
"""
Provides tasks to build documentation with sphinx, etc.
"""

from __future__ import absolute_import, print_function
from invoke import task, Collection
from invoke.util import cd
from path import Path
import os.path
import sys

# -- TASK-LIBRARY:
from .clean import cleanup_tasks, cleanup_dirs

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
    "options": "Additional options for sphinx-build",
})
def build(ctx, builder="html", options=""):
    """Build docs with sphinx-build"""
    sourcedir = ctx.config.sphinx.sourcedir
    destdir = Path(ctx.config.sphinx.destdir or "build")/builder
    destdir = destdir.abspath()
    with cd(sourcedir):
        destdir_relative = Path(".").relpathto(destdir)
        command = "sphinx-build {opts} -b {builder} {sourcedir} {destdir}" \
                    .format(builder=builder, sourcedir=".",
                            destdir=destdir_relative, opts=options)
        ctx.run(command)

@task
def linkcheck(ctx):
    """Check if all links are corect."""
    build(ctx, builder="linkcheck")

@task
def browse(ctx):
    """Open documentation in web browser."""
    page_html = Path(ctx.config.sphinx.destdir)/"html"/"index.html"
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

@task(help = {"dest": "Destination directory to save docs"})
def save(ctx, dest="docs.html", format="html"):
    """Save/update docs under destination directory."""
    print("STEP: Generate docs in HTML format")
    build(ctx, builder=format)

    print("STEP: Save docs under %s/" % dest)
    source_dir = Path(ctx.config.sphinx.destdir)/format
    Path(dest).rmtree_p()
    source_dir.copytree(dest)

    # -- POST-PROCESSING: Polish up.
    for part in [ ".buildinfo", ".doctrees" ]:
        partpath = Path(dest)/part
        if partpath.isdir():
            partpath.rmtree_p()
        elif partpath.exists():
            partpath.remove_p()

# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection(clean, linkcheck, browse, save)
namespace.add_task(build, default=True)
namespace.configure({
    "sphinx": {
        "sourcedir": "docs",
        "destdir": "build/docs"
    }
})

# -- ADD CLEANUP TASK:
cleanup_tasks.add_task(clean, "clean_docs")
cleanup_tasks.configure(namespace.configuration())
