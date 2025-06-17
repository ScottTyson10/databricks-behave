Feature: Verify table presence in Databricks
  
  @databricks @tables
  Scenario: Check if table exists
    Given I connect to the Databricks workspace
    When I check for the table "samples.accuweather.forecast_daily_calendar_imperial"
    Then the table should exist

  @databricks @tables
  Scenario: Check if table does not exist
    Given I connect to the Databricks workspace
    When I check for the table "samples.accuweather.forecast_daily_calendar_imperial_not_exist"
    Then the table should not exist