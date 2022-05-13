import argparse

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

parser = argparse.ArgumentParser(
    usage="%(prog)s [options] github_org pat",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=banner,
)

parser.add_argument("github_org", type=str, help="Github organisation to target")

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
