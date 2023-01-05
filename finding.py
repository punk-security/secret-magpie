from hashlib import sha256
from base64 import b64decode
import enums


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
        redacted_secret=None,
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

    def redact(self, secret):
        if len(secret) < 5:
            return "REDACTED"
        else:
            return f"{secret[0:3]}{'*' * (len(secret) - 4)}"

    @staticmethod
    def fromTrufflehog(trufflehog_dict, repo):
        data = trufflehog_dict["SourceMetadata"]["Data"]
        commit = (
            "master" if data["Git"]["commit"] == "unstaged" else data["Git"]["commit"]
        )
        return Finding(
            source="trufflehog",
            detector_type=enums.DetectorTypeEnum(trufflehog_dict["DetectorType"]).name,
            verified=trufflehog_dict["Verified"],
            commit=commit,
            date=data["Git"]["timestamp"],
            author_email=data["Git"]["email"],
            repository=repo.name.replace("\\", "/"),
            repository_uri=data["Git"].get("repository", "").replace("\\", "/"),
            link=repo.link_to_file(
                commit, data["Git"]["file"], data["Git"]["line"]
            ).replace("\\", "/"),
            secret=trufflehog_dict["Raw"].rstrip("\n"),
            file=data["Git"]["file"].replace("\\", "/"),
            line=data["Git"]["line"],
        )

    @staticmethod
    def fromGitLeak(gitleak_dict, repo):
        repo_url = repo.html_url
        link = repo.link_to_file(
            gitleak_dict["Commit"], gitleak_dict["File"], gitleak_dict["StartLine"]
        )
        return Finding(
            source="gitleaks",
            detector_type=gitleak_dict["RuleID"],
            verified=False,
            commit=gitleak_dict["Commit"],
            date=gitleak_dict["Date"],
            author_email=gitleak_dict["Email"],
            repository=repo.name.replace("\\", "/"),
            repository_uri=repo_url.replace("\\", "/"),
            link=link.replace("\\", "/"),
            secret=gitleak_dict["Secret"].rstrip("\n"),
            file=gitleak_dict["File"].replace("\\", "/"),
            line=gitleak_dict["StartLine"],
        )

    def __repr__(self):
        return f"{self.hashed_secret}:{self.repository}:{self.file}"
