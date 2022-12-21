from behave import given, when, then, step
from helper import *

import json
import csv


def validate_results_csv():
    with open("results.csv", "r") as f:
        table = csv.DictReader(f)

        # Because Python's CSV reader tries to be "helpful" and insert missing data
        # we need to manually iterate through each row to ensure there are no None values
        # which it automatically inserts when there is missing data.

        for row in table:
            for _, v in row.items():
                assert v != None, "CSV output is not of valid form."


def validate_results_json():
    with open("results.json", "r") as f:
        json_content = f.read()
        try:
            json.loads(json_content)
        except json.decoder.JSONDecodeError:
            raise AssertionError("JSON Validation failed! json.loads decode failed!")


@then("results.csv will be a valid CSV file")
def step_impl(context):
    # Ensure we actually ran secret-magpie-cli in CSV mode
    assert context.format == "csv"

    validate_results_csv()


@then("results.json will be a valid JSON file")
def step_impl(context):
    # Ensure we actually ran secret-magpie-cli in JSON mode
    assert context.format == "json"

    validate_results_json()


@then("the results file will be of valid form")
def step_impl(context):
    if context.format == "csv":
        validate_results_csv()
    elif context.format == "json":
        validate_results_json()


@then("the secret field within the output will be blank")
def step_impl(context):
    if context.format == "csv":
        with open("results.csv", "r") as f:
            table = csv.DictReader(f)

            for row in table:
                assert (
                    row["secret"] == ""
                ), "Found secret within secret column when secret column is expected to be blank!"

    elif context.format == "json":
        with open("results.json", "r") as f:
            json_content = f.read()
            json_data = json.loads(json_content)

            for entry in json_data:
                assert (
                    entry["secret"] == ""
                ), "Found secret within secret column when secret column is expected to be blank!"
