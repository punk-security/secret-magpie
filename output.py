import csv


class Output:
    supported_formats = ["csv"]

    def __init__(self, format, path):
        if format not in self.supported_formats:
            raise Exception("Unsupported output format")
        self.path = path
        self.format = format
        self.writer = None

    def __enter__(self):
        if self.format == "csv":
            self.fd = open(self.path, "w", 1, encoding="utf-8", newline="")
        return self

    def __exit__(self, type, value, traceback):
        self.fd.close()

    def write(self, finding):
        if self.format == "csv":
            self.write_csv(finding)

    def write_csv(self, finding):
        if self.writer == None:
            self.writer = csv.DictWriter(
                self.fd, fieldnames=finding.__dict__.keys(), dialect="excel"
            )
        self.writer.writerow(finding.__dict__)
