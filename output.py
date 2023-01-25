import csv
import json
import os

import main


class Output:
    supported_formats = ["csv", "json", "html"]

    def __init__(self, format, path):
        if format not in self.supported_formats:
            raise Exception("Unsupported output format")
        self.path = f"{path}.{format}"
        self.format = format
        self.writer = None

    def __enter__(self):
        if self.format == "csv":
            self.fd = open(self.path, "w", 1, encoding="utf-8", newline="")
        if self.format == "json":
            self.fd = open(self.path, "w", 1, encoding="utf-8", newline="")
        if self.format == "html":
            with open("template.html", "r") as f:
                self.ag_grid_template = f.read()
            self.fd = open(self.path, "w", 1, encoding="utf-8", newline="")
            self.fd.write(self.ag_grid_template.split("$$ROWDATA$$")[0])
        return self

    def __exit__(self, type, value, traceback):
        if self.format == "json":
            self.fd.write(f"{os.linesep}]")
        if self.format == "html":
            self.fd.write("]")
            self.fd.write(self.ag_grid_template.split("$$ROWDATA$$")[1])
        self.fd.close()

    def write(self, finding):
        if self.format == "csv":
            self.write_csv(finding)
        if self.format == "json":
            self.write_json(finding)
        if self.format == "html":
            self.write_html(finding)

    def write_csv(self, finding):
        if self.writer == None:
            self.writer = csv.DictWriter(
                self.fd, fieldnames=finding.__dict__.keys(), dialect="excel"
            )
            self.writer.writeheader()

        self.writer.writerow(finding.__dict__)

    def write_json(self, finding):
        sep = ","
        if self.writer == None:
            self.fd.write("[")
            self.writer = True
            sep = ""  # no seperator for the first run
        json_payload = json.dumps(finding.__dict__)
        self.fd.write(f"{sep}{os.linesep}{json_payload}")
        self.fd.flush()

    def write_html(self, finding):
        sep = ","
        if self.writer == None:
            self.fd.write("[")
            self.writer = True
            sep = ""  # no seperator for the first run
        data = finding.__dict__
        data["status"] = "New"
        json_payload = json.dumps(data)
        self.fd.write(f"{sep}{os.linesep}{json_payload}")
        self.fd.flush()
