from behave import given, when, then
from features.steps.databricks_utils import for_each_table, get_column_metadata


@then('each table should have a non-empty "comment" field')
def step_check_table_comments(context):
    """Validate that all tables have meaningful comments."""
    def check_table_comment(detail, catalog, schema, table):
        comment = detail.get('comment', '').strip() if detail.get('comment') else ''
        if not comment:
            return False
        
        generic_terms = ['table', 'data', 'temp', 'test', 'tbd', 'todo']
        if comment.lower() in generic_terms:
            return False
        
        return True
    
    for_each_table(context, context.catalog_schema, check_table_comment, 'tables_without_documentation')


@then('the comment should not be generic like "table" or "data"')
def step_check_non_generic_comments(context):
    """Validate that table comments are not generic."""
    # This is covered by the previous step, but can be used separately
    assert not hasattr(context, 'tables_without_documentation') or not context.tables_without_documentation, \
        f"Tables with missing or generic documentation: {getattr(context, 'tables_without_documentation', [])}"


@then('at least {threshold:d}% of columns per table should have descriptions')
def step_check_column_documentation(context, threshold):
    """Validate column documentation coverage meets threshold."""
    def check_column_documentation(detail, catalog, schema, table):
        columns = get_column_metadata(context, f"{catalog}.{schema}.{table}")
        total_columns = len(columns)
        documented_columns = sum(1 for col in columns if col.get('comment'))
        
        if total_columns == 0:
            return True
            
        percentage = (documented_columns / total_columns) * 100
        return percentage >= threshold
    
    for_each_table(context, context.catalog_schema, check_column_documentation, 'tables_with_poor_column_docs')


@then('critical columns (containing "{patterns}") must have descriptions')
def step_check_critical_columns(context, patterns):
    """Ensure critical columns are documented."""
    critical_patterns = [p.strip() for p in patterns.split(',')]
    
    def check_critical_column_docs(detail, catalog, schema, table):
        columns = get_column_metadata(context, f"{catalog}.{schema}.{table}")
        
        for col in columns:
            col_name = col['name'].lower()
            is_critical = any(pattern in col_name for pattern in critical_patterns)
            if is_critical and not col.get('comment'):
                return False
        
        return True
    
    for_each_table(context, context.catalog_schema, check_critical_column_docs, 'tables_with_undocumented_critical_columns')