import glob
from shutil import rmtree
from time import sleep
from git import Repo as GitRepo
from github import Github
from gitlab import Gitlab
from atlassian import bitbucket

from repos import BitbucketRepo, GithubRepo, GitlabRepo, RepoCredentials, FilesystemRepo


def onerror(func, path, exc_info):
    import stat, os

    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def get_branches(path):
    r = GitRepo.init(path)

    branches = []

    if len(r.remotes) > 0:
        branches.extend(
            ["remotes/" + x.name for x in r.remotes[0].refs if x.is_detached == True]
        )

    branches.extend(
        [
            head.name
            for head in r.heads
            if head.is_detached == True and not head.is_remote()
        ]
    )

    return branches


class ProcessRepoResult(object):
    def __init__(self, repo, status, message, findings=[]):
        self.repo = repo
        self.status = status
        self.message = message
        self.findings = findings

    def __repr__(self):
        if self.status == "SUCCESS":
            return (
                f"{self.status}::{self.repo.name}::{self.message}::{len(self.findings)}"
            )
        else:
            return f"{self.status}::{self.repo.name}::{self.message}"


def process_repo(repo, functions, single_branch=False, cleanup=True):
    out = []
    try:
        path = repo.clone_repo()
    except:
        return [ProcessRepoResult(repo, "FAIL", "Could not clone")]
    if not single_branch:
        branches = get_branches(path)
    else:
        branches = ["HEAD"]
    for branch in branches:
        for function in functions:
            try:
                out.append(
                    ProcessRepoResult(
                        repo, "SUCCESS", function.__name__, function(path, repo, branch)
                    )
                )
            except:
                out.append(
                    ProcessRepoResult(repo, "FAIL", f"Could not {function.__name__}")
                )
    if cleanup:
        for i in range(3):
            try:
                rmtree(path, onerror=onerror)
                break
            except:
                sleep(10)
                pass
    ret = []
    for function in functions:
        deduped = {}
        for result in out:
            if result.status != "SUCCESS":
                ret.append(result)
            if result.status == "SUCCESS" and result.message == function.__name__:
                for f in result.findings:
                    key = f"{f.commit}{f.file}{f.line}{f.hashed_secret}"
                    deduped[key] = f
        ret.append(
            ProcessRepoResult(repo, "SUCCESS", function.__name__, deduped.values())
        )

    return ret


def get_repos_from_bitbucket(workspace, username, password):
    instance = bitbucket.Cloud(username=username, password=password, cloud=True)

    workspace = instance.workspaces.get(workspace)
    for repo in workspace.repositories.each():
        clone_url = [
            x["href"] for x in repo.data["links"]["clone"] if "https" == x["name"]
        ][0]

        at = clone_url.index("@") + 1
        clone_url = "https://" + clone_url[at:]

        yield BitbucketRepo(
            clone_url=clone_url,
            name=repo.data["name"],
            html_url=repo.data["links"]["html"]["href"],
            credentials=RepoCredentials(password, username),
        )


def get_repos_from_github(org, pat):
    g = Github(pat)
    organisation = g.get_organization(org)
    repos = organisation.get_repos()

    for repo in repos:
        yield GithubRepo(
            clone_url=repo.clone_url,
            name=repo.name,
            html_url=repo.html_url,
            credentials=RepoCredentials(pat),
        )


def get_repos_from_gitlab(org, pat):
    g = Gitlab(private_token=pat)
    group = g.groups.get(org, lazy=True)
    repos = group.projects.list(all=True)

    for repo in repos:
        yield GitlabRepo(
            clone_url=repo.http_url_to_repo,
            name=repo.name,
            html_url=repo.web_url,
            credentials=RepoCredentials(pat, username="oauth2"),
        )


def get_repos_from_filesystem(path):
    for repo_path in glob.glob(path + "/*", recursive=False):
        yield FilesystemRepo(repo_path)


def get_repos(provider, **kwargs):
    if "github" == provider:
        return get_repos_from_github(kwargs["org"], kwargs["pat"])

    if "gitlab" == provider:
        return get_repos_from_gitlab(kwargs["org"], kwargs["pat"])

    if "bitbucket" == provider:
        return get_repos_from_bitbucket(
            kwargs["workspace"], kwargs["username"], kwargs["password"]
        )
    if "filesystem" == provider:
        return get_repos_from_filesystem(kwargs["path"])

    raise NotImplementedError("Unsupported provider: " + provider)
