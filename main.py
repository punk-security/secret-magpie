from multiprocessing.pool import ThreadPool
from functools import partial
import sys

import tools
import tasks
import argparsing

if __name__ == "__main__":
    try:
        args = argparsing.parser.parse_args()
    except SystemExit as e:
        argparsing.parser.print_help()
        sys.exit(1)
    print(argparsing.banner)
    repos = tasks.get_repos_from_github(args.github_org, args.pat)
    total_results = []
    f = partial(
        tasks.process_repo, pat=args.pat, functions=[tools.gitleaks, tools.truffle_hog]
    )
    pool = ThreadPool(args.parallel_repos)
    results = pool.imap_unordered(f, repos)
    processed_repos = 0
    with open(args.out, "w", 1, encoding="utf-8") as f:
        for result_batch in results:
            processed_repos += 1
            print(
                f"       | Processed Repos: {processed_repos} | | Total secret detections: {len(total_results)} |",
                end="\r",
                flush=True,
            )
            for result in result_batch:
                if result.status == "FAIL" or result.findings == []:
                    continue
                for item in result.findings:
                    total_results.append(item)
                    f.write(f"{item.__dict__}\n")
