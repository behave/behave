#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
from fnmatch import fnmatch
import os.path
import shutil
import sys
import textwrap

__author__  = "Jens Engel"
__version__ = "0.1"



class Package(object):
    """
    Helper class to create pypi like directory structure in local filesystem.
    """
    PATTERNS = [ "*.zip", "*.7z", "*.tar.gz", "*.tar.bz2" ]
    HTML_INDEX_TEMPLATE = """\
<html>
<head><title>{title}</title></head>
<body>
<h1>{title}</h1>
<ul>
{packages}
</ul>
</body>
</html>
"""
    HTML_ITEM_TEMPLATE = '<li><a href="{package_url}">{package_name}</a></li>'

    def __init__(self, filename, name=None):
        if not name and filename:
            name = self.get_pkgname(filename)
        self.name  = name
        self.files = []
        if filename:
            self.files.append(filename)

    @staticmethod
    def get_pkgname(filename):
        return os.path.basename(filename).rsplit("-", 1)[0]

    @classmethod
    def isa(cls, filename):
        basename = os.path.basename(filename)
        for pattern in cls.PATTERNS:
            if basename.startswith("."):
                return False
            elif fnmatch(filename, pattern):
                return True
        return False

    def make_index(self, index_dir):
        index_filename = os.path.join(index_dir, "index.html")
        if not os.path.isdir(index_dir):
            os.makedirs(index_dir)

        parts = []
        for pkg_filename in self.files:
            pkg_name = os.path.basename(pkg_filename)
            if pkg_name == "index.html":
                pkg_name = os.path.basename(os.path.dirname(pkg_filename))
            else:
                pkg_name = os.path.splitext(pkg_name)[0]
                if pkg_name.endswith(".tar"):
                    pkg_name = os.path.splitext(pkg_name)[0]
            pkg_relpath  = os.path.relpath(pkg_filename, index_dir)
            item = self.HTML_ITEM_TEMPLATE.format(
                    package_name=pkg_name, package_url=pkg_relpath)
            parts.append(item)

        with open(index_filename, "w") as f:
            text = self.HTML_INDEX_TEMPLATE.format(
                            title=self.name, packages= "\n".join(parts))
            f.write(textwrap.dedent(text).strip())
            f.close()


def make_localpi(download_dir):
    """
    Create a pypi server like file structure below download directory.


    EXAMPLE BEFORE:
      +-- downloads/
           +-- alice-1.0.zip
           +-- alice-1.0.tar.gz
           +-- bob-1.3.0.tar.gz
           +-- bob-1.4.2.tar.gz
           +-- charly-1.0.tar.bz2

    EXAMPLE AFTERWARDS:
      +-- downloads/
           +-- simple/
           |      +-- alice/index.html   --> ../../alice-*.*
           |      +-- bob/index.html     --> ../../bob-*.*
           |      +-- charly/index.html  --> ../../charly-*.*
           +-- alice-1.0.zip
           +-- alice-1.0.tar.gz
           +-- bob-1.3.0.tar.gz
           +-- bob-1.4.2.tar.gz
           +-- charly-1.0.tar.bz2
    """
    if not os.path.isdir(download_dir):
        raise ValueError("No such directory: %r" % download_dir)

    pkg_rootdir = os.path.join(download_dir, "simple")
    if os.path.isdir(pkg_rootdir):
        shutil.rmtree(pkg_rootdir, ignore_errors=True)
    os.mkdir(pkg_rootdir)

    last_package = None
    packages = []
    for filename in sorted(os.listdir(download_dir)):
        if not Package.isa(filename):
            continue
        pkg_filepath = os.path.join(download_dir, filename)
        package = Package(pkg_filepath)
        if last_package:
            if package.name == last_package.name:
                # -- COLLECT SAME PACKAGE (other variant/version):
                last_package.files.append(pkg_filepath)
                continue
            else:
                # -- OTHER PACKAGE DETECTED: Process last package.
                index_dir = os.path.join(pkg_rootdir, last_package.name)
                last_package.make_index(index_dir)
                packages.append(last_package)
        last_package = package

    if last_package:
        # -- FINALLY: Process last package.
        index_dir = os.path.join(pkg_rootdir, last_package.name)
        last_package.make_index(index_dir)
        packages.append(last_package)

    # -- FINALLY:
    package = Package(None, "Local package index (localpi)")
    package.files = [ os.path.join(pkg_rootdir, pkg.name, "index.html")
                      for pkg in packages ]
    package.make_index(pkg_rootdir)

# -----------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    make_localpi(sys.argv[1])
