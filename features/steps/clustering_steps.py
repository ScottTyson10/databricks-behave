from behave import when, then
from databricks_utils import for_each_table, get_table_detail, get_table_metadata
import json

@when('I check all tables in "{catalog_schema}" are clustered or cluster_exclusion flag is set')
def step_check_all_tables_clustered_or_cluster_exclusion(context, catalog_schema):
    def check(_, catalog, schema, table):
        detail = get_table_detail(context.dbx, catalog, schema, table)
        clustering_columns = json.loads(detail.get("clusteringColumns", "[]"))
        cluster_by_auto = json.loads(detail.get("clusterByAuto", "false"))
        if (isinstance(clustering_columns, list) and len(clustering_columns) > 0) or (cluster_by_auto is True):
            return True
        table_properties: dict = get_table_metadata(context.dbx, catalog, schema, table).get("table_properties")
        return table_properties.get("cluster_exclusion") in {"true", "1"}
    for_each_table(context, catalog_schema, check, 'failed_clustered_tables')


@then('all tables should be clustered or auto-clustered or have cluster_exclusion flag')
def step_assert_all_tables_clustered_or_auto(context):
    assert not context.failed_clustered_tables, f"The following tables are not clustered, not auto-clustered, and have no cluster_exclusion flag: {context.failed_clustered_tables}"
