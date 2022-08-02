from multiprocessing.pool import ThreadPool
from functools import partial
import sys

import tools
import tasks
import argparsing
import stats
import output

if __name__ == "__main__":
    print(argparsing.banner)
    args = argparsing.parse_args()
    cleanup = not (args.no_cleanup or "filesystem" == args.provider)

    tool_list = []
    if not args.disable_gitleaks:
        tool_list.append(tools.gitleaks)
    if not args.disable_trufflehog:
        tool_list.append(tools.truffle_hog)
    if len(tool_list) == 0:
        print("ERROR: No tools to scan with")
        sys.exit(1)
    repos = tasks.get_repos(**args.__dict__)
    total_results = []
    f = partial(
        tasks.process_repo,
        functions=tool_list,
        single_branch=args.single_branch,
        cleanup=cleanup,
    )
    pool = ThreadPool(args.parallel_repos)
    results = pool.imap_unordered(f, repos)
    processed_repos = 0
    with output.Output(args.out_format, args.out) as o:
        for result_batch in results:
            processed_repos += 1
            print(
                f"          | Processed Repos: {processed_repos} | | Total secret detections: {len(total_results)} |",
                end="\r",
                flush=True,
            )
            for result in result_batch:
                if result.status == "FAIL" or result.findings == []:
                    continue
                for item in result.findings:
                    total_results.append(item)
                    if args.dont_store_secret:
                        item.secret = ""  # nosec hardcoded_password_string
                    o.write(item)
    print(
        f"          | Processed Repos: {processed_repos} | | Total secret detections: {len(total_results)} |"
    )

    if not args.no_stats:
        s = stats.Stats(total_results, processed_repos)
        print(s.Report())
