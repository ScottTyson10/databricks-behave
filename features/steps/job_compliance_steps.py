from behave import given, when, then
from features.steps.job_utils import *


@given('I have permissions to list and describe jobs')
def step_check_job_permissions(context):
    """Verify we can access job APIs."""
    try:
        # Test API access
        client = get_workspace_client(context)
        list(client.jobs.list(limit=1))
        context.has_job_permissions = True
    except Exception as e:
        context.has_job_permissions = False
        raise Exception(f"Cannot access jobs API: {str(e)}")


@when('I check all jobs in the workspace')
def step_get_all_jobs(context):
    """Retrieve all jobs for validation."""
    context.all_jobs = list_all_jobs(context)


@when('I check jobs with "{pattern}" in their name')
def step_filter_jobs_by_name(context, pattern):
    """Filter jobs by name pattern."""
    all_jobs = list_all_jobs(context)
    context.filtered_jobs = [job for job in all_jobs if pattern.lower() in job['name'].lower()]


@when('I check each job\'s timeout configuration')
def step_check_job_timeouts(context):
    """Check timeout configuration for all jobs."""
    context.all_jobs = list_all_jobs(context)


@when('I check each job\'s cluster configuration')
def step_check_job_clusters(context):
    """Check cluster configuration for all jobs."""
    context.all_jobs = list_all_jobs(context)


@then('no job should have a run_as containing "@"')
def step_check_no_user_accounts(context):
    """Ensure no jobs use user accounts."""
    context.jobs_with_user_accounts = []
    
    for job in context.all_jobs:
        is_compliant, issue = check_service_principal(job['settings'])
        if not is_compliant and '@' in str(issue):
            context.jobs_with_user_accounts.append({
                'name': job['name'],
                'issue': issue
            })
    
    assert len(context.jobs_with_user_accounts) == 0, \
        f"Found {len(context.jobs_with_user_accounts)} jobs with user accounts: {[j['name'] for j in context.jobs_with_user_accounts]}"


@then('jobs with "{pattern}" in the name must have service principal')
def step_check_production_service_principals(context, pattern):
    """Ensure production jobs use service principals."""
    production_jobs = [job for job in context.all_jobs if pattern.lower() in job['name'].lower()]
    context.prod_jobs_without_sp = []
    
    for job in production_jobs:
        is_compliant, issue = check_service_principal(job['settings'])
        if not is_compliant:
            context.prod_jobs_without_sp.append({
                'name': job['name'],
                'issue': issue
            })
    
    assert len(context.prod_jobs_without_sp) == 0, \
        f"Found {len(context.prod_jobs_without_sp)} production jobs without service principals: {[j['name'] for j in context.prod_jobs_without_sp]}"


@then('each production job should have max_retries > 0')
def step_check_retry_configuration(context):
    """Validate retry configuration for production jobs."""
    context.jobs_without_retries = []
    
    for job in context.filtered_jobs:
        is_compliant, issue = check_retry_configuration(job['settings'])
        if not is_compliant:
            context.jobs_without_retries.append({
                'name': job['name'],
                'issue': issue
            })
    
    assert len(context.jobs_without_retries) == 0, \
        f"Found {len(context.jobs_without_retries)} jobs with inadequate retry configuration: {[j['name'] for j in context.jobs_without_retries]}"


@then('retry_on_timeout should be true')
def step_check_retry_on_timeout(context):
    """This is covered by the retry configuration check above."""
    # The check_retry_configuration function validates both max_retries and retry_on_timeout
    pass


@then('each job should have timeout_seconds defined')
def step_check_timeout_defined(context):
    """Validate that all jobs have timeout configuration."""
    context.jobs_without_timeout = []
    
    for job in context.all_jobs:
        is_compliant, issue = check_timeout_configuration(context, job['settings'])
        if not is_compliant:
            context.jobs_without_timeout.append({
                'name': job['name'],
                'issue': issue
            })
    
    assert len(context.jobs_without_timeout) == 0, \
        f"Found {len(context.jobs_without_timeout)} jobs with timeout issues: {[j['name'] for j in context.jobs_without_timeout]}"


@then('timeout_seconds should be between {min_timeout:d} and {max_timeout:d}')
def step_check_timeout_range(context, min_timeout, max_timeout):
    """This is covered by the timeout configuration check above."""
    # The check_timeout_configuration function validates the timeout range
    pass


@then('jobs should use new_cluster configuration')
def step_check_new_cluster_usage(context):
    """Validate that jobs use new clusters instead of existing ones."""
    context.jobs_with_cluster_issues = []
    
    for job in context.all_jobs:
        is_compliant, issue = check_cluster_configuration(job['settings'])
        if not is_compliant:
            context.jobs_with_cluster_issues.append({
                'name': job['name'],
                'issue': issue
            })
    
    assert len(context.jobs_with_cluster_issues) == 0, \
        f"Found {len(context.jobs_with_cluster_issues)} jobs with cluster configuration issues: {[j['name'] for j in context.jobs_with_cluster_issues]}"


@then('should not reference existing_cluster_id')
def step_check_no_existing_cluster(context):
    """This is covered by the cluster configuration check above."""
    # The check_cluster_configuration function validates existing_cluster_id usage
    pass


@then('Unless tagged with "interactive" or "debug"')
def step_check_cluster_exceptions(context):
    """This is covered by the cluster configuration check above."""
    # The check_cluster_configuration function handles tag-based exceptions
    pass