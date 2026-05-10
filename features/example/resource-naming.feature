# Replace this file with your first governance check.
# @enforced scenarios run in CI and block merges.
# @wip scenarios are documented aspirations — implement step definitions to enforce them.
#
# See examples/ for complete domain examples (Kafka, REST API).

@example
Feature: Resource naming convention

  # Replace with your ADR reference
  Reference: ADR-001
  Status: example — replace with your first rule

  @enforced
  Scenario: Valid resource name is accepted
    # TODO: replace with your naming rule
    Given the resource name "valid-example-name"
    When I validate the resource name
    Then it should be valid

  @enforced
  Scenario: Empty resource name is rejected
    Given the resource name ""
    When I validate the resource name
    Then it should be invalid
    And the reason should mention "name cannot be empty"

  @wip
  Scenario: Resource name with invalid characters is rejected
    Given the resource name "Invalid_Name!"
    When I validate the resource name
    Then it should be invalid
