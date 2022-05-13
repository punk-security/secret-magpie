from shutil import rmtree
from time import sleep
from hashlib import sha256
from git import Repo  # gitpython
from github import Github


def clone_repo(clone_url, pat):
    path = sha256(clone_url.encode("utf-8")).hexdigest()[0:8]
    if clone_url.lower()[0:8] != "https://":
        raise Exception(f"clone url not in expected format: '{clone_url}'")
    target = f"https://{pat}@{clone_url[8:]}"
    Repo.clone_from(target, path).remotes[0].fetch()
    return path


def onerror(func, path, exc_info):
    import stat, os

    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def get_branches(path):
    r = Repo.init(path)
    return list([x.remote_head for x in r.remotes[0].refs if x.is_detached == True])


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


def process_repo(repo, pat, functions, single_branch=False):
    out = []
    try:
        path = clone_repo(repo.clone_url, pat)
    except:
        return [ProcessRepoResult(repo, "FAIL", "Could not clone")]
    if not single_branch:
        branches = get_branches(path)
    else:
        branches = [
            None,
        ]
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


def get_repos_from_github(org, pat):
    g = Github(pat)
    organisation = g.get_organization(org)
    repos = organisation.get_repos()
    return repos
