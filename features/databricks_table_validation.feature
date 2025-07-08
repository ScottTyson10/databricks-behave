Feature: Databricks Table Existence, Metadata, and Clustering Validation

  @databricks @tables @dev
  Scenario: Check if table exists
    Given I connect to the Databricks workspace
    When I check for the table "workspace.test_clustering.clustered_table"
    Then the table should exist

  @databricks @tables @dev
  Scenario: Check if table does not exist
    Given I connect to the Databricks workspace
    When I check for the table "workspace.test_clustering.non_existent_table"
    Then the table should not exist

  @databricks @tables @metadata
  Scenario: All tables in a schema are managed or have a comment
    Given I connect to the Databricks workspace
    When I check all tables in "workspace.test_clustering" have a managed location
    Then all tables should have a managed location

  @databricks @tables @clustering
  Scenario: All tables in a schema are clustered, auto-clustered, or explicitly excluded
    Given I connect to the Databricks workspace
    When I check all tables in "workspace.test_clustering" are clustered or cluster_exclusion flag is set
    Then all tables should be clustered or auto-clustered or have cluster_exclusion flag

  @databricks @tables @documentation
  Scenario: All tables must have meaningful descriptions
    Given I connect to the Databricks workspace
    When I check all tables in "workspace.test_clustering" have metadata
    Then each table should have a non-empty "comment" field
    And the comment should not be generic like "table" or "data"

  @databricks @tables @documentation @dev
  Scenario: Tables should have documented columns
    Given I connect to the Databricks workspace
    And a threshold of 80% column documentation
    When I count columns with non-empty descriptions in "workspace.test_clustering"
    Then at least 80% of columns per table should have descriptions
    And critical columns (containing "id", "date", "amount") must have descriptions
