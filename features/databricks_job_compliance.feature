Feature: Databricks Job Compliance
  As a platform administrator
  I want to ensure all jobs follow security and reliability best practices
  So that our data platform is secure and reliable

  Background:
    Given I have a connection to the Databricks workspace
    And I have permissions to list and describe jobs

  @jobs @service-principal
  Scenario: Production jobs must use service principals
    When I check all jobs in the workspace
    Then no job should have a run_as containing "@"
    And jobs with "prod" in the name must have service principal

  @jobs @service-principal  
  Scenario: Production jobs with "production" keyword must use service principals
    When I check all jobs in the workspace
    Then jobs with "production" in the name must have service principal

  @jobs @retry
  Scenario: Production jobs must have retry policies
    When I check jobs with "prod" in their name
    Then each production job should have max_retries > 0
    And retry_on_timeout should be true

  @jobs @retry
  Scenario: Production jobs with "production" keyword must have retry policies  
    When I check jobs with "production" in their name
    Then each production job should have max_retries > 0
    And retry_on_timeout should be true

  @jobs @timeout
  Scenario: All jobs must have timeout settings
    When I check each job's timeout configuration
    Then each job should have timeout_seconds defined
    And timeout_seconds should be between 300 and 86400

  @jobs @cluster
  Scenario: Jobs should use job clusters not all-purpose clusters
    When I check each job's cluster configuration
    Then jobs should use new_cluster configuration
    And should not reference existing_cluster_id
    Unless tagged with "interactive" or "debug"