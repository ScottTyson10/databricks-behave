import os
from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv
load_dotenv()

# Configuration
TABLE_CLUSTERED = "clustered_table"
TABLE_AUTO_CLUSTERED = "auto_clustered_table"
TABLE_NO_CLUSTERING = "no_clustering_table"
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")


def create_schema(dbx: WorkspaceClient, catalog: str, schema: str):
    print(f"Creating schema {catalog}.{schema} if not exists...")
    dbx.statement_execution.execute_statement(
        statement=f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}",
        warehouse_id=WAREHOUSE_ID,
        catalog=catalog,
        schema=schema,
    )


def drop_table_if_exists(dbx: WorkspaceClient, catalog: str, schema: str, table: str):
    print(f"Dropping table {catalog}.{schema}.{table} if exists...")
    dbx.statement_execution.execute_statement(
        statement=f"DROP TABLE IF EXISTS {catalog}.{schema}.{table}",
        warehouse_id=WAREHOUSE_ID,
        catalog=catalog,
        schema=schema,
    )


def create_clustered_table(dbx: WorkspaceClient, catalog: str, schema: str, table: str):
    print(f"Creating clustered table {catalog}.{schema}.{table}...")
    dbx.statement_execution.execute_statement(
        statement=(
            f"CREATE TABLE {catalog}.{schema}.{table} (id INT, name STRING, value DOUBLE) "
            "CLUSTER BY (id, name)"
        ),
        warehouse_id=WAREHOUSE_ID,
        catalog=catalog,
        schema=schema,
    )


def create_auto_clustered_table(dbx: WorkspaceClient, catalog: str, schema: str, table: str):
    print(f"Creating auto-clustered table {catalog}.{schema}.{table}...")
    dbx.statement_execution.execute_statement(
        statement=(
            f"CREATE TABLE {catalog}.{schema}.{table} (id INT, name STRING, value DOUBLE) "
            "CLUSTER BY AUTO"
        ),
        warehouse_id=WAREHOUSE_ID,
        catalog=catalog,
        schema=schema,
    )


def create_no_clustering_table(dbx: WorkspaceClient, catalog: str, schema: str, table: str):
    print(f"Creating table with no clustering {catalog}.{schema}.{table}...")
    dbx.statement_execution.execute_statement(
        statement=(
            f"CREATE TABLE {catalog}.{schema}.{table} (id INT, name STRING, value DOUBLE) "
            f"USING DELTA "
            f"TBLPROPERTIES ('cluster_exclusion' = True)"
        ),
        warehouse_id=WAREHOUSE_ID,
        catalog=catalog,
        schema=schema,
    )


def set_dbx_tables(catalog: str, schema: str):
    dbx = WorkspaceClient()
    create_schema(dbx, catalog, schema)
    drop_table_if_exists(dbx, catalog, schema, TABLE_CLUSTERED)
    drop_table_if_exists(dbx, catalog, schema, TABLE_AUTO_CLUSTERED)
    drop_table_if_exists(dbx, catalog, schema, TABLE_NO_CLUSTERING)
    create_clustered_table(dbx, catalog, schema, TABLE_CLUSTERED)
    create_auto_clustered_table(dbx, catalog, schema, TABLE_AUTO_CLUSTERED)
    create_no_clustering_table(dbx, catalog, schema, TABLE_NO_CLUSTERING)
    print("Schema and test tables created.")
