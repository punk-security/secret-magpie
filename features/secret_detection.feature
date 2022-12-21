Feature: Validate secret detection against various engines.
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
    
    @fixture.branchTest
    Scenario Outline: Detect four unique secrets in the dev branch in single branch mode with engines: <engine>
        When we run secret-magpie-cli in single branch mode, secret storing disabled, output format csv and engines: <engine>
        Then there will be 4 unique secrets detected

        Examples:
            | engine     |
            | all        |
            | gitleaks   |
            | trufflehog |
    
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

    @fixture.wantsSSHKey
    Scenario: Ensure gitleaks can detect secrets
        When we run secret-magpie-cli with engines: gitleaks
        Then there will be 1 secrets detected

    @fixture.wantsSSHKey
    Scenario: Ensure trufflehog can detect secrets
        When we run secret-magpie-cli with engines: trufflehog
        Then there will be 1 secrets detected
