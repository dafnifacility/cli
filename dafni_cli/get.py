import click
from click import Context
from typing import List, Optional

from dafni_cli.api.datasets_api import get_all_datasets, get_latest_dataset_metadata
from dafni_cli.api.models_api import get_models_dicts
from dafni_cli.datasets import dataset, dataset_filtering
from dafni_cli.login import check_for_jwt_file
from dafni_cli.api.models_api import get_models_dicts
from dafni_cli.model import Model
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
    type=bool,
)
@click.option(
    "--creation-date",
    default=None,
    help="Filter for models created since given date. Format: DD/MM/YYYY",
    type=str,
)
@click.option(
    "--publication-date",
    default=None,
    help="Filter for models published since given date. Format: DD/MM/YYYY",
    type=str,
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


@get.command()
@click.argument("version-id", nargs=-1, required=True, type=str)
@click.pass_context
def model(ctx: Context, version_id: List[str]):
    """Displays the metadata for one or more model versions

    Args:
         ctx (context): contains JWT for authentication
         version_id (list[str]): List of version ids of the models to be displayed
    """
    for vid in version_id:
        model = Model()
        model.get_details_from_id(ctx.obj["jwt"], vid)
        model.get_metadata(ctx.obj["jwt"])
        model.output_model_metadata()


@get.command(help="List and filter datasets")
@click.option(
    "--search",
    default=None,
    help='Search terms for elastic search. Format: "search terms"',
    type=str,
)
@click.option(
    "--start-date",
    default=None,
    help="Filter for datasets with a start date since given date. Format: DD/MM/YYYY",
    type=str,
)
@click.option(
    "--end-date",
    default=None,
    help="Filter for datasets with a end date up to given date. Format: DD/MM/YYYY",
    type=str,
)
@click.pass_context
def datasets(
    ctx: Context,
    search: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
):
    """Displays a list of all available datasets

    Args:
        ctx (context): contains JWT for authentication
    """
    filters = dataset_filtering.process_datasets_filters(search, start_date, end_date)
    datasets_response = get_all_datasets(ctx.obj["jwt"], filters)
    datasets = process_response_to_class_list(
        datasets_response["metadata"], dataset.Dataset
    )
    for dataset_model in datasets:
        dataset_model.output_dataset_details()


@get.command()
@click.option("--id", required=True, type=str, help="Dataset ID")
@click.option("--version-id", required=True, type=str, help="Dataset Version ID")
@click.pass_context
def dataset(ctx: Context, id: str, version_id: str):

    metadata = get_latest_dataset_metadata(ctx.obj["jwt"], id, version_id)


@get.command()
def workflows():
    pass


@get.command()
def groups():
    pass
