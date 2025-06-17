import os
from behave import given, when, then
from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv

# Load Databricks environment variables from .env file
load_dotenv()

def table_exists(dbx: WorkspaceClient, catalog: str, schema: str, table: str) -> bool:
    query = f"SHOW TABLES IN {catalog}.{schema} LIKE '{table}'"
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

    try:
        statement = dbx.statement_execution.execute_statement(
            statement=query,
            warehouse_id=warehouse_id,
            catalog=catalog,
            schema=schema,
        )
        result = dbx.statement_execution.get_statement(statement.statement_id)
        if result.result and result.result.data_array:
            rows = result.result.data_array
            # Confirm table in results
            return any(table in row for row in rows if row)
        else:
            # If no results, the table does not exist
            return False

    except Exception as e:
        raise e


@given("I connect to the Databricks workspace")
def step_connect_to_databricks(context):
    context.dbx = WorkspaceClient()

@when('I check for the table "{table_full_name}"')
def step_check_table_exists(context, table_full_name):
    context.table_full_name = table_full_name
    catalog, schema, table = table_full_name.split(".", 2)
    context.table_found = table_exists(context.dbx, catalog, schema, table)

@then("the table should exist")
def step_assert_table_exists(context):
    assert context.table_found, f"Table {context.table_full_name} was not found"

@then("the table should not exist")
def step_assert_table_not_exists(context):
    assert not context.table_found, f"Table {context.table_full_name} was found but should not exist"
