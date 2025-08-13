# -- ISSUE #678: Support tags with commas and semicolons.

import os.path
from behave import given, when


@given('I create a symlink from "{source}" to "{dest}"')
@when('I create a symlink from "{source}" to "{dest}"')
def step_create_symlink(context, source, dest):
    print("symlink: %s -> %s" % (source, dest))
    # assert os.path.exists(source), "FILE-NOT-FOUND: source=%s" % source

    # -- VARIANT 1:
    text = 'When I run "ln -s {source} {dest}"'.format(source=source, dest=dest)
    context.execute_steps(text)

    # -- VARIANT 2:
    # SINCE: Python 3.x (support for Windows and target_is_directory=...)
    if False:
        source_is_dir = os.path.isdir(source)
        if source_is_dir:
            os.symlink(source, dest, target_is_directory=source_is_dir)

