from git import Repo as GitRepo
from hashlib import sha256


class RepoCredentials:
    def __init__(self, password, username=""):
        self.username = username
        self.password = password

    def get_auth_string(self) -> str:
        if self.username:
            return f"{self.username}:{self.password}"

        return self.password


class Repo:
    def __init__(self, clone_url, html_url, name, credentials: RepoCredentials) -> None:
        self.credentials = credentials
        self.html_url = html_url
        self.name = name
        self.clone_url = clone_url

    def clone_repo(self):
        path = sha256(self.clone_url.encode("utf-8")).hexdigest()[0:8]
        if self.clone_url.lower()[0:8] != "https://":
            raise Exception(f"clone url not in expected format: '{self.clone_url}'")

        target = f"https://{self.credentials.get_auth_string()}@{self.clone_url[8:]}"
        GitRepo.clone_from(target, path).remotes[0].fetch()
        return path

    def link_to_file(self, commit_hash, file_path, line_num):
        raise NotImplementedError("This method must be overridden in child classes")


class GithubRepo(Repo):
    def link_to_file(self, commit_hash, file_path, line_num) -> str:
        return f"{self.html_url}/blob/{commit_hash}/{file_path}#L{line_num}"


class GitlabRepo(Repo):
    def link_to_file(self, commit_hash, file_path, line_num) -> str:
        return f"{self.html_url}/blob/{commit_hash}/{file_path}#L{line_num}"


class BitbucketRepo(Repo):
    def link_to_file(self, commit_hash, file_path, line_num) -> str:
        return f"{self.html_url}/src/{commit_hash}/{file_path}#lines-{line_num}"


class ADORepo(Repo):
    def link_to_file(self, commit_hash, file_path, line_num):
        return f"{self.html_url}/commit/{commit_hash}?path=%2F{file_path}"


class FilesystemRepo(Repo):
    """Represents a repository that is already checked out in the local filesystem"""

    def __init__(self, clone_url):
        super().__init__(clone_url, "", clone_url, None)

    def clone_repo(self):
        return self.clone_url

    def link_to_file(self, commit_hash, file_path, line_num):
        return self.clone_url
