from os import remove
from subprocess import run  # nosec B404
from finding import Finding
from json import loads


def truffle_hog(path: str, repo, branch, extra_context):
    target = "file://" + path.replace("\\", "/")
    truffle_hog = [
        "trufflehog",
        "--no-update",
        "--json",
        "git",
        target,
        "--fail",
    ]
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
        f = Finding.fromTrufflehog(loads(line), repo, extra_context)
        ret.append(f)
    return ret


def gitleaks(path, repo, branch, extra_context, config):
    temp_path = f"{path}.out"
    gitleaks = ["gitleaks", "detect", "-s", path, "-r", temp_path]
    gitleaks.append(f"--log-opts={branch}")

    if config is not None:
        gitleaks.append(f"--config={config}")

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
            ret.append(Finding.fromGitLeak(finding_dict, repo, extra_context))
        remove(temp_path)
        return ret
    else:
        try:
            remove(temp_path)
        except FileNotFoundError:
            # Expected sometimes
            pass
        return []
