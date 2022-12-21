from behave import given, when, then, step

from helper import *


@then("there will be {count:d} secrets detected")
def step_impl(context, count):
    assert context.found == count, (
        "Expected "
        + str(count)
        + " secret"
        + ("s" if count != 1 else "")
        + ", found "
        + str(context.found)
    )


@then("there will be {count:d} unique secrets detected")
def step_impl(context, count):
    assert context.found_unique == count, (
        "Expected "
        + str(count)
        + " secret"
        + ("s" if count != 1 else "")
        + ", found "
        + str(context.found_unique)
    )
