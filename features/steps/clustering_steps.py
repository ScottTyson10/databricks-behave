from behave import when, then
from databricks_utils import for_each_table, get_table_detail, get_table_metadata, get_table_properties
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


@then('each table should have clustering or cluster_exclusion property')
def step_check_clustering_or_optout(context):
    """Check that tables either have clustering or explicit opt-out."""
    def check_clustering_compliance(detail, catalog, schema, table):
        # First check for clustering
        clustering_columns = json.loads(detail.get("clusteringColumns", "[]"))
        cluster_by_auto = json.loads(detail.get("clusterByAuto", "false"))
        
        if (isinstance(clustering_columns, list) and len(clustering_columns) > 0) or (cluster_by_auto is True):
            return True
        
        # Check for opt-out property using new utility
        properties = get_table_properties(context, f"{catalog}.{schema}.{table}")
        if properties.get('cluster_exclusion') == 'true':
            return True
        
        return False
    
    for_each_table(context, context.catalog_schema, check_clustering_compliance, 'tables_without_clustering_or_optout')
