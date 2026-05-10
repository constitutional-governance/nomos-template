@api @enforced
Feature: REST API URL structure

  Reference: ADR-001
  Status: enforced

  @enforced
  Scenario: Valid resource URL is accepted
    Given the API path "/api/v1/payments"
    When I validate the URL structure
    Then it should be valid

  @enforced
  Scenario: Missing version prefix is rejected
    Given the API path "/payments/pay-123"
    When I validate the URL structure
    Then it should be invalid
    And the reason should mention "version prefix required"

  @enforced
  Scenario: Verb in URL path is rejected
    Given the API path "/api/v1/processPayment"
    When I validate the URL structure
    Then it should be invalid
    And the reason should mention "resource name must be a noun"

  @wip
  Scenario: Offset pagination is rejected for unbounded collections
    Given a collection endpoint without a cursor parameter
    And the collection is marked as unbounded
    When I validate the pagination contract
    Then it should be invalid
