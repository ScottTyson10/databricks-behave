# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Databricks table validation testing framework using Behave (BDD). It validates table configurations for clustering, metadata, and existence requirements.

### Dependencies
- **behave 1.2.6**: BDD testing framework
- **databricks-sdk 0.57.0**: Databricks Python SDK for SQL warehouse operations
- **python-dotenv 1.1.0**: Environment variable management
- **pytest/pytest-bdd**: Included but not currently used in the test suite

## Essential Commands

### Setup
```bash
# Create/activate virtual environment (Python 3.10)
make venv

# Configure environment variables
cp .env.template .env
# Edit .env with your Databricks credentials:
# - DATABRICKS_TOKEN
# - DATABRICKS_HOST
# - DATABRICKS_WAREHOUSE_ID
```

### Testing
```bash
# Run all tests
make test

# Run specific test tags
make test-dev        # Development tests only
make test-clustering # Clustering validation tests
make test-metadata   # Metadata validation tests

# Run individual feature files
behave features/databricks_table_validation.feature

# Run with specific tags combination
behave --tags=@databricks --tags=@clustering

# Run a single scenario by name
behave -n "Scenario name"

# Debug mode with verbose output
behave --verbose --no-capture
```

## Architecture

### Test Structure
- **features/**: Gherkin feature files defining test scenarios
- **features/steps/**: Step definitions implementing test logic
  - `databricks_utils.py`: Core utilities for Databricks operations (features/steps/databricks_utils.py)
  - `environment_steps.py`: Environment-related step definitions
  - `table_existence_steps.py`: Table existence validation steps
  - `metadata_steps.py`: Metadata validation steps
  - `clustering_steps.py`: Clustering validation steps
- **features/environment.py**: Test setup/teardown hooks (features/environment.py)

### Key Design Patterns
1. **Shared Context**: Uses Behave's context object to share state between steps
2. **Bulk Validation**: `for_each_table` function in databricks_utils.py enables efficient validation of multiple tables
3. **Auto Setup/Teardown**: Test tables are automatically created before tests and cleaned up after
4. **Tag-based Execution**: Tests can be filtered using tags (@dev, @clustering, @metadata)

### Core Utility Functions (features/steps/databricks_utils.py)
- **`execute_query(context, query)`**: Executes SQL queries using Databricks SQL warehouse
- **`for_each_table(context, validation_function, tables)`**: Iterates through tables and applies validation
- **`get_table_clustering_info(context, full_table_name)`**: Retrieves clustering columns for a table
- **`get_all_tables_in_catalog(context, catalog_name)`**: Lists all tables in a catalog
- **`get_table_properties(context, full_table_name)`**: Fetches table properties including cluster_exclusion

### Test Data Management
The framework automatically creates three test tables in `workspace.test_clustering`:
- `clustered_table`: Table with explicit clustering on columns (c1, c2)
- `auto_clustered_table`: Table with AUTO clustering
- `no_clustering_table`: Table with `cluster_exclusion=true` property

To skip automatic setup/teardown during development:
- Set `context.skip_setup = True` in environment.py:8
- Set `context.skip_teardown = True` in environment.py:9

### Environment Configuration
Required environment variables (via .env file):
- `DATABRICKS_TOKEN`: Personal access token for authentication
- `DATABRICKS_HOST`: Databricks workspace URL (e.g., https://xxx.cloud.databricks.com)
- `DATABRICKS_WAREHOUSE_ID`: SQL warehouse ID for query execution

Default values:
- Test catalog: `workspace`
- Test schema: `test_clustering`

### Writing New Tests
1. Add scenarios to existing feature files or create new .feature files
2. Implement step definitions in appropriate files under features/steps/
3. Use existing utilities from databricks_utils.py for database operations
4. Tag scenarios appropriately for selective execution

### Common Development Tasks
```bash
# Add new dependencies
echo "package==version" >> requirements.txt
make install-requirements

# Clean and reinstall environment
make pyenv-rm
make install-venv

# Debug a specific scenario (add @dev tag to scenario)
make test-dev
```

### Debugging Tips
- **Authentication errors**: Verify DATABRICKS_TOKEN and DATABRICKS_HOST in .env file
- **Warehouse connection issues**: Check DATABRICKS_WAREHOUSE_ID is valid and warehouse is running
- **Table not found**: Ensure test tables are created (check skip_setup flag in environment.py)
- **Step definition errors**: Use `behave --verbose` to see detailed error messages