from behave import when, then
from databricks_utils import list_tables_in_schema


@when('I check for the table "{table_full_name}"')
def step_check_table_exists(context, table_full_name):
    catalog, schema, table = table_full_name.split(".", 2)
    tables = list_tables_in_schema(context.dbx, catalog, schema)
    context.table_full_name = table_full_name
    context.table_found = table in tables


@then("the table should exist")
def step_assert_table_exists(context):
    assert context.table_found, f"Table {context.table_full_name} was not found"


@then("the table should not exist")
def step_assert_table_not_exist(context):
    assert not context.table_found, f"Table {context.table_full_name} was found but should not exist"
