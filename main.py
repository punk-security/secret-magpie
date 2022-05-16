from multiprocessing.pool import ThreadPool
from functools import partial
import sys

import tools
import tasks
import argparsing
import stats

if __name__ == "__main__":
    print(argparsing.banner)
    args = argparsing.parser.parse_args()
    tool_list = []
    if not args.disable_gitleaks:
        tool_list.append(tools.gitleaks)
    if not args.disable_trufflehog:
        tool_list.append(tools.truffle_hog)
    if len(tool_list) == 0:
        print("ERROR: No tools to scan with")
        sys.exit(1)
    repos = tasks.get_repos_from_github(args.github_org, args.pat)
    total_results = []
    f = partial(
        tasks.process_repo,
        pat=args.pat,
        functions=tool_list,
        single_branch=args.single_branch,
    )
    pool = ThreadPool(args.parallel_repos)
    results = pool.imap_unordered(f, repos)
    processed_repos = 0
    with open(f"results/{args.out}", "w", 1, encoding="utf-8") as f:
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
                    if args.dont_store_secret:
                        item.secret = ""
                    f.write(f"{item.__dict__}\n")
    print(
        f"       | Processed Repos: {processed_repos} | | Total secret detections: {len(total_results)} |"
    )

    if not args.no_stats:
        s = stats.Stats(total_results, processed_repos)
        print(s.Report())
