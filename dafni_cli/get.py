import click
from click import Context

from dafni_cli.login import check_for_jwt_file
from dafni_cli.API_requests import get_models_dicts
from dafni_cli.model import create_model_list


@click.group()
@click.pass_context
def get(ctx: Context):
    """Lists entities available to the user from
    models, datasets, workflows, groups, depending on command."""
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


@get.command(help="List and filter models")
@click.option(
    "--creation-date",
    default=None,
    help="Filter for models created since given date. Format: DD/MM/YYYY",
)
@click.option(
    "--publication-date",
    default=None,
    help="Filter for models published since given date. Format: DD/MM/YYYY",
)
@click.pass_context
def models(ctx: Context, creation_date: str, publication_date: str):
    """Displays list of model names with other options allowing
        more details to be listed as well.

    Args:
        ctx (context): contains JWT for authentication
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
    """
    model_dict_list = get_models_dicts(ctx.obj["jwt"])
    model_list = create_model_list(model_dict_list)
    for model in model_list:
        date_filter = True
        if creation_date:
            date_filter = model.filter_by_date("creation", creation_date)
        if publication_date:
            date_filter = model.filter_by_date("publication", publication_date)
        if date_filter:
            model.output_model_details()


@get.command()
@click.pass_context
def metadata(ctx):
    pass


@get.command()
def datasets():
    pass


@get.command()
def workflows():
    pass


@get.command()
def groups():
    pass
