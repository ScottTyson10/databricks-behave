from databricks.sdk import WorkspaceClient
from typing import Optional, Tuple


def get_workspace_client(context) -> WorkspaceClient:
    """Get or create workspace client."""
    if not hasattr(context, 'workspace_client'):
        context.workspace_client = WorkspaceClient()
    return context.workspace_client


def list_all_jobs(context) -> list[dict]:
    """List all jobs in the workspace."""
    client = get_workspace_client(context)
    jobs = []
    for job in client.jobs.list():
        jobs.append({
            'job_id': job.job_id,
            'name': job.settings.name,
            'settings': job.settings
        })
    return jobs


def get_job_details(context, job_id: int) -> dict:
    """Get detailed information about a specific job."""
    client = get_workspace_client(context)
    return client.jobs.get(job_id=job_id)


def is_production_job(job_name: str) -> bool:
    """Determine if a job is a production job based on naming."""
    prod_indicators = ['prod', 'production', 'prd']
    return any(indicator in job_name.lower() for indicator in prod_indicators)


def check_service_principal(job_settings) -> Tuple[bool, Optional[str]]:
    """Check if job uses service principal."""
    run_as = getattr(job_settings, 'run_as', None)
    if run_as and hasattr(run_as, 'user_name') and run_as.user_name and '@' in run_as.user_name:
        return False, f"Uses user account: {run_as.user_name}"
    if run_as and hasattr(run_as, 'service_principal_name') and run_as.service_principal_name:
        return True, None
    return False, "No run_as configuration"


def check_retry_configuration(job_settings) -> Tuple[bool, Optional[str]]:
    """Validate job retry settings."""
    issues = []
    
    max_retries = getattr(job_settings, 'max_retries', 0)
    if max_retries == 0:
        issues.append("max_retries is 0")
    
    retry_on_timeout = getattr(job_settings, 'retry_on_timeout', False)
    if not retry_on_timeout:
        issues.append("retry_on_timeout is False")
    
    if issues:
        return False, "; ".join(issues)
    return True, None


def check_timeout_configuration(context, job_settings) -> Tuple[bool, Optional[str]]:
    """Validate job timeout settings."""
    timeout_seconds = getattr(job_settings, 'timeout_seconds', None)
    
    if timeout_seconds is None:
        return False, "No timeout configured"
    
    min_timeout = int(context.config.userdata.get('MIN_TIMEOUT_SECONDS', 300))
    max_timeout = int(context.config.userdata.get('MAX_TIMEOUT_SECONDS', 86400))
    
    if timeout_seconds < min_timeout:
        return False, f"Timeout too short: {timeout_seconds}s < {min_timeout}s"
    if timeout_seconds > max_timeout:
        return False, f"Timeout too long: {timeout_seconds}s > {max_timeout}s"
    
    return True, None


def check_cluster_configuration(job_settings) -> Tuple[bool, Optional[str]]:
    """Validate job cluster configuration."""
    # Check if job has tags that allow all-purpose clusters
    tags = getattr(job_settings, 'tags', {})
    if tags and ('interactive' in tags or 'debug' in tags):
        return True, None
    
    # Check tasks for cluster configuration
    tasks = getattr(job_settings, 'tasks', [])
    for task in tasks:
        if hasattr(task, 'existing_cluster_id') and task.existing_cluster_id:
            task_key = getattr(task, 'task_key', 'unknown')
            return False, f"Task '{task_key}' uses existing cluster"
    
    return True, None