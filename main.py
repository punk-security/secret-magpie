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
import random
import string

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

ag_grid_template = ""

if __name__ == "__main__":
    urllib3.disable_warnings()
    print(argparsing.banner)
    args = argparsing.parse_args()
    cleanup = not (args.no_cleanup or "filesystem" == args.provider)

    if args.web:
        with open("template.html", "r", encoding="utf-8") as f:
            ag_grid_template = f.read()
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

    if args.web:
        filename = f"{args.out}.{args.out_format}"
        print(filename)
        with open(filename, "r") as f:
            filetype = None
            results = None
            if filename.endswith(".csv"):
                results = list(csv.DictReader(f))
            elif filename.endswith(".json"):
                results = json.loads(f.read())
            elif filename.endswith(".html"):
                pass
            else:
                print("ERROR: Invalid input format for HTML conversion.")
                sys.exit(1)

            # Add the status column
            for i in range(0, len(results)):
                results[i]["status"] = "New"

        with open("results.html", "w", encoding="utf-8") as f:
            with open("ag-grid-community.min.js") as aggrid:
                f.write(
                    ag_grid_template.replace(
                        "$$ROWDATA$$", json.dumps(results)
                    ).replace("$$AGGRID_CODE$$", aggrid.read()),
                )

        auth_param = "".join(
            [random.choice(string.ascii_letters) for i in range(0, 64)]
        )

        class ServeResultsHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                query = urlparse(self.path).query
                query_components = parse_qs(query)

                if query_components.get("key", "") != [auth_param]:
                    return None
                self.path = "results.html"
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

        [ADDR, PORT] = os.environ.get(
            "SECRETMAGPIE_LISTEN_ADDR", "127.0.0.1:8080"
        ).split(":")

        with socketserver.TCPServer((ADDR, int(PORT)), ServeResultsHandler) as httpd:
            print(f"Server started at {ADDR}:{PORT}")
            print(
                f"Available at http://{ADDR if ADDR != '0.0.0.0' else '127.0.0.1'}:{PORT}/?key={auth_param}"
            )
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Shutting down...")
                httpd.server_close()
                print("Server shutdown.")
