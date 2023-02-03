from behave import given, when, then, step
from helper import *

import json
import csv
import glob
import subprocess

import io

import requests
import time


@when("we run Trufflehog capturing JSON output")
def step_impl(context):
    try:
        context.repos = LocalRepos(context.rules, TESTING_DIRECTORY)
    except:
        context.repos = LocalRepos([], TESTING_DIRECTORY)

    # Run trufflehog against every directory in TESTING_DIRECTORY

    trufflehog_outputs = []
    for repo_path in glob.glob(TESTING_DIRECTORY + "/*", recursive=False):
        process = subprocess.run(
            [
                "trufflehog",
                "--no-update",
                "--json",
                "git",
                "file://" + repo_path.replace("\\", "/"),
                "--fail",
            ],
            capture_output=True,
            encoding="UTF-8",
        )

        if process.returncode == 183:
            # Each line in the trufflehog output is JSON
            trufflehog_outputs.extend(
                [json.loads(s) for s in process.stdout.split("\n") if not s == ""]
            )

    context.json = trufflehog_outputs


@when("we run Gitleaks capturing JSON output")
def step_impl(context):
    try:
        context.repos = LocalRepos(context.rules, TESTING_DIRECTORY)
    except:
        context.repos = LocalRepos([], TESTING_DIRECTORY)

    # Run trufflehog against every directory in TESTING_DIRECTORY

    gitleaks_outputs = []
    for repo_path in glob.glob(TESTING_DIRECTORY + "/*", recursive=False):
        process = subprocess.run(
            [
                "gitleaks",
                "detect",
                "-s",
                repo_path.replace("\\", "/"),
                "-r",
                "gitleaks_output",
            ],
            capture_output=True,
            encoding="UTF-8",
        )

        with open("gitleaks_output") as f:
            gitleaks_outputs.append(json.loads(f.read()))

    os.remove("gitleaks_output")

    context.json = gitleaks_outputs


def recursive_compare_json(expected, actual):
    if type(expected) != type(actual):
        print(
            f"Failed on type({expected}) == type({actual}) ({type(expected)} == {type(actual)})"
        )
        return False
    match expected:
        case dict():
            if expected.keys() != actual.keys():
                print(f"Failed on {expected.keys()} == {actual.keys()}")
                return False
            for key in expected.keys():
                if not recursive_compare_json(expected[key], actual[key]):
                    return False
            return True
        case list():
            if len(expected) != len(actual):
                print(
                    f"Failed on len({expected}) == len({actual}) ({len(expected)} == {len(actual)})"
                )
                return False
            for expected, actual in zip(expected, actual):
                if not recursive_compare_json(expected, actual):
                    return False
            return True
        case _:
            if expected != actual and expected != "_":
                print(f"Failed on {expected} == {actual}")
                return False
            return True


@then("the JSON output will match")
def step_impl(context):
    expected_json = json.loads(context.text)

    assert recursive_compare_json(
        expected_json, context.json
    ), "JSON output did not match!"


@then("the JSON output will match file {file}")
def step_impl(context, file):
    with open("features/match_files/" + file) as f:
        expected_json = json.loads(f.read())

        assert recursive_compare_json(
            expected_json, context.json
        ), "JSON output did not match!"


def do_match_test(format, expected):
    match format:
        case "json":
            with open("results.json", "r") as f:
                assert recursive_compare_json(
                    json.loads(expected), json.loads(f.read())
                ), "results.json did not match!"
        case "html":
            with open("results.html", "r") as f:
                # For the HTML, we need to
                #  - verify that the start of the file exists
                #  - validate the data within the "middle" of the file
                #  - verify that the end of the file exists
                file_contents = f.read()

                # We expect the rowData to be all on one line

                position = file_contents.find("let rowData = ")

                first_half = file_contents[0:position]
                latter_half = file_contents[(file_contents.find("\n", position)) :]

                rowData = file_contents[
                    position
                    + len("let rowData = ") : file_contents.find("\n", position)
                    - 1
                ]

                if first_half.find("<!DOCTYPE html>") == -1:
                    raise AssertionError("results.html is missing its first half!")

                if first_half.find("ag-grid-community") == -1:
                    raise AssertionError("ag-grid-community.min.js is missing!")

                if latter_half.find("</html>") == -1:
                    raise AssertionError("results.html is missing its latter half!")

                assert recursive_compare_json(
                    json.loads(expected), json.loads(rowData)
                ), "results.html's data did not match!"

        case "csv":
            with open("results.csv", "r") as f:
                expected = list(csv.DictReader(io.StringIO(expected)))
                actual = list(csv.DictReader(f))

                assert len(expected) == len(actual), "results.csv did not match!"
                for expected_row, actual_row in zip(expected, actual):
                    assert not (
                        None in expected_row.values() or None in actual_row.values()
                    ), "results.csv did not match!"
                    for expected_value, actual_value in zip(
                        expected_row.values(), actual_row.values()
                    ):
                        if expected_value == "_":
                            continue
                        assert (
                            expected_value == actual_value
                        ), f"results.csv did not match! Failing comparison: {expected_value} == {actual_value}"


@then("results.{format} will match")
def step_impl(context, format):
    do_match_test(format, context.text)


@then("results.{format} will match file {file}")
def step_impl(context, format, file):
    with open("features/match_files/" + file) as f:
        do_match_test(format, f.read())


@then("a web request will match file {file}")
def step_impl(context, file):
    # Set non-blocking on stdout and stderr
    os.set_blocking(context.proc.stdout.fileno(), False)
    os.set_blocking(context.proc.stderr.fileno(), False)

    stdout = b""
    stderr = b""

    # We expect the server to print its address within 10 seconds of it starting
    start_time = time.time()
    while time.time() - start_time < 10:
        if (read := context.proc.stdout.read()) is not None:
            stdout += read
        if (read := context.proc.stderr.read()) is not None:
            stderr += read
        time.sleep(1)

    stdout = stdout.decode(encoding="UTF-8")

    linestart = stdout.find("Available at ")
    lineend = stdout.find("\n", linestart)
    if linestart == -1:
        raise AssertionError("Webserver never started!")

    address = stdout[linestart:lineend].split(" ")[2]

    resp = requests.get(address).content.decode(encoding="UTF-8")

    if resp == "":
        raise AssertionError("Empty response!")

    with open("features/match_files/" + file) as f:
        expected = f.read()
        position = resp.find("let rowData = ")

        first_half = resp[0:position]
        latter_half = resp[(resp.find("\n", position)) :]

        rowData = resp[position + len("let rowData = ") : resp.find("\n", position) - 1]

        if first_half.find("<!DOCTYPE html>") == -1:
            raise AssertionError("results.html is missing its first half!")

        if first_half.find("ag-grid-community") == -1:
            raise AssertionError("ag-grid-community.min.js is missing!")

        if latter_half.find("</html>") == -1:
            raise AssertionError("results.html is missing its latter half!")

        assert recursive_compare_json(
            json.loads(expected), json.loads(rowData)
        ), "results.html's data did not match!"
