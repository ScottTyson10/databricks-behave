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
  Scenario: All tables in a schema are clustered or auto-clustered
    Given I connect to the Databricks workspace
    When I check all tables in "workspace.test_clustering" are clustered or auto-clustered
    Then all tables should be clustered or auto-clustered
