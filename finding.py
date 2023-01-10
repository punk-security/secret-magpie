from hashlib import sha256
from base64 import b64decode
from repos import FilesystemRepo
import enums
import git
import re


class Finding(object):
    def __init__(
        self,
        source,
        detector_type,
        verified,
        commit,
        date,
        author_email,
        repository,
        repository_uri,
        link,
        secret,
        file,
        line,
        directory,
        redacted_secret=None,
        extra_context=False,
    ):
        self.source = source
        self.detector_type = detector_type
        self.verified = verified
        self.commit = commit
        self.date = date
        self.author_email = author_email
        self.repository = repository
        self.repository_uri = repository_uri
        self.link = link
        self.file = file
        self.line = line
        self.filename = file.split("/")[-1]
        self.extension = file.split(".")[-1] if "." in file else ""
        self.hashed_secret = sha256(secret.encode("utf-8")).hexdigest()
        self.secret = secret
        if redacted_secret == None:
            self.redacted_secret = self.redact(secret)

        g = git.Repo(directory)
        lines = g.git.show(f"{commit}:{file}").split("\n")

        lines_of_secret = len(secret.rstrip("\n").split("\n"))

        start_line = max(0, line - 1)
        end_line = line + lines_of_secret - 1

        self.context = "\n".join(
            [l.rstrip("\n").rstrip("\r") for l in lines[start_line:end_line]]
        )

        start_line = max(0, line - 3)
        end_line = min(len(lines), line + lines_of_secret + 1)

        if extra_context:
            self.extra_context = "\n".join(
                [l.rstrip("\n").rstrip("\r") for l in lines[start_line:end_line]]
            )
        else:
            self.extra_context = ""

    def redact(self, secret):
        if len(secret) < 5:
            return "REDACTED"
        else:
            return f"{secret[0:3]}{'*' * (len(secret) - 4)}"

    @staticmethod
    def getDirectoryOfRepo(repo):
        if type(repo) == FilesystemRepo:
            return repo.name.replace("\\", "/")
        else:
            return sha256(repo.clone_url.encode("utf-8")).hexdigest()[0:8]

    @staticmethod
    def normaliseTrufflehogTimestamp(ts):
        parts = re.match(
            r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2}) \+([0-9]{2})([0-9]{2})",
            ts,
        ).groups()
        return f"{parts[0]}-{parts[1]}-{parts[2]}T{parts[3]}:{parts[4]}:{parts[5]}+{parts[6]}:{parts[7]}"

    @staticmethod
    def normaliseGitleaksTimestamp(ts):
        parts = re.match(
            r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})", ts
        ).groups()
        return (
            f"{parts[0]}-{parts[1]}-{parts[2]}T{parts[3]}:{parts[4]}:{parts[5]}+00:00"
        )

    @staticmethod
    def fromTrufflehog(trufflehog_dict, repo, extra_context):
        data = trufflehog_dict["SourceMetadata"]["Data"]
        commit = (
            "master" if data["Git"]["commit"] == "unstaged" else data["Git"]["commit"]
        )
        return Finding(
            source="trufflehog",
            detector_type=enums.DetectorTypeEnum(trufflehog_dict["DetectorType"]).name,
            verified=trufflehog_dict["Verified"],
            commit=commit,
            date=Finding.normaliseTrufflehogTimestamp(data["Git"]["timestamp"]),
            author_email=data["Git"]["email"],
            repository=repo.name.replace("\\", "/"),
            repository_uri=data["Git"].get("repository", "").replace("\\", "/"),
            link=repo.link_to_file(
                commit, data["Git"]["file"], data["Git"]["line"]
            ).replace("\\", "/"),
            secret=trufflehog_dict["Raw"].rstrip("\n"),
            file=data["Git"]["file"].replace("\\", "/"),
            line=data["Git"]["line"],
            directory=Finding.getDirectoryOfRepo(repo),
            extra_context=extra_context,
        )

    @staticmethod
    def fromGitLeak(gitleak_dict, repo, extra_context):
        repo_url = repo.html_url
        link = repo.link_to_file(
            gitleak_dict["Commit"], gitleak_dict["File"], gitleak_dict["StartLine"]
        )
        return Finding(
            source="gitleaks",
            detector_type=gitleak_dict["RuleID"],
            verified=False,
            commit=gitleak_dict["Commit"],
            date=Finding.normaliseGitleaksTimestamp(gitleak_dict["Date"]),
            author_email=gitleak_dict["Email"],
            repository=repo.name.replace("\\", "/"),
            repository_uri=repo_url.replace("\\", "/"),
            link=link.replace("\\", "/"),
            secret=gitleak_dict["Secret"].rstrip("\n"),
            file=gitleak_dict["File"].replace("\\", "/"),
            line=gitleak_dict["StartLine"],
            directory=Finding.getDirectoryOfRepo(repo),
            extra_context=extra_context,
        )

    def __repr__(self):
        return f"{self.hashed_secret}:{self.repository}:{self.file}"
