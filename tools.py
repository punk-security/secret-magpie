from os import remove
from subprocess import run  # nosec B404
from finding import Finding
from json import loads


def truffle_hog(path, repo, branch=None):
    target = f"file://{path}"
    truffle_hog = [
        "trufflehog",
        "--no-update",
        "--json",
        "git",
        target,
        "--no-verification",
        "--fail",
    ]
    if branch != None:
        truffle_hog.append(f"--branch={branch}")
    output = run(  # nosec B603 git branch has limited char set
        truffle_hog, capture_output=True
    )
    if output.returncode == 0:
        return []
    ret = []
    for line in output.stdout.decode("utf-8").split("\n"):
        if line == "":
            continue
        f = Finding.fromTrufflehog(loads(line), repo)
        ret.append(f)
    return ret


def gitleaks(path, repo, branch=None):
    temp_path = f"{path}.out"
    gitleaks = ["gitleaks", "detect", "-s", path, "-r", temp_path]
    if branch != None:
        gitleaks.append(f"--log-opts=remotes/origin/{branch}")
    result = run(  # nosec B603 git branch has limited char set
        gitleaks, capture_output=True
    )
    if result.returncode == 1:
        try:
            with open(temp_path, "r") as f:
                findings = f.read()
        except:
            return []
        findings_list = loads(findings)
        ret = []
        for finding_dict in findings_list:
            ret.append(Finding.fromGitLeak(finding_dict, repo))
        remove(temp_path)
        return ret
    else:
        try:
            remove(temp_path)
        except FileNotFoundError:
            # Expected sometimes
            pass
        return []
