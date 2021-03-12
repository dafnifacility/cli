import click
from click import Context

from dafni_cli.login import check_for_jwt_file
from dafni_cli.API_requests import get_models_dicts
from dafni_cli.model.model import Model
from dafni_cli.utils import process_response_to_class_list


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
    "--long/--short",
    default=False,
    help="Also displays the full description of each model.",
)
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
def models(ctx: Context, long: bool, creation_date: str, publication_date: str):
    """Displays list of model names with other options allowing
        more details to be listed as well.

    Args:
        ctx (context): contains JWT for authentication
        long (bool): whether to print the description of each model as well
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
    """
    model_dict_list = get_models_dicts(ctx.obj["jwt"])
    model_list = process_response_to_class_list(model_dict_list, Model)
    for model in model_list:
        date_filter = True
        if creation_date:
            date_filter = model.filter_by_date("creation", creation_date)
        if publication_date:
            date_filter = model.filter_by_date("publication", publication_date)
        if date_filter:
            model.output_model_details(long)


@get.group(invoke_without_command=True)
@click.argument("version-id", nargs=-1)
@click.pass_context
def model(ctx: Context, version_id: str):
    """Displays the metadata for one or more model versions

    Args:
        ctx (Context): contains JWT for authentication
        version_id (list[str]): List of version IDs of the models to be displayed
    """
    for vid in version_id:
        model = Model()
        model.get_details_from_id(ctx.obj["jwt"], vid)
        model.get_metadata(ctx.obj["jwt"])
        model.output_model_metadata()


@model.command()
@click.argument("version-id", nargs=1)
@click.pass_context
def version_history(ctx: Context, version_id: str):
    """Displays the version history for a model

    Args:
        ctx (Context): contains JWT for authentication
        version_id (str): Version ID of the model whose version history is to be displayed
    """



@get.command()
def datasets():
    pass


@get.command()
def workflows():
    pass


@get.command()
def groups():
    pass
