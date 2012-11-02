#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copy a source directory recursively below a destination directory.
Similar to `cp -R srcdir destdir`.
"""

import os.path
import shutil
import sys

def copytree_main(args):
    """
    USAGE: copytree srcdir... destdir
    Copy one or more source-directory(s) below a destination-directory.
    Parts of the destination directory path are created if needed.
    Similar to the UNIX command: 'cp -R srcdir destdir'
    """
    if len(args) < 2:
        sys.stderr.write("COMMAND-LINE ERROR: copytree %s\n" % args)
        usage = "\n".join(line.strip()
            for line in copytree_main.__doc__.strip().splitlines())
        sys.stderr.write(usage + "\n")
        return 1
    # -- NORMAL CASE:
    # XXX sys.stdout.write("python.executable: %s\n" % sys.executable)
    # XXX sys.stdout.write("python.version: %s\n" % sys.version[:5])
    srcdirs  = args[:-1]
    destdir = args[-1]
    for srcdir in srcdirs:
        basename = os.path.basename(srcdir)
        destdir2 = os.path.normpath(os.path.join(destdir, basename))
        if os.path.exists(destdir2):
            shutil.rmtree(destdir2)

        sys.stdout.write("copytree: %s => %s\n" % (srcdir, destdir2))
        shutil.copytree(srcdir, destdir2)
    return 0

if __name__ == "__main__":
    sys.exit(copytree_main(sys.argv[1:]))