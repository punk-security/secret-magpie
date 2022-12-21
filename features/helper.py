import git
import os
import shutil
import stat
import subprocess

from behave import given, when, then, step


TESTING_DIRECTORY = "testing"


@given("we create a local repo named {repo}")
def step_impl(context, repo):
    try:
        context.rules
    except AttributeError:
        context.rules = []
    context.repo_name = repo
    context.current_branch = "master"

    context.rules.append(["repo " + repo])


@given("we create a file named {file} on branch {branch} with contents")
def step_impl(context, file, branch):
    if branch != context.current_branch:
        context.rules.append(["branch " + branch])

    content = context.text.split("\n")
    content.insert(0, "file " + file)

    context.rules.append(content)


@given("we commit all changes")
def step_impl(context):
    context.rules.append(["commit"])


@given("we delete {file}")
def step_impl(context, file):
    context.rules.append(["delete " + file])


@given("we switch branch to {branch}")
def step_impl(context, branch):
    context.rules.append(["branch " + branch])


def run_secret_magpie(context, engines, outformat="csv", args=[]):
    try:
        context.repos = LocalRepos(context.rules, TESTING_DIRECTORY)
    except:
        context.repos = LocalRepos([], TESTING_DIRECTORY)

    context.format = outformat

    param_list = [
        "python",
        "./main.py",
        "--out-format",
        outformat,
        "filesystem",
        "--path",
        TESTING_DIRECTORY,
        "--no-cleanup",
    ]

    for arg in args:
        param_list.append(arg)

    if engines != "all":
        engines = engines.split(" ")
        if not "trufflehog" in engines:
            param_list.append("--disable-trufflehog")
        if not "gitleaks" in engines:
            param_list.append("--disable-gitleaks")

    env = os.environ
    env["PYTHONUTF8"] = "1"

    proc = subprocess.run(param_list, capture_output=True, env=env, encoding="UTF-8")

    if proc.stderr != "":
        raise AssertionError(proc.stderr)

    if "❌" in proc.stdout:
        raise AssertionError(proc.stdout)

    stdout = proc.stdout.split("\n")

    context.stdout = stdout[10:][:1]

    for fn in [
        lambda l: list(map(lambda l: l.split("|"), l)),
        lambda l: list(filter(lambda l: len(l) == 4, l)),
    ]:
        stdout = fn(stdout)

    detections = list(filter(lambda l: l[1].strip() == "Detections", stdout))
    unique_secrets = list(filter(lambda l: l[1].strip() == "Unique Secrets", stdout))

    try:
        context.found = int(detections[0][2])
    except:
        context.found = 0

    try:
        context.found_unique = int(unique_secrets[0][2])
    except:
        context.found_unique = 0


@when("we run secret-magpie-cli with engines: {engines}")
def step_impl(context, engines):
    run_secret_magpie(context, engines)


@when("we run secret-magpie-cli with output format {format} and engines: {engines}")
def step_impl(context, format, engines):
    run_secret_magpie(context, engines, outformat=format)


@when(
    "we run secret-magpie-cli with secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(context, secret_toggle, format, engines):
    args = []
    if secret_toggle == "disabled":
        args.append("--dont-store-secret")
    run_secret_magpie(context, engines, outformat=format, args=args)


@when(
    "we run secret-magpie-cli in {branch_toggle} branch mode, secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(context, branch_toggle, secret_toggle, format, engines):
    args = []
    if secret_toggle == "disabled":
        args.append("--dont-store-secret")
    if branch_toggle == "single":
        args.append("--single-branch")
    run_secret_magpie(context, engines, outformat=format, args=args)


@then("secret-magpie-cli's output will be")
def step_impl(context):
    stdout = context.stdout
    expected = list(map(lambda s: s.rstrip("\r"), context.text.split("\n")))

    assert stdout == expected, (
        "Expected output: " + str(stdout) + ", found " + str(expected)
    )


def onerror(func, path, exc_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)


class LocalRepos:
    def __init__(self, rules, dir):
        # Prepare the directory for repositories
        if os.path.exists(dir):
            shutil.rmtree(dir, onerror=onerror)
            os.mkdir(dir)
        else:
            os.mkdir(dir)

        # Set up fields

        self.dir = dir

        # Variables to store state

        current_repo_name = ""
        current_repo = None

        commit_all = True

        # Create the repositories according to rules

        for rule_group in rules:
            rule = rule_group[0].split(" ", 1)

            match rule[0]:
                case "repo":
                    # If we have content that isn't commit yet
                    # We should commit it before anything else.

                    if not commit_all:
                        current_repo.git.add(A=True)
                        current_repo.index.commit("Commit.")

                    commit_all = True

                    current_repo_name = rule[1]

                    if current_repo != None:
                        current_repo.close()
                    current_repo = git.Repo.init(dir + "/" + rule[1])

                case "file":
                    commit_all = False
                    with open(dir + "/" + current_repo_name + "/" + rule[1], "w+") as f:
                        for i in range(1, len(rule_group)):
                            f.write(rule_group[i])

                case "delete":
                    commit_all = False
                    if os.path.exists(dir + "/" + current_repo_name + "/" + rule[1]):
                        os.remove(dir + "/" + current_repo_name + "/" + rule[1])

                case "commit":
                    current_repo.git.add(A=True)
                    if not commit_all:
                        commit_all = True
                        if len(rule) > 1:
                            current_repo.index.commit(rule[1])
                        else:
                            current_repo.index.commit("Commit.")

                case "branch":
                    # If we have content that isn't commit yet
                    # We should commit it before anything else.
                    if not commit_all:
                        current_repo.git.add(A=True)
                        current_repo.index.commit("Commit.")

                    commit_all = True

                    # Check if the branch exists or not yet
                    if not rule[1] in current_repo.heads:
                        branch = current_repo.create_head(rule[1], "HEAD")
                        current_repo.head.reference = branch
                    else:
                        current_repo.head.reference = current_repo.heads[rule[1]]

                    assert not current_repo.head.is_detached
                    current_repo.head.reset(index=True, working_tree=True)

        # Do one final check to ensure we've commit everything.

        if not commit_all:
            current_repo.git.add(update=True)
            current_repo.index.commit("Commit.")

        if not current_repo == None:
            current_repo.close()
