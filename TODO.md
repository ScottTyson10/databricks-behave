1. Clustering or Explicit Opt-out
Description: Ensures every table either has clustering enabled for performance optimization or has explicitly documented why clustering isn't appropriate.

Gherkin Scenario:


gherkin
Feature: Table Clustering Compliance
  Scenario: All tables should have clustering or opt-out tag
    Given I have access to all tables in the workspace
    When I check each table's clustering configuration
    Then each table should either:
      | have clustering columns defined |
      | OR have a "no_clustering" tag set to "true" |
    And no tables should lack both clustering and the opt-out tag
SDK Implementation:


python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
# List all catalogs
catalogs = w.catalogs.list()
# List schemas in catalog
schemas = w.schemas.list(catalog_name="catalog_name")
# List tables
tables = w.tables.list(catalog_name="catalog_name", schema_name="schema_name")
# Get table details including clustering columns
table_info = w.tables.get(full_name="catalog.schema.table")
# Check table_info.properties for tags and table_info.clustering_columns
2. Basic Documentation
Description: Verifies that all tables have meaningful descriptions to help users understand the data's purpose and content.

Gherkin Scenario:


gherkin
Feature: Table Documentation
  Scenario: All tables must have descriptions
    Given I have access to all tables in the workspace
    When I check each table's metadata
    Then each table should have a non-empty "comment" field
    And the comment should not be generic like "table" or "data"
SDK Implementation:


python
# Get table metadata
table_info = w.tables.get(full_name="catalog.schema.table")
# Check table_info.comment - should not be None or empty
3. Column Descriptions
Description: Ensures columns are documented to help users understand field meanings and appropriate usage.

Gherkin Scenario:


gherkin
Feature: Column Documentation Coverage
  Scenario: Tables should have documented columns
    Given I have access to all tables in the workspace
    And a threshold of 80% column documentation
    When I count columns with non-empty descriptions
    Then at least 80% of columns per table should have descriptions
    And critical columns (containing "id", "date", "amount") must have descriptions
SDK Implementation:


python
# Get table columns
table_info = w.tables.get(full_name="catalog.schema.table")
# Check table_info.columns - each column has a 'comment' field
# Calculate percentage: len([c for c in table_info.columns if c.comment]) / len(table_info.columns)
4. Service Principal Usage
Description: Ensures automated jobs run under service principals rather than personal accounts for security and continuity.

Gherkin Scenario:


gherkin
Feature: Job Service Principal Compliance
  Scenario: Production jobs must use service principals
    Given I have access to all jobs in the workspace
    When I check each job's run_as configuration
    Then no job should have a run_as containing "@"
    And jobs with "prod" or "production" in the name must have service principal
SDK Implementation:


python
# List all jobs
jobs = w.jobs.list()
# For each job, check job.settings.run_as
# If run_as.user_name exists and contains "@", it's a user account
# If run_as.service_principal_name exists, it's compliant
5. Retry Configuration
Description: Ensures production jobs have retry policies to handle transient failures automatically.

Gherkin Scenario:


gherkin
Feature: Job Retry Configuration
  Scenario: Production jobs must have retry policies
    Given I have access to all jobs in the workspace
    When I check jobs with "prod" or "production" in their name
    Then each production job should have max_retries > 0
    And retry_on_timeout should be true
SDK Implementation:


python
# Get job details
job = w.jobs.get(job_id=job_id)
# Check job.settings.max_retries (should be > 0)
# Check job.settings.retry_on_timeout (should be True)
6. Timeout Settings
Description: Prevents runaway jobs by ensuring reasonable timeout configurations.

Gherkin Scenario:


gherkin
Feature: Job Timeout Configuration
  Scenario: All jobs must have timeout settings
    Given I have access to all jobs in the workspace
    When I check each job's timeout configuration
    Then each job should have timeout_seconds defined
    And timeout_seconds should be between 300 and 86400 (5 min to 24 hours)
SDK Implementation:


python
# Get job details
job = w.jobs.get(job_id=job_id)
# Check job.settings.timeout_seconds
# Verify it's set and within reasonable bounds
7. Cluster Configuration
Description: Ensures jobs use ephemeral job clusters rather than expensive all-purpose clusters.

Gherkin Scenario:


gherkin
Feature: Job Cluster Best Practices
  Scenario: Jobs should use job clusters not all-purpose clusters
    Given I have access to all jobs in the workspace
    When I check each job's cluster configuration
    Then jobs should use new_cluster configuration
    And should not reference existing_cluster_id
    Unless tagged with "interactive" or "debug"
SDK Implementation:


python
# Get job details
job = w.jobs.get(job_id=job_id)
# Check job.settings.tasks[].new_cluster exists
# Verify job.settings.tasks[].existing_cluster_id is not used
# Or check job.settings.job_clusters is defined
8. Vacuum History
Description: Ensures Delta tables are regularly maintained to optimize storage and performance.

Gherkin Scenario:


gherkin
Feature: Delta Table Maintenance
  Scenario: Delta tables should be vacuumed regularly
    Given I have access to all Delta tables in the workspace
    When I check the table history for VACUUM operations
    Then each table should have a VACUUM operation within the last 30 days
    Or have a "no_vacuum_needed" tag
SDK Implementation:


python
# Get table history
history = w.tables.get_table_history(full_name="catalog.schema.table")
# Look for operations where history.operation = "VACUUM"
# Check history.timestamp for recency
9. Orphaned Tables
Description: Identifies unused tables that may be candidates for removal to reduce clutter and costs.

Gherkin Scenario:


gherkin
Feature: Table Usage Monitoring
  Scenario: Identify potentially orphaned tables
    Given I have access to all tables in the workspace
    When I check table access patterns
    Then I should flag tables with:
      | no reads in the last 90 days |
      | AND no updates in the last 90 days |
      | AND not tagged with "archive" or "reference" |
SDK Implementation:


python
# This requires query history analysis
# Use w.query_history.list() to get recent queries
# Parse query text to find table references
# Or use table lineage APIs if available
# Alternative: Check table properties for last_accessed custom property
10. File Sizing
Description: Ensures Delta tables maintain optimal file sizes for query performance.

Gherkin Scenario:


gherkin
Feature: Delta Table File Optimization
  Scenario: Delta tables should not have excessive small files
    Given I have access to all Delta tables in the workspace
    When I analyze the file metrics for each table
    Then the average file size should be between 64MB and 1GB
    And no table should have more than 10000 files under 10MB
SDK Implementation:


python
# Get table details
detail = w.tables.get(full_name="catalog.schema.table")
# Use SQL through w.statement_execution.execute_statement():
# "DESCRIBE DETAIL catalog.schema.table"
# Check numFiles and sizeInBytes to calculate average
11. Partition Health
Description: Prevents over-partitioning which can severely degrade query performance.

Gherkin Scenario:


gherkin
Feature: Partition Strategy Health
  Scenario: Partitioned tables should not be over-partitioned
    Given I have access to all partitioned tables in the workspace
    When I count the number of partitions per table
    Then no table should have more than 10000 partitions
    And partition columns should not include high-cardinality fields
    And average partition size should be at least 128MB
SDK Implementation:


python
# Get table partitioning info
table_info = w.tables.get(full_name="catalog.schema.table")
# Check table_info.partition_columns
# Use SHOW PARTITIONS via statement execution to count
# Calculate partition sizes using DESCRIBE DETAIL
12. Auto-termination Settings
Description: Ensures clusters automatically shut down when idle to control costs.

Gherkin Scenario:


gherkin
Feature: Cluster Auto-termination
  Scenario: All clusters must have auto-termination enabled
    Given I have access to all clusters in the workspace
    When I check each cluster's configuration
    Then all-purpose clusters should have auto_termination_minutes <= 120
    And job clusters should have auto_termination after job completion
    And no cluster should have auto_termination disabled