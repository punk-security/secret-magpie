import argparse
from os import linesep, environ
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

    Scan all your github repos from one tool, with multiple tools!
        """


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

parser.add_argument("github_org", type=str, help="Github organisation name to target")

parser.add_argument(
    "pat", type=str, help="Github Personal Access Token for API access and cloning"
)


parser.add_argument(
    "--out", type=str, default="results.json", help="Output file (default: %(default)s)"
)

parser.add_argument(
    "--parallel-repos",
    type=int,
    default=1,
    help="Number of repos to process in parallel - more than 3 not advised (default: %(default)s)",
)

parser.add_argument(
    "--disable-trufflehog",
    action="store_true",
    help="Scan with trufflehog",
)

parser.add_argument(
    "--disable-gitleaks",
    action="store_true",
    help="Scan with gitleaks",
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
