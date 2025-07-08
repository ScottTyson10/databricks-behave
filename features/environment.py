import os

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from setup.create_test_clustering_tables import set_dbx_tables

load_dotenv()

CATALOG = "workspace"
SCHEMA = "test_clustering"

# Skip test setup and teardown for development purposes
SKIP_TEST_SETUP = False
SKIP_TEST_TEARDOWN = False

# NOTE: In production repositories we wont need to create these as we'll use the existing tables
#       For testing we need to create some dbx objects
def before_all(context):
    # Set up Databricks client
    context.dbx = WorkspaceClient()
    context.catalog_schema = f"{CATALOG}.{SCHEMA}"
    
    # Load configuration from environment or defaults
    context.config.userdata.setdefault('COLUMN_DOC_THRESHOLD', '80')
    context.config.userdata.setdefault('VACUUM_DAYS_THRESHOLD', '30')
    context.config.userdata.setdefault('ORPHAN_DAYS_THRESHOLD', '90')
    context.config.userdata.setdefault('MIN_TIMEOUT_SECONDS', '300')
    context.config.userdata.setdefault('MAX_TIMEOUT_SECONDS', '86400')
    
    if SKIP_TEST_SETUP:
        print("Skipping test setup")
        return
    set_dbx_tables(catalog=CATALOG, schema=SCHEMA)


def after_all(context):
    if SKIP_TEST_TEARDOWN:
        print("Skipping test teardown")
        return
    dbx = WorkspaceClient()
    dbx.statement_execution.execute_statement(
        statement=f"DROP SCHEMA IF EXISTS {CATALOG}.{SCHEMA} CASCADE",
        catalog=CATALOG,
        schema=SCHEMA,
        warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID")
    )
