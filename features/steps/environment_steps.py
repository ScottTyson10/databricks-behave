from behave import given
from databricks.sdk import WorkspaceClient

from dotenv import load_dotenv
load_dotenv()

@given("I connect to the Databricks workspace")
def step_connect_to_databricks(context):
    context.dbx = WorkspaceClient()


@given("a threshold of {threshold:d}% column documentation")
def step_set_column_documentation_threshold(context, threshold):
    """Set the column documentation threshold for validation."""
    context.column_doc_threshold = threshold
