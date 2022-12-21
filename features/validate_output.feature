Feature: Validate that the results files produced by secret-magpie-cli is of valid form and contains expected data.
    @fixture.wantsSSHKey
    Scenario Outline: Validate that the <format> output is of valid form when a repo contains multi-line secrets
        When we run secret-magpie-cli with output format <format> and engines: all
        Then the results file will be of valid form

        Examples:
            | format |
            | json   |
            | csv    |

    @fixture.wantsAWSSecret
    Scenario Outline: Ensure that the secrets column is blank when using format <format> and we disable storing secrets
        When we run secret-magpie-cli with secret storing disabled, output format <format> and engines: all
        Then the secret field within the output will be blank

        Examples:
            | format |
            | json   |
            | csv    |
    
    Scenario: Ensure that when we run secret-magpie-cli with no engines enabled, we get the correct error
        When we run secret-magpie-cli with engines: none
        Then secret-magpie-cli's output will be
            """
            ERROR: No tools to scan with
            """
