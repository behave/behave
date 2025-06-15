from behave._stepimport import SimpleStepContainer, use_step_import_modules
from tests.functional.error import SomeError


# ----------------------------------------------------------------------------
# TEST SUPPORT -- Steps
# ----------------------------------------------------------------------------
def load_steps_into_step_registry():
    # -- REGISTER EXAMPLE STEPS:
    step_container = SimpleStepContainer()
    with use_step_import_modules(step_container):
        from behave import step
        @step(u'{name} passes')
        @step(u'{name} passes with output')
        def step_passes_with_output(ctx, name):
            print("CALLED: {}".format(name))

        @step(u'{name} without output')
        @step(u'{name} passes without output')
        def step_passes_without_output(ctx, name):
            pass

        @step(u'{name} fails with failed')
        def step_fails_with_assert(ctx, name):
            print("BAD_CALLED: {}".format(name))
            raise AssertionError("OOPS, FAILED in {}".format(name))

        @step(u'{name} fails with error')
        def step_fails_with_error(ctx, name):
            print("BAD_CALLED: {}".format(name))
            # raise SomeError("OOPS: FAILED")
            raise SomeError("OOPS, FAILED in {}".format(name))
    return step_container.step_registry
