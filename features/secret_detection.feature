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
    Scenario: Validate that we can detect secrets for remote repos
        When we run secret-magpie-cli with engines: all
        Then there will be 4 secrets detected
