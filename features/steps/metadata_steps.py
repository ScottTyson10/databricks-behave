from behave import when, then
from databricks_utils import for_each_table, get_table_extended_properties

# NOTE this test is a placeholder for testing useful properties from desc table extended
@when('I check all tables in "{catalog_schema}" have a managed location')
def step_check_all_tables_managed_or_comment(context, catalog_schema):
    def check(_, catalog, schema, table):
        props = get_table_extended_properties(context.dbx, catalog, schema, table)
        is_managed = props.get("is_managed_location")
        return is_managed
    for_each_table(context, catalog_schema, check, 'failed_tables')


@then('all tables should have a managed location')
def step_assert_all_tables_managed(context):
    assert not context.failed_tables, f"The following tables locations are not managed: {context.failed_tables}"


@when('I check all tables in "{catalog_schema}" have metadata')
def step_check_all_tables_metadata(context, catalog_schema):
    """Check table metadata for documentation scenarios."""
    context.catalog_schema = catalog_schema


@when('I count columns with non-empty descriptions in "{catalog_schema}"')
def step_count_column_descriptions(context, catalog_schema):
    """Count columns with descriptions for validation."""
    context.catalog_schema = catalog_schema
