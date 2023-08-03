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


@given("we have a file called {name} with content")
def step_impl(context, name):
    with open(name, "w") as f:
        f.write(context.text)


def run_secret_magpie(context, engines, outformat="csv", args=[]):
    try:
        context.repos = LocalRepos(context.rules, TESTING_DIRECTORY)
    except:
        context.repos = LocalRepos([], TESTING_DIRECTORY)

    context.format = outformat

    param_list = []

    match context.repo_type:
        case "local":
            param_list = [
                "python",
                "./main.py",
                "--out-format",
                outformat,
                "filesystem",
                "--path",
                TESTING_DIRECTORY,
            ]
        case "github":
            param_list = [
                "python",
                "./main.py",
                "--out-format",
                outformat,
                "github",
                "--org",
                context.org,
                "--pat",
                context.pat,
            ]
        case "gitlab":
            param_list = [
                "python",
                "./main.py",
                "--out-format",
                outformat,
                "gitlab",
                "--group",
                context.org,
                "--access-token",
                context.pat,
            ]

            try:
                param_list.extend(["--gitlab-url", context.url])
            except:
                pass
        case "azuredevops":
            param_list = [
                "python",
                "./main.py",
                "--out-format",
                outformat,
                "azuredevops",
                "--org",
                context.org,
                "--pat",
                context.pat,
            ]
        case "bitbucket":
            param_list = [
                "python",
                "./main.py",
                "--out-format",
                outformat,
                "bitbucket",
                "--workspace",
                context.workspace,
                "--username",
                context.username,
                "--password",
                context.password,
            ]
        case _:
            raise (AssertionError("Repo type not specified"))

    param_list.extend(args)
    try:
        param_list.extend(context.args)
    except:
        pass

    if engines != "all":
        engines = engines.split(" ")
        if not "trufflehog" in engines:
            param_list.append("--disable-trufflehog")
        if not "gitleaks" in engines:
            param_list.append("--disable-gitleaks")

    env = os.environ
    env["PYTHONUTF8"] = "1"

    context.stdout = ""

    if context.web:
        context.proc = subprocess.Popen(
            param_list, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    else:
        context.proc = subprocess.run(
            param_list, capture_output=True, env=env, encoding="UTF-8"
        )

        if context.proc.stderr != "":
            raise AssertionError(context.proc.stderr)

        if "❌" in context.proc.stdout:
            raise AssertionError(context.proc.stdout)

        if "warning" in context.proc.stdout:
            raise AssertionError(context.proc.stdout)

        stdout = context.proc.stdout.split("\n")

        context.stdout = stdout[10:][:1]

        for fn in [
            lambda l: list(map(lambda l: l.split("|"), l)),
            lambda l: list(filter(lambda l: len(l) == 4, l)),
        ]:
            stdout = fn(stdout)

        detections = list(filter(lambda l: l[1].strip() == "Detections", stdout))
        unique_secrets = list(
            filter(lambda l: l[1].strip() == "Unique Secrets", stdout)
        )

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


@when(
    "we run secret-magpie-cli in {branch_toggle} branch mode, extra context {extra_context}, secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(context, branch_toggle, extra_context, secret_toggle, format, engines):
    args = []
    if extra_context == "enabled":
        args.append("--extra-context")
    if secret_toggle == "disabled":
        args.append("--dont-store-secret")
    if branch_toggle == "single":
        args.append("--single-branch")
    run_secret_magpie(context, engines, outformat=format, args=args)


@when(
    "we run secret-magpie-cli in {branch_toggle} branch mode, ignoring commits older than {threshold_date} extra context {extra_context}, secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(
    context,
    branch_toggle,
    threshold_date,
    extra_context,
    secret_toggle,
    format,
    engines,
):
    args = []
    if threshold_date != "None":
        args.append(f"--ignore-branches-older-than={threshold_date}")
    if extra_context == "enabled":
        args.append("--extra-context")
    if secret_toggle == "disabled":
        args.append("--dont-store-secret")
    if branch_toggle == "single":
        args.append("--single-branch")
    run_secret_magpie(context, engines, outformat=format, args=args)


@when(
    "we run secret-magpie-cli in {branch_toggle} branch mode, https validation {https_validation}, ignoring commits older than {threshold_date}, extra context {extra_context}, secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(
    context,
    branch_toggle,
    https_validation,
    threshold_date,
    extra_context,
    secret_toggle,
    format,
    engines,
):
    args = []
    if https_validation == "disabled":
        args.append("--dont-validate-https")
    if threshold_date != "None":
        args.append(f"--ignore-branches-older-than={threshold_date}")
    if extra_context == "enabled":
        args.append("--extra-context")
    if secret_toggle == "disabled":
        args.append("--dont-store-secret")
    if branch_toggle == "single":
        args.append("--single-branch")
    run_secret_magpie(context, engines, outformat=format, args=args)


@when(
    "we run secret-magpie-cli in {branch_toggle} branch mode, to scan list {to_scan_list}, https validation {https_validation}, ignoring commits older than {threshold_date}, extra context {extra_context}, secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(
    context,
    branch_toggle,
    to_scan_list,
    https_validation,
    threshold_date,
    extra_context,
    secret_toggle,
    format,
    engines,
):
    args = []
    if to_scan_list != "None":
        args.append(f"--to-scan-list={to_scan_list}")
    if https_validation == "disabled":
        args.append("--dont-validate-https")
    if threshold_date != "None":
        args.append(f"--ignore-branches-older-than={threshold_date}")
    if extra_context == "enabled":
        args.append("--extra-context")
    if secret_toggle == "disabled":
        args.append("--dont-store-secret")
    if branch_toggle == "single":
        args.append("--single-branch")
    run_secret_magpie(context, engines, outformat=format, args=args)


@when(
    "we run secret-magpie-cli in {branch_toggle} branch mode, web mode {web_mode}, to scan list {to_scan_list}, https validation {https_validation}, ignoring commits older than {threshold_date}, extra context {extra_context}, secret storing {secret_toggle}, output format {format} and engines: {engines}"
)
def step_impl(
    context,
    branch_toggle,
    web_mode,
    to_scan_list,
    https_validation,
    threshold_date,
    extra_context,
    secret_toggle,
    format,
    engines,
):
    args = []
    if web_mode == "enabled":
        context.web = True
        args.append("--web")
    if to_scan_list != "None":
        args.append(f"--to-scan-list={to_scan_list}")
    if https_validation == "disabled":
        args.append("--dont-validate-https")
    if threshold_date != "None":
        args.append(f"--ignore-branches-older-than={threshold_date}")
    if extra_context == "enabled":
        args.append("--extra-context")
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


@then("directory {dir} won't exist")
def step_impl(context, dir):
    assert (
        os.path.exists(dir) == False
    ), f"Directory check failed! {dir} exists even though we expect it not to."


@then("directory {dir} will exist")
def step_impl(context, dir):
    assert (
        os.path.exists(dir) == True
    ), f"Directory check failed! {dir} doesn't exist even though we expect it to."


def onerror(func, path, exc_info):
    os.chmod(path, stat.S_IWUSR)
    func(path)


@when("we run secret-magpie-cli with a gitleaks rules.toml file")
def step_impl(context):
    run_secret_magpie(
        context,
        engines="gitleaks",
        args=[f"--gl-config=rules.toml"],
    )


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

                case "commitdate":
                    current_repo.git.add(A=True)
                    if not commit_all:
                        commit_all = True
                        if len(rule) > 1:
                            current_repo.index.commit("Commit.", commit_date=rule[1])
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
