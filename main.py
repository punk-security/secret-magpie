from logging import handlers
from multiprocessing.pool import ThreadPool
from functools import partial
import sys

import csv
import json
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

import http.server
import socketserver

ag_grid_template = ""

if __name__ == "__main__":
    with open("template.html", "r", encoding="utf-8") as f:
        ag_grid_template = f.read()
    urllib3.disable_warnings()
    print(argparsing.banner)
    args = argparsing.parse_args()
    cleanup = not (args.no_cleanup or "filesystem" == args.provider)

    if args.convert_to_html is None:
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
    else:
        filename = args.convert_to_html
        with open(filename, "r") as f:
            filetype = None
            results = None
            if filename.endswith(".csv"):
                results = list(csv.DictReader(f))
            elif filename.endswith(".json"):
                results = json.loads(f.read())
            else:
                print("ERROR: Invalid input format for HTML conversion.")
                sys.exit(1)

            # Add the status column
            for i in range(0, len(results)):
                results[i]["status"] = "New"

        with open("results.html", "w", encoding="utf-8") as f:
            f.write(ag_grid_template.replace("$$ROWDATA$$", json.dumps(results)))

        
        PORT = 8080

        with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
            print("Server started at localhost:"+str(PORT))
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.server_close()
                print("Server shutdown")
