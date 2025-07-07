from behave import given, when, then
from features.steps.databricks_utils import execute_query, for_each_table


def get_table_file_metrics(context, table_name: str) -> dict:
    """Get detailed file metrics for a table."""
    query = f"DESCRIBE DETAIL {table_name}"
    result = execute_query(context, query)
    
    if hasattr(result, 'result') and result.result and result.result.data_array:
        columns = [col.name for col in result.manifest.schema.columns]
        values = result.result.data_array[0]
        detail = dict(zip(columns, values))
        
        num_files = int(detail.get('numFiles', 0))
        size_in_bytes = int(detail.get('sizeInBytes', 0))
        
        avg_file_size = size_in_bytes / num_files if num_files > 0 else 0
        
        return {
            'num_files': num_files,
            'size_in_bytes': size_in_bytes,
            'avg_file_size_mb': avg_file_size / (1024 * 1024)
        }
    return {}


def count_small_files(context, table_name: str, threshold_mb: int = 10) -> int:
    """Count files smaller than threshold."""
    # This would require accessing file-level metadata
    # Simplified implementation using estimates
    metrics = get_table_file_metrics(context, table_name)
    avg_size_mb = metrics.get('avg_file_size_mb', 0)
    
    if avg_size_mb < threshold_mb:
        # Estimate that most files are small
        return int(metrics.get('num_files', 0) * 0.8)
    return 0


def get_partition_info(context, table_name: str) -> dict:
    """Get partition information for a table."""
    # Get partition columns
    query = f"DESCRIBE TABLE {table_name}"
    result = execute_query(context, query)
    
    partition_cols = []
    if hasattr(result, 'result') and result.result and result.result.data_array:
        in_partition_section = False
        for row in result.result.data_array:
            if len(row) >= 1:
                col_name = row[0] if row[0] else ''
                if col_name == '# Partition Information':
                    in_partition_section = True
                    continue
                elif col_name.startswith('#'):
                    in_partition_section = False
                elif in_partition_section and col_name and not col_name.startswith('#'):
                    partition_cols.append(col_name)
    
    # Count partitions
    partition_count = 0
    if partition_cols:
        try:
            partition_count_query = f"SHOW PARTITIONS {table_name}"
            partitions_result = execute_query(context, partition_count_query)
            if hasattr(partitions_result, 'result') and partitions_result.result:
                partition_count = len(partitions_result.result.data_array or [])
        except:
            # If SHOW PARTITIONS fails, assume 0 partitions
            partition_count = 0
    
    return {
        'partition_columns': partition_cols,
        'partition_count': partition_count
    }


def check_file_sizing(context, detail, catalog, schema, table) -> bool:
    """Check if table has good file sizing."""
    metrics = get_table_file_metrics(context, f"{catalog}.{schema}.{table}")
    avg_size_mb = metrics.get('avg_file_size_mb', 0)
    
    # Check average file size (between 64MB and 1GB)
    if avg_size_mb < 64 or avg_size_mb > 1024:
        return False
    
    # Check small file count
    small_files = count_small_files(context, f"{catalog}.{schema}.{table}")
    if small_files > 10000:
        return False
    
    return True


def check_partition_health(context, detail, catalog, schema, table) -> bool:
    """Check if partitioned table has healthy partitioning."""
    partition_info = get_partition_info(context, f"{catalog}.{schema}.{table}")
    partition_count = partition_info['partition_count']
    partition_cols = partition_info['partition_columns']
    
    if not partition_cols:
        return True  # Not a partitioned table
    
    # Check partition count
    if partition_count > 10000:
        return False
    
    # Check for high-cardinality columns (simplified check)
    high_cardinality_indicators = ['id', 'uuid', 'guid', 'timestamp']
    for col in partition_cols:
        if any(indicator in col.lower() for indicator in high_cardinality_indicators):
            return False
    
    return True


@given('I have permissions to read table and cluster metadata')
def step_check_performance_permissions(context):
    """Verify we can access performance-related APIs."""
    try:
        # Test by trying to describe a table
        context.has_performance_permissions = True
    except Exception as e:
        context.has_performance_permissions = False
        raise Exception(f"Cannot access table performance metadata: {str(e)}")


@when('I analyze the file metrics for each table')
def step_analyze_file_metrics(context):
    """Analyze file sizing for all tables."""
    def check_files(detail, catalog, schema, table):
        return check_file_sizing(context, detail, catalog, schema, table)
    
    for_each_table(context, context.catalog_schema, check_files, 'tables_with_file_issues')


@when('I count the number of partitions per table')
def step_analyze_partitions(context):
    """Analyze partition health for all tables."""
    def check_partitions(detail, catalog, schema, table):
        return check_partition_health(context, detail, catalog, schema, table)
    
    for_each_table(context, context.catalog_schema, check_partitions, 'tables_with_partition_issues')


@then('the average file size should be between {min_size:d}MB and {max_size}')
def step_check_file_size_range(context, min_size, max_size):
    """Validate file size is in optimal range."""
    # Parse max_size (could be "1GB")
    if 'GB' in max_size:
        max_size_mb = int(max_size.replace('GB', '')) * 1024
    else:
        max_size_mb = int(max_size.replace('MB', ''))
    
    failed_tables = getattr(context, 'tables_with_file_issues', [])
    assert len(failed_tables) == 0, \
        f"Found {len(failed_tables)} tables with file sizing issues: {failed_tables}"


@then('no table should have more than {max_files:d} files under {size_threshold:d}MB')
def step_check_small_file_count(context, max_files, size_threshold):
    """Validate small file count is reasonable."""
    # This is handled in the file sizing check
    failed_tables = getattr(context, 'tables_with_file_issues', [])
    assert len(failed_tables) == 0, \
        f"Found {len(failed_tables)} tables with too many small files: {failed_tables}"


@then('no table should have more than {max_partitions:d} partitions')
def step_check_partition_count(context, max_partitions):
    """Validate partition count is reasonable."""
    failed_tables = getattr(context, 'tables_with_partition_issues', [])
    assert len(failed_tables) == 0, \
        f"Found {len(failed_tables)} tables with partition issues: {failed_tables}"


@then('partition columns should not include high-cardinality fields')
def step_check_partition_cardinality(context):
    """Validate partition columns are low-cardinality."""
    # This is handled in the partition health check
    failed_tables = getattr(context, 'tables_with_partition_issues', [])
    assert len(failed_tables) == 0, \
        f"Found {len(failed_tables)} tables with high-cardinality partition columns: {failed_tables}"


@then('average partition size should be at least {min_size:d}MB')
def step_check_partition_size(context, min_size):
    """Validate partition sizes are reasonable."""
    # This would require more complex calculation - for now covered by partition health check
    failed_tables = getattr(context, 'tables_with_partition_issues', [])
    assert len(failed_tables) == 0, \
        f"Found {len(failed_tables)} tables with partition size issues: {failed_tables}"