Feature: Validate secret detection against various engines.
    @localrepos
    @fixture.branchTest
    Scenario Outline: Detect four unique secrets over two branches with engine: <engine>
        Given we switch branch to master

        When we run secret-magpie-cli with engines: <engine>
        Then there will be 4 unique secrets detected

        Examples:
            | engine     |
            | all        |
            | gitleaks   |
            | trufflehog |
    
    @localrepos
    @fixture.branchTest
    Scenario Outline: Detect four unique secrets in the dev branch in single branch mode with engines: <engine>
        When we run secret-magpie-cli in single branch mode, secret storing disabled, output format csv and engines: <engine>
        Then there will be 4 unique secrets detected

        Examples:
            | engine     |
            | all        |
            | gitleaks   |
            | trufflehog |
    
    @localrepos
    @fixture.branchTest
    Scenario Outline: Detect two unique secrets in the master branch in single branch mode with engines: <engine>
        Given we switch branch to master

        When we run secret-magpie-cli in single branch mode, secret storing disabled, output format csv and engines: <engine>
        Then there will be 2 unique secrets detected

        Examples:
            | engine     |
            | all        |
            | gitleaks   |
            | trufflehog |

    @localrepos
    @fixture.wantsSSHKey
    Scenario: Ensure gitleaks can detect secrets
        When we run secret-magpie-cli with engines: gitleaks
        Then there will be 1 secrets detected

    @localrepos
    @fixture.wantsSSHKey
    Scenario: Ensure trufflehog can detect secrets
        When we run secret-magpie-cli with engines: trufflehog
        Then there will be 1 secrets detected

    @github.secretmagpie-testing
    Scenario: Validate that we can detect secrets for a GitHub remote
        When we run secret-magpie-cli with engines: all
        Then there will be 4 secrets detected

    @azuredevops.PunkSecurity
    Scenario: Ensure that we can detect secrets in AzureDevOps organisations
        When we run secret-magpie-cli with engines: all
        Then there will be 4 secrets detected

    @localrepos
    @fixture.wantsFixedDateSecret
    Scenario: Detect all secrets with fixed dates when we don't ignore secrets
        When we run secret-magpie-cli in multi branch mode, ignoring commits older than None extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 2 secrets detected

    @localrepos
    @fixture.wantsFixedDateSecret
    Scenario Outline: Detect no secrets with fixed dates when we ignore secrets older than 2022-01-01T00:00:00+00:00 in <mode> branch mode.
        When we run secret-magpie-cli in <mode> branch mode, ignoring commits older than 2022-01-01T00:00:00+00:00 extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 0 secrets detected

        Examples:
            | mode   |
            | single |
            | multi  |

    @skipinrunner 
    @gitlab.secretmagpie-testing.https://gitlab.punksecurity.io
    @pat.SECRETMAGPIE_GITLAB_CE_PAT
    Scenario: Validate that we can detect secrets for GitLab CE remote
        When we run secret-magpie-cli with engines: all
        Then there will be 4 secrets detected

    @gitlab.secretmagpie-testing
    Scenario: Validate that we can detect secrets for GitLab remote
        When we run secret-magpie-cli with engines: all
        Then there will be 4 secrets detected

    @github.secretmagpie-testing
    Scenario: Ensure that we still detect secrets on GitHub remote works when we turn off HTTPS validation
        When we run secret-magpie-cli in multi branch mode, https validation disabled, ignoring commits older than None, extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 4 secrets detected

    @gitlab.secretmagpie-testing
    Scenario: Ensure that we still detect secrets on GitLab remote works when we turn off HTTPS validation
        When we run secret-magpie-cli in multi branch mode, https validation disabled, ignoring commits older than None, extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 4 secrets detected

    @skipinrunner
    @gitlab.secretmagpie-testing.https://gitlab.punksecurity.io
    @pat.SECRETMAGPIE_GITLAB_CE_PAT
    Scenario: Ensure that we still detect secrets on GitLab CE remote works when we turn off HTTPS validation
        When we run secret-magpie-cli in multi branch mode, https validation disabled, ignoring commits older than None, extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 4 secrets detected
    
    @azuredevops.PunkSecurity
    Scenario: Ensure that we still detect secrets on AzureDevOps remote works when we turn off HTTPS validation
        When we run secret-magpie-cli in multi branch mode, https validation disabled, ignoring commits older than None, extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 4 secrets detected

    @github.secretmagpie-testing
    Scenario: Validate that repo filtering works for GitHub
        Given we have a file called repos.txt with content
            """
            https://github.com/secretmagpie-testing/ssh_key
            """
        When we run secret-magpie-cli in multi branch mode, to scan list repos.txt, https validation enabled, ignoring commits older than None, extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 2 secrets detected
    
    @gitlab.secretmagpie-testing
    Scenario: Validate that repo filtering works for GitLab
        Given we have a file called repos.txt with content
            """
            https://gitlab.com/secretmagpie-testing/ssh_key
            """
        When we run secret-magpie-cli in multi branch mode, to scan list repos.txt, https validation enabled, ignoring commits older than None, extra context disabled, secret storing enabled, output format csv and engines: all
        Then there will be 2 secrets detected
    

    @localrepos
    @fixture.wantsAWSSecret
    Scenario: Ensure that we only detect an AWS secret locally, when a matching rule is provided by toml file, and with only gitleaks enabled
        Given we have a file called rules.toml with content
            """
            [[rules]]
            description = "AWS"
            id = "aws-access-token"
            regex = '''AKIAYVP4CIPPERUVIFXG'''
            keywords = [
                "akia","agpa","aida","aroa","aipa","anpa","anva","asia",
            ]
            """
        When we run secret-magpie-cli with a gitleaks rules.toml file
        Then there will be 1 secrets detected
    
    @localrepos
    @fixture.wantsAWSSecret
    @fixture.wantsSSHKey
    Scenario: Ensure that we only detect 1 AWS secret locally, and not the SSH key, when a matching rule is provided by toml file, and with only gitleaks enabled
        Given we have a file called rules.toml with content
            """
            [[rules]]
            description = "AWS"
            id = "aws-access-token"
            regex = '''AKIAYVP4CIPPERUVIFXG'''
            keywords = [
                "akia","agpa","aida","aroa","aipa","anpa","anva","asia",
            ]
            """
        When we run secret-magpie-cli with a gitleaks rules.toml file
        Then there will be 1 secrets detected

    @localrepos
    @fixture.wantsAWSSecret
    Scenario: Ensure that we don't detect any secrets locally, when there are no matching rules provided by toml file, and with only gitleaks enabled
        Given we have a file called rules.toml with content
            """
            """
        When we run secret-magpie-cli with a gitleaks rules.toml file
        Then there will be 0 secrets detected

