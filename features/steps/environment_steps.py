from behave import given
from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv
load_dotenv()

@given("I connect to the Databricks workspace")
def step_connect_to_databricks(context):
    context.dbx = WorkspaceClient()
