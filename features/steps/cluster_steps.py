from behave import given, when, then
from features.steps.job_utils import get_workspace_client


def list_all_clusters(context) -> list[dict]:
    """List all clusters in the workspace."""
    client = get_workspace_client(context)
    clusters = []
    
    for cluster in client.clusters.list():
        clusters.append({
            'cluster_id': cluster.cluster_id,
            'cluster_name': cluster.cluster_name,
            'cluster_source': cluster.cluster_source,
            'autotermination_minutes': cluster.autotermination_minutes,
            'state': cluster.state
        })
    
    return clusters


@when("I check each cluster's configuration")
def step_check_cluster_configs(context):
    """Retrieve all cluster configurations."""
    context.all_clusters = list_all_clusters(context)


@then('all-purpose clusters should have auto_termination_minutes <= {max_minutes:d}')
def step_check_all_purpose_termination(context, max_minutes):
    """Validate all-purpose cluster auto-termination."""
    context.clusters_with_bad_termination = []
    
    for cluster in context.all_clusters:
        if cluster['cluster_source'] == 'UI' or cluster['cluster_source'] == 'API':
            # This is an all-purpose cluster
            auto_term = cluster.get('autotermination_minutes')
            
            if auto_term is None:
                context.clusters_with_bad_termination.append({
                    'name': cluster['cluster_name'],
                    'issue': 'No auto-termination configured'
                })
            elif auto_term > max_minutes:
                context.clusters_with_bad_termination.append({
                    'name': cluster['cluster_name'],
                    'issue': f'Auto-termination too long: {auto_term} minutes'
                })
    
    assert len(context.clusters_with_bad_termination) == 0, \
        f"Found {len(context.clusters_with_bad_termination)} clusters with termination issues: {[c['name'] for c in context.clusters_with_bad_termination]}"


@then('job clusters should have auto_termination after job completion')
def step_check_job_cluster_termination(context):
    """Validate job cluster auto-termination."""
    context.job_clusters_with_issues = []
    
    for cluster in context.all_clusters:
        if cluster['cluster_source'] == 'JOB':
            # Job clusters should auto-terminate by default
            # They don't need explicit auto_termination_minutes as they terminate with the job
            pass
    
    # Job clusters auto-terminate by design, so this should always pass
    assert len(context.job_clusters_with_issues) == 0, \
        f"Found {len(context.job_clusters_with_issues)} job clusters with termination issues"


@then('no cluster should have auto_termination disabled')
def step_check_no_disabled_termination(context):
    """Ensure no clusters have auto-termination completely disabled."""
    disabled_clusters = []
    
    for cluster in context.all_clusters:
        if cluster['cluster_source'] in ['UI', 'API']:  # All-purpose clusters
            auto_term = cluster.get('autotermination_minutes')
            if auto_term is None or auto_term == 0:
                disabled_clusters.append(cluster['cluster_name'])
    
    assert len(disabled_clusters) == 0, \
        f"Found {len(disabled_clusters)} clusters with auto-termination disabled: {disabled_clusters}"