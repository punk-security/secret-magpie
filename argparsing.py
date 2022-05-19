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
    usage=f"{linesep} {runtime} [options] 'github organisation name' 'personal access token' {linesep}",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="",
)

parser.add_argument(
    "provider",
    type=str,
    choices=["github", "bitbucket"],
)

github_group = parser.add_argument_group("github")
github_group.add_argument("--org", type=str, help="Github organisation name to target")
github_group.add_argument(
    "--pat", type=str, help="Github Personal Access Token for API access and cloning"
)

bitbucket_group = parser.add_argument_group("bitbucket")
bitbucket_group.add_argument("--workspace")
bitbucket_group.add_argument("--username")
bitbucket_group.add_argument("--password")

parser.add_argument(
    "--out",
    type=str,
    default="results",
    help="Output file (default: %(default)s)",
)

parser.add_argument(
    "--out-format",
    type=str,
    default="csv",
    choices=["csv", "json"],
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
    "--dont-store-secret",
    action="store_true",
    help="Do not store the plaintext secret in the results",
)

parser.add_argument(
    "--no-stats",
    action="store_true",
    help="Do not output stats summary",
)


def parse_args():
    args = parser.parse_args()
    if "bitbucket" == args.provider and (
        args.workspace is None or args.password is None or args.username is None
    ):
        parser.error("bitbucket requires --workspace, --username and --password")

    if "github" == args.provider and (args.pat is None or args.org is None):
        parser.error("github requires --pat and --org")

    return args
