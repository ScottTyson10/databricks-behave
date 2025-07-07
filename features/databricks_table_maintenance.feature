Feature: Databricks Table Maintenance
  As a data engineer
  I want to ensure tables are properly maintained
  So that performance and costs are optimized

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table metadata and history

  @maintenance @vacuum
  Scenario: Delta tables should be vacuumed regularly
    When I check the table history for VACUUM operations
    Then each table should have a VACUUM operation within the last 30 days
    Or have a "no_vacuum_needed" tag

  @maintenance @vacuum @dev
  Scenario: Delta tables should be vacuumed within custom threshold
    When I check the table history for VACUUM operations  
    Then each table should have a VACUUM operation within the last 7 days
    Or have a "no_vacuum_needed" tag

  @maintenance @orphaned @dev
  Scenario: Identify potentially orphaned tables
    When I check table access patterns
    Then I should flag tables with:
      | no reads in the last 90 days |
      | AND no updates in the last 90 days |
      | AND not tagged with "archive" or "reference" |