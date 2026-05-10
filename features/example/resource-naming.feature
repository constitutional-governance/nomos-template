# STARTER EXAMPLE — replace this file with your first governance check.
#
# How to use this file:
#   1. Copy it to features/<your-domain>/<your-rule>.feature
#   2. Write step definitions in features/steps/<your-domain>_steps.py
#   3. Change @wip to @enforced once the step definitions exist and run in CI
#   4. Delete this file
#
# See examples/kafka/features/ for a complete working implementation.

@wip
Feature: Resource naming convention

  Reference: ADR-001
  Status: wip — replace with your first enforced rule

  @wip
  Scenario: Valid resource name is accepted
    Given the resource name "valid-example-name"
    When I validate the resource name
    Then it should be valid

  @wip
  Scenario: Empty resource name is rejected
    Given the resource name ""
    When I validate the resource name
    Then it should be invalid
    And the reason should mention "name cannot be empty"
