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

ag_grid_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Ag-Grid Basic Example</title>
    <script src="https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js"></script>
    <script>
        let excludeHashes = [];

        class HashIgnorer {
            // gets called once before the renderer is used
            init(params) {
                // create the cell
                this.eGui = document.createElement('div');
                this.eGui.innerHTML = `
                    <span>
                        <span class="my-value"></span>
                        <button class="btn-simple">Ignore Hash</button>
                    </span>
                `;

                // get references to the elements we want
                this.eButton = this.eGui.querySelector('.btn-simple');
                this.eValue = this.eGui.querySelector('.my-value');

                // set value into cell
                this.cellValue = this.getValueToDisplay(params);
                this.eValue.innerHTML = this.cellValue;

                // add event listener to button
                this.eventListener = () => {
                    excludeHashes.push(this.cellValue);
                    params.api.onFilterChanged();
                }
                this.eButton.addEventListener('click', this.eventListener);
            }

            getGui() {
                return this.eGui;
            }

            // gets called whenever the cell refreshes
            refresh(params) {
                // set value into cell again
                this.cellValue = this.getValueToDisplay(params);
                this.eValue.innerHTML = this.cellValue;

                // return true to tell the grid we refreshed successfully
                return true;
            }

            // gets called when the cell is removed from the grid
            destroy() {
                // do cleanup, remove event listener from button
                if (this.eButton) {
                    // check that the button element exists as destroy() can be called before getGui()
                    this.eButton.removeEventListener('click', this.eventListener);
                }
            }

            getValueToDisplay(params) {
                return params.valueFormatted ? params.valueFormatted : params.value;
            }
        }

        class ContextTooltip {
            init(params) {
                const eGui = (this.eGui = document.createElement('div'));
                const color = 'white';
                const data = params.api.getDisplayedRowAtIndex(params.rowIndex).data;

                eGui.classList.add('context-tooltip');

                eGui.style['background-color'] = "#242930";
                eGui.innerHTML = `
                        <p>
                            <span class"orange">${data.secret}</span>
                        </p>
                        <p>
                            <span><span class="orange">Context: </span><code>${data.context.split('\\n').join('</br>')}</code></span>
                        </p>
                        <p>
                            <span class="orange">Total: </span>
                            <code>
                                ${data.extra_context.split('\\n').join('</br>')}
                            </code>
                        </p>
                    `;
            }

            getGui() {
                return this.eGui;
            }
        }

        const columnDefs = [
                { field: "date" },
                { field: "source" },
                { field: "detector_type" },
                { field: "commit" },
                { field: "link" },
                { field: "file" },
                { field: "line" },
                { 
                    field: "hashed_secret",
                    cellRenderer: HashIgnorer
                },
                { 
                    field: "secret",
                    tooltipField: "secret"
                }
            ];

            // specify the data
            const rowData = $$ROWDATA$$;

            // let the grid know which columns and what data to use
            const gridOptions = {
                defaultColDef: {
                    resizable: true,
                    tooltipComponent: ContextTooltip
                },
                columnDefs: columnDefs,
                rowData: rowData,

                isExternalFilterPresent: () => true,
                doesExternalFilterPass: row => excludeHashes.indexOf(row.data.hashed_secret) == -1
            };

            // setup the grid after the page has finished loading
            document.addEventListener('DOMContentLoaded', () => {
                const gridDiv = document.querySelector('#myGrid');
                new agGrid.Grid(gridDiv, gridOptions);
            });
    </script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-theme-alpine.css"/>
	<style>
		body {
			font-family: anaheim, sans-serif;
		}

		.ag-theme-customtheme {
			--ag-borders: solid 6px;
			--ag-border-color: #1d2024;
			--ag-header-background-color: #1d2024;
			--ag-background-color: black;
			--ag-odd-row-background-color: #1d2024;
			--ag-row-border-color: transparent;
			--ag-header-foreground-color: #be7b1e;
		}

		.downloadButtons {
			padding: 10px 20px;
			border: 1px solid;
			border-color: #c5c6c7;
			border-radius: 0;
			color: white;
			background-color: transparent;
			transition: all .3s ease-in 0s;
			display: inline-block;
			margin-left: 10px;
		}

			.downloadButtons:hover {
				background-color: #2da84d;
			}

		.selectionBar {
			background-color: #1d2024;
			margin-bottom: 20px;
			padding: 5px 20px;
		}

		.makeInline {
			display: inline-block;
		}

        .orange {
            color: #be7b1e;
            font-weight: bold;
        }

        code {
            color: white;
            font-family: monospace;
        }

        .context-tooltip {
            max-width: 500px;
            max-height: 300px;
            border: 1px solid white;
            overflow-x: hidden;
            overflow-y: scroll;
            width: auto;
            height: auto;
        }

        .context-tooltip p {
            margin: 5px;
            white-space: nowrap;
        }

        .context-tooltip p:first-of-type {
            font-weight: bold;
        }

	</style>
</head>
<body style="background-color: #242930; margin: 20px">
	<div class="selectionBar">
		<p style="color: #f39b20; display: inline-block;">Download as:</p>
		<button type="button" class="downloadButtons">CSV</button>
		<button type="button" class="downloadButtons">JSON</button>
		<div style="display: inline-block; float: right">
			<p class="makeInline" style="color: white;">In </p>
			<input class="makeInline" id="searchbar" onkeyup="" type="text" name="search">

			<p class="makeInline" style="color: white;"> search for </p>
			<!--TODO: Pull column headers from JSON using JS and display them here-->
			<!--This option will make it so that words searched for will only be searched for in said column--->
			<select name="column">
				<option value="test">TestOption</option>
			</select>
		</div>
	</div>
	<div id="myGrid" style="height: 1000px; width: 100%;" class="ag-theme-alpine-dark ag-theme-customtheme"></div>
</html>

"""

if __name__ == "__main__":
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
            if filename.endswith(".csv"):
                results = json.dumps(list(csv.DictReader(f)))
            elif filename.endswith(".json"):
                results = f.read()
            else:
                print("ERROR: Invalid input format for HTML conversion.")
                sys.exit(1)

        with open("results.html", "w") as f:
            f.write(ag_grid_template.replace("$$ROWDATA$$", results))
