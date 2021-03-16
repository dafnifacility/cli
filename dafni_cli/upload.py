import click
from click import Context

from dafni_cli.login import check_for_jwt_file


@click.group()
@click.pass_context
def upload(ctx: Context):
    """Uploads entities (models, datasets, workflows, groups) to DAFNI.

    Args:
        ctx (Context): Context containing JWT of the user.
    """
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


@upload.command()
@click.argument("metadata", nargs=1, required=True, type=click.Path(exists=True))
@click.argument("image", nargs=1, required=True, type=click.Path(exists=True))
@click.pass_context
def model(ctx: Context, )
    """Uploads model to DAFNI from metadata and image files.
    
    Args:
        ctx (Context): contains JWT for authentication
        
    """
