Feature: Basic functionality

    @basic
    Scenario: Check that 1 + 1 equals 2
        Given I have two numbers 1 and 1
        When I add them
        Then the result should be 2