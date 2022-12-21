from behave import use_fixture
from fixtures import fixture_map


def before_tag(context, tag):
    tag_parts = tag.split(".", 1)
    if tag_parts[0] == "fixture":
        if len(tag_parts) > 1:
            try:
                use_fixture(fixture_map[tag_parts[1]], context)
            except:
                pass
