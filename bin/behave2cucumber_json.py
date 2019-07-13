#!/usr/bin/env python
# =============================================================================
# CONVERT: behave JSON dialect to cucumber JSON dialect
# =============================================================================
# STATUS: __PROTOTYPE__
# REQUIRES: Python >= 2.7
# REQUIRES: https://github.com/behalf-oss/behave2cucumber
# SEE:
# * https://github.com/behave/behave/issues/267#issuecomment-251746565
# =============================================================================
"""
Convert a file with behave JSON data into a file with cucumber JSON data.
Note that both JSON dialects differ slightly.
"""

from __future__ import print_function
import json
import sys
import os.path
try:
    import behave2cucumber
except ImportError:
    print("REQUIRE: https://github.com/behalf-oss/behave2cucumber")
    print("INSTALL: pip install behave2cucumber")
    sys.exit(2)


NAME = os.path.basename(__file__)


def convert_behave_to_cucumber_json(behave_filename, cucumber_filename,
                                    encoding="UTF-8", pretty=True):
    """Convert behave JSON dialect into cucumber JSON dialect.

    .. param behave_filename:       Input filename with behave JSON data.
    .. param cucumber_filename:     Output filename with cucumber JSON data.
    """
    dump_kwargs = {"encoding": encoding}
    if pretty:
        dump_kwargs.update(indent=2, sort_keys=True)

    with open(behave_filename, "r") as behave_json:
        with open(cucumber_filename, "w+") as output_file:
            behave_json = json.load(behave_json, encoding)
            cucumber_json = behave2cucumber.convert(behave_json)
            # cucumber_text = json.dumps(cucumber_json, **dump_kwargs)
            # output_file.write(cucumber_text)
            json.dump(cucumber_json, output_file, **dump_kwargs)
    return 0


def main(args=None):
    """Main function to run the script."""
    if args is None:
        args = sys.argv[1:]
    if len(args) != 2:
        print("USAGE: %s BEHAVE_FILE.json CUCUMBER_FILE.json" % NAME)
        print("Converts behave JSON dialect to cucumber JSON dialect.")
        return 1

    behave_filename = args[0]
    cucumber_filename = args[1]
    return convert_behave_to_cucumber_json(behave_filename, cucumber_filename)


# -- AUTO-MAIN:
if __name__ == "__main__":
    sys.exit(main())
