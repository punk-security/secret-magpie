Feature: Validate that the output of the various tools and secret magpie itself loosely match an expected pattern
    @localrepos
    @fixture.wantsSSHKey
    Scenario Outline: Validate that <tool>'s output is consistent with what we expected
        When we run <tool> capturing JSON output
        Then the JSON output will match file <tool>.json

        Examples:
            | tool       |
            | Trufflehog |
            | Gitleaks   |

    @localrepos
    @fixture.wantsAWSSecret
    Scenario: Validate that results.csv contains expected data when secret-magpie-cli is run
        When we run secret-magpie-cli with output format csv and engines: all
        Then results.csv will match file secret-magpie.csv

    @localrepos
    @fixture.wantsAWSSecret
    Scenario: Validate that results.csv contains expected data when secret-magpie-cli is run with secret storing disabled
        When we run secret-magpie-cli with secret storing disabled, output format csv and engines: all
        Then results.csv will match file secret-magpie-no-secrets.csv
    
    @localrepos
    @fixture.wantsAWSSecret
    Scenario: Validate that results.csv contains expected data when secret-magpie-cli is run with secret storing disabled
        When we run secret-magpie-cli in multi branch mode, extra context enabled, secret storing enabled, output format csv and engines: all
        Then results.csv will match file secret-magpie-extra-context.csv

    @github.secretmagpie-testing
    Scenario: Validate that results.csv contains expected data when secret-magpie-cli is run against remote repos
        When we run secret-magpie-cli with output format csv and engines: all
        Then results.csv will match file secret-magpie-github.csv

    @github.secretmagpie-testing
    Scenario: Validate that results.csv contains expected data when secret-magpie-cli is run against remote repos with secret storing disabled
        When we run secret-magpie-cli with secret storing disabled, output format csv and engines: all
        Then results.csv will match file secret-magpie-github-no-secrets.csv
