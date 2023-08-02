import argparse
import math
from os import linesep, environ, cpu_count
import sys

runtime = environ.get("SM_COMMAND", f"{sys.argv[0]}")

banner = """\
          ____              __   _____                      _ __       
         / __ \__  ______  / /__/ ___/___  _______  _______(_) /___  __
        / /_/ / / / / __ \/ //_/\__ \/ _ \/ ___/ / / / ___/ / __/ / / /
       / ____/ /_/ / / / / ,<  ___/ /  __/ /__/ /_/ / /  / / /_/ /_/ / 
      /_/    \__,_/_/ /_/_/|_|/____/\___/\___/\__,_/_/  /_/\__/\__, /  
                                             PRESENTS         /____/  
                              Secret-Magpie ✨

      Scan all your github/bitbucket repos from one tool, with multiple tools!
        """

cores = cpu_count()
if cores is None or cores == 0:
    parallel = 1
else:
    parallel = math.ceil(cores / 4)


class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stdout.write(f" ❌ error: {message}{linesep}{linesep}")
        self.print_usage()
        sys.exit(2)


parser = CustomParser(
    usage=f"{linesep} {runtime} {{bitbucket/github/gitlab/azuredevops/filesystem}} [options] {linesep}",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="",
)

parser.add_argument(
    "provider",
    type=str,
    choices=["github", "gitlab", "bitbucket", "azuredevops", "filesystem"],
)

github_group = parser.add_argument_group("github/azuredevops")
github_group.add_argument("--org", type=str, help="Organisation name to target")
github_group.add_argument(
    "--pat", type=str, help="Personal Access Token for API access and cloning"
)

gitlab_group = parser.add_argument_group("gitlab")
gitlab_group.add_argument(
    "--group",
    type=str,
    help="The GitLab Group to import repositories from",
)
gitlab_group.add_argument(
    "--access-token",
    type=str,
    help="The access token to use for accessing GitLab.",
)
gitlab_group.add_argument(
    "--gitlab-url",
    type=str,
    default="https://gitlab.com",
    help="URL of the GitLab instance to run against. (default: %(default)s)",
)

bitbucket_group = parser.add_argument_group("bitbucket")
bitbucket_group.add_argument("--workspace")
bitbucket_group.add_argument("--username")
bitbucket_group.add_argument("--password")

filesystem_group = parser.add_argument_group("filesystem")
filesystem_group.add_argument(
    "--path",
    help="The root directory that contains all of the repositories to scan. Each repository should be a subdirectory "
    "under this path.",
)

parser.add_argument(
    "--out",
    type=str,
    default="results",
    help="Output file (default: %(default)s)",
)

parser.add_argument(
    "--no-cleanup",
    action="store_true",
    help="Don't remove checked-out repositories upon completion",
)

parser.add_argument(
    "--out-format",
    type=str,
    default="csv",
    choices=["csv", "json", "html"],
)

parser.add_argument(
    "--parallel-repos",
    type=int,
    default=parallel,
    help="Number of repos to process in parallel - more than 3 not advised (default: %(default)s)",
)

parser.add_argument(
    "--disable-trufflehog",
    action="store_true",
    help="Scan without trufflehog",
)

parser.add_argument(
    "--disable-gitleaks",
    action="store_true",
    help="Scan without gitleaks",
)

parser.add_argument(
    "--single-branch",
    action="store_true",
    help="Scan only the default branch",
)

parser.add_argument(
    "--max-branch-count",
    type=int,
    default=20,
    help="Limit the number of branches scanned per repo",
)

parser.add_argument(
    "--dont-store-secret",
    action="store_true",
    help="Do not store the plaintext secret in the results",
)

parser.add_argument(
    "--extra-context",
    action="store_true",
    help="Output two lines before and after the secret for additional context.",
)

parser.add_argument(
    "--no-stats",
    action="store_true",
    help="Do not output stats summary",
)

parser.add_argument(
    "--ignore-branches-older-than",
    type=str,
    default=None,
    help="Ignore branches whose last commit date is before this value. Format is Pythons's expected ISO format e.g. 2020-01-01T00:00:00+00:00",
)

parser.add_argument(
    "--update-ca-store",
    action="store_true",
    help="If you're running secret-magpie-cli within Docker and need to provide an external CA certificate to trust, pass this option to cause it to update the container's certificate store.",
)

parser.add_argument(
    "--dont-validate-https",
    action="store_true",
    help="Disables HTTPS validation for APIs/cloning.",
)

parser.add_argument(
    "--web",
    action="store_true",
    help="Hosts a webserver on http://127.0.0.1:8080 to view the results in browser",
)

parser.add_argument(
    "--to-scan-list",
    type=str,
    help="The file to read the list of repositories to scan from. One repository per line, web URL to the repository.",
)

parser.add_argument(
    "--gl-config",
    type=str,
    help="The .toml file to pass from Gitleaks.",
)


def parse_args():
    args = parser.parse_args()
    if "bitbucket" == args.provider and (
        args.workspace is None or args.password is None or args.username is None
    ):
        parser.error("bitbucket requires --workspace, --username and --password")

    if ("github" == args.provider) and (args.pat is None or args.org is None):
        parser.error("github requires --pat and --org")

    if ("gitlab" == args.provider) and (
        args.access_token is None or args.group is None
    ):
        parser.error("gitlab requires --access-token and --group")

    if ("azuredevops" == args.provider) and (args.pat is None or args.org is None):
        parser.error("azuredevops requires --pat and --org")

    if "filesystem" == args.provider and (args.path is None):
        parser.error("filesystem requires --path")

    if "gl-config" == args.gl_config and args.disable_gitleaks:
        parser.error("gitleaks can't be disabled to pass a if passing a .toml file")
    return args
