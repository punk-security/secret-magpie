from behave import use_fixture
from fixtures import fixture_map

import helper
import shutil
import os
import time


def before_tag(context, tag):
    tag_parts = tag.split(".")
    match tag_parts[0].lower():
        case "fixture":
            if len(tag_parts) > 1:
                try:
                    use_fixture(fixture_map[tag_parts[1]], context)
                except:
                    pass

        case "localrepos":
            context.repo_type = "local"

        case "github":
            context.repo_type = "github"
            context.org = tag_parts[1]

            # PAT is provided via environment variables
            context.pat = os.environ["SECRETMAGPIE_GITHUB_PAT"]

        case "gitlab":
            context.repo_type = "gitlab"
            context.org = tag_parts[1]

            # PAT is provided via environment variables
            context.pat = os.environ["SECRETMAGPIE_GITLAB_PAT"]

        case "azuredevops":
            context.repo_type = "azuredevops"
            context.org = tag_parts[1]

            # PAT is provided via environment variables
            context.pat = os.environ["SECRETMAGPIE_ADO_PAT"]

        case "bitbucket":
            context.repo_type = "bitbucket"
            context.workspace = tag_parts[1]

            # Credentials are provided via environment variables
            context.username = os.environ["SECRETMAGPIE_BITBUCKET_USERNAME"]
            context.password = os.environ["SECRETMAGPIE_BITBUCKET_PASSWORD"]

        case "no-cleanup":
            try:
                context.args
            except:
                context.args = []

            context.args.append("--no-cleanup")


def after_tag(context, tag):
    tag_parts = tag.split(".")
    match tag_parts[0].lower():
        case "rmtree":
            for i in range(0, 3):
                try:
                    shutil.rmtree(tag_parts[1], onerror=helper.onerror)
                    break
                except:
                    time.sleep(10)
                    continue
