###############################################################################
# Execute command
###############################################################################

import click

from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.api.workflows_api import get_single_workflow_dict
from dafni_cli.api.workflows_api import execute_workflow


###############################################################################
# Execute base command
###############################################################################
@click.group(help = "Execute a DAFNI workflow")
@click.pass_context
def execute(ctx: click.Context):
    """
    Execute a DAFNI command
    """
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


###############################################################################
# Execute WORKFLOW
###############################################################################
@execute.command(help = "Execute a workflow version")
@click.argument("workflow-id", nargs=1, required=True, type=str)
@click.argument("paramset-id", nargs=1, required=True, type=str)
@click.pass_context
def workflow(
    ctx: click.Context,
    workflow_id: str,
    paramset_id: str
):
    """
    Execute a DAFNI workflow version
    """
    dict = get_single_workflow_dict(ctx.obj["jwt"], workflow_id)
    print(dict)
    execute_workflow(ctx.obj["jwt"], workflow_id, paramset_id)