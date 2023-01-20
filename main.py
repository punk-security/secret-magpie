from multiprocessing.pool import ThreadPool
from functools import partial
import sys

import tools
import tasks
import argparsing
import stats
import output
import datetime
import time
import os
import subprocess  # nosec blacklist
import urllib3

if __name__ == "__main__":
    urllib3.disable_warnings()
    print(argparsing.banner)
    args = argparsing.parse_args()
    cleanup = not (args.no_cleanup or "filesystem" == args.provider)

    to_scan_list = None

    if args.to_scan_list is not None:
        with open(args.to_scan_list, "r") as f:
            to_scan_list = f.read().split("\n")

    with open(os.devnull, "wb") as devnull:
        if args.update_ca_store:
            subprocess.call(  # nosec subprocess_without_shell_equals_true start_process_with_partial_path
                ["update-ca-certificates"], stdout=devnull, stderr=devnull
            )

    threshold_date = None
    if args.ignore_branches_older_than != None:
        try:
            threshold_date = time.mktime(
                datetime.datetime.fromisoformat(
                    args.ignore_branches_older_than
                ).timetuple()
            )
        except ValueError:
            print("ERROR: Invalid ISO format string.")
            sys.exit(1)

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
        extra_context=args.extra_context,
        cleanup=cleanup,
        threshold_date=threshold_date,
        validate_https=not args.dont_validate_https,
        to_scan_list=to_scan_list,
        max_branch_count=args.max_branch_count,
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
                        item.context = ""
                        item.extra_context = ""
                    o.write(item)
    print(
        f"          | Processed Repos: {processed_repos} | | Total secret detections: {len(total_results)} |"
    )

    if not args.no_stats:
        s = stats.Stats(total_results, processed_repos)
        print(s.Report())
