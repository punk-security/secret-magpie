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

    def link_to_file(self, commit_hash, file_path, line_num):
        raise NotImplementedError("This method must be overridden in child classes")


class GithubRepo(Repo):
    def link_to_file(self, commit_hash, file_path, line_num) -> str:
        return f"{self.html_url}/blob/{commit_hash}/{file_path}#L{line_num}"


class BitbucketRepo(Repo):
    def link_to_file(self, commit_hash, file_path, line_num) -> str:
        return f"{self.html_url}/src/{commit_hash}/{file_path}#lines-{line_num}"
