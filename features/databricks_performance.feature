Feature: Databricks Performance Optimization
  As a platform engineer
  I want to ensure tables and clusters are optimized
  So that queries run efficiently and costs are controlled

  Background:
    Given I connect to the Databricks workspace
    And I have permissions to read table and cluster metadata

  @performance @file-sizing
  Scenario: Delta tables should not have excessive small files
    When I analyze the file metrics for each table
    Then the average file size should be between 64MB and 1GB
    And no table should have more than 10000 files under 10MB

  @performance @partitions
  Scenario: Partitioned tables should not be over-partitioned
    When I count the number of partitions per table
    Then no table should have more than 10000 partitions
    And partition columns should not include high-cardinality fields
    And average partition size should be at least 128MB

  @performance @auto-termination
  Scenario: All clusters must have auto-termination enabled
    When I check each cluster's configuration
    Then all-purpose clusters should have auto_termination_minutes <= 120
    And job clusters should have auto_termination after job completion
    And no cluster should have auto_termination disabled