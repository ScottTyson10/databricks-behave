import os
from typing import Any, Callable
from databricks.sdk import WorkspaceClient
import json


def _get_warehouse_id() -> str | None:
    return os.getenv("DATABRICKS_WAREHOUSE_ID")


def _execute_query(dbx: WorkspaceClient, query: str, catalog: str = None, schema: str = None) -> Any:
    return dbx.statement_execution.get_statement(
        dbx.statement_execution.execute_statement(
            statement=query,
            warehouse_id=_get_warehouse_id(),
            catalog=catalog,
            schema=schema,
        ).statement_id
    )


def list_schemas_in_catalog(dbx: WorkspaceClient, catalog: str) -> list[str]:
    result = _execute_query(dbx, f"SHOW SCHEMAS IN {catalog}", catalog)
    return [row[0] for row in getattr(result.result, 'data_array', []) if row and len(row) > 0]


def list_tables_in_schema(dbx: WorkspaceClient, catalog: str, schema: str) -> list[str]:
    result = _execute_query(dbx, f"SHOW TABLES IN {catalog}.{schema}", catalog, schema)
    return [row[1] for row in getattr(result.result, 'data_array', []) if row and len(row) > 1]


def get_table_detail(dbx: WorkspaceClient, catalog: str, schema: str, table: str) -> dict[str, Any]:
    result = _execute_query(dbx, f"DESCRIBE DETAIL {catalog}.{schema}.{table}", catalog, schema)
    if result.result and result.result.data_array:
        columns = [col.name for col in result.manifest.schema.columns]
        values = result.result.data_array[0]
        return dict(zip(columns, values))
    return {}


def get_table_extended_properties(dbx, catalog, schema, table):
    result = _execute_query(dbx, f"DESCRIBE TABLE EXTENDED {catalog}.{schema}.{table} AS JSON", catalog, schema)
    if result.result and result.result.data_array:
        return json.loads(result.result.data_array[0][0])
    return {}


def for_each_table(
    context: Any,
    catalog_schema: str,
    check_fn: Callable[[dict[str, Any], str, str, str], bool],
    fail_attr: str
) -> None:
    parts = catalog_schema.split(".")
    catalog = parts[0]
    schemas = [parts[1]] if len(parts) > 1 else list_schemas_in_catalog(context.dbx, catalog)
    failed = []
    for schema in schemas:
        for table in list_tables_in_schema(context.dbx, catalog, schema):
            detail = get_table_detail(context.dbx, catalog, schema, table)
            if not check_fn(detail, catalog, schema, table):
                failed.append(f"{catalog}.{schema}.{table}")
    setattr(context, fail_attr, failed)
