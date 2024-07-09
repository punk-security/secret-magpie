Feature: Validate that the results files produced by secret-magpie-cli is of valid form and contains expected data.
    @localrepos
    @fixture.wantsSSHKey
    Scenario Outline: Validate that the <format> output is of valid form when a repo contains multi-line secrets
        When we run secret-magpie-cli with output format <format> and engines: all
        Then the results file will be of valid form

        Examples:
            | format |
            | json   |
            | csv    |

    @localrepos
    @fixture.wantsAWSSecret
    Scenario Outline: Ensure that the secrets column is blank when using format <format> and we disable storing secrets
        When we run secret-magpie-cli with secret storing disabled, output format <format> and engines: all
        Then the secret field within the output will be blank

        Examples:
            | format |
            | json   |
            | csv    |
    
    @localrepos
    Scenario: Ensure that when we run secret-magpie-cli with no engines enabled, we get the correct error
        When we run secret-magpie-cli with engines: none
        Then secret-magpie-cli's output will be
            """
            ERROR: No tools to scan with
            """

    @github.secretmagpie-testing
    Scenario: Ensure that we clean up repos that we've cloned when using a remote
        When we run secret-magpie-cli with engines: all
        Then directory 7c484be0 won't exist
        And directory 42cbad53 won't exist

    @no-cleanup
    @github.secretmagpie-testing
    @rmtree.7c484be0
    @rmtree.42cbad53
    Scenario: Ensure that we clean up repos that we've cloned when using a remote
        When we run secret-magpie-cli with engines: all
        Then directory 7c484be0 will exist
        And directory 42cbad53 will exist

    @localrepos
    @wantsAWSSecret
    Scenario: Ensure that the date field within the repo is parseable in ISO8601 format.
        When we run secret-magpie-cli with engines: all
        Then the date column of results.csv will be ISO8601 format

    @localrepos
    @wantsAWSSecret
    Scenario: Ensure that secret-magpie-cli gives the expected error when we run it with an invalid threshold date
        When we run secret-magpie-cli in multi branch mode, ignoring commits older than invaliddate extra context disabled, secret storing enabled, output format csv and engines: all
        Then secret-magpie-cli's output will be
            """
            ERROR: Invalid ISO format string.
            """

    @localrepos
    Scenario: Ensure that secret-magpie-cli gives the expected error when we provide an invalid gitleaks toml file
        When we run secret-magpie-cli with a gitleaks rules_not_found.toml file
        Then secret-magpie-cli's output will be
            """
            ERROR: File at rules_not_found.toml not found.
            """

    @localrepos
    Scenario: Ensure that secret-magpie-cli gives the expected error when gitleaks is not found
        Given gitleaks is not present
        When we run secret-magpie-cli with engines: gitleaks
        Then secret-magpie-cli's error output will be
            """
            ❌ error: Could not find Gitleaks on your system. Ensure it's on the PATH or pass --disable-gitleaks
            """

    @localrepos
    Scenario: Ensure that secret-magpie-cli gives the expected error when trufflehog is not found
        Given trufflehog is not present
        When we run secret-magpie-cli with engines: trufflehog
        Then secret-magpie-cli's error output will be
            """
            ❌ error: Could not find Trufflehog on your system. Ensure it's on the PATH or pass --disable-trufflehog
            """
