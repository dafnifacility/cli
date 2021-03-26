import click
from click import Context
from typing import List, Optional

from dafni_cli.api.datasets_api import get_all_datasets, get_latest_dataset_metadata
from dafni_cli.api.models_api import get_models_dicts
from dafni_cli.datasets import (
    dataset_filtering,
    dataset_metadata,
    dataset_version_history,
)
from dafni_cli.datasets.dataset import Dataset
from dafni_cli.commands.login import check_for_jwt_file
from dafni_cli.model.model import Model
from dafni_cli.model.version_history import ModelVersionHistory
from dafni_cli.api.models_api import get_models_dicts
from dafni_cli.utils import (
    process_response_to_class_list,
    print_json
)


@click.group(help="Lists entities available to the user")
@click.pass_context
def get(ctx: Context):
    """Lists entities available to the user from
    models, datasets, workflows, groups, depending on command.
    \f
    Args:
        ctx (Context): Context containing JWT of the user.
    """
    ctx.ensure_object(dict)
    jwt_dict, _ = check_for_jwt_file()
    ctx.obj["jwt"] = jwt_dict["jwt"]


@get.command(help="List and filter models")
@click.option(
    "--long/--short",
    "-l/-s",
    default=False,
    help="Also displays the description of each model. Default: -s",
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
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool
)
@click.pass_context
def models(ctx: Context, long: bool, creation_date: str, publication_date: str, json: bool):
    """Displays list of model details with other options allowing
        more details to be listed, filters, and for the json to be displayed.
    \f
    Args:
        ctx (context): contains JWT for authentication
        long (bool): whether to print the description of each model as well
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
        json (bool): whether to print the raw json returned by the DAFNI API
    """
    model_dict_list = get_models_dicts(ctx.obj["jwt"])
    model_list = process_response_to_class_list(model_dict_list, Model)
    filtered_model_dict_list = []
    for model in model_list:
        date_filter = True
        if creation_date:
            date_filter = model.filter_by_date("creation", creation_date)
        if publication_date:
            date_filter = model.filter_by_date("publication", publication_date)
        if date_filter:
            if json:
                filtered_model_dict_list.append(model.dictionary)
            else:
                model.output_details(long)
    if json:
        print_json(filtered_model_dict_list)


@get.command(help="Display metadata or version history of a particular model or models")
@click.argument("version-id", nargs=-1, required=True)
@click.option(
    "--version-history/--metadata",
    "-v/-m",
    default=False,
    help="Whether to display the version history of a model instead of the metadata. Default -m",
)
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool
)
@click.pass_context
def model(ctx: Context, version_id: List[str], version_history: bool, json: bool):
    """Displays the metadata for one or more model versions
    \f
    Args:
        ctx (Context): contains JWT for authentication
        version_id (list[str]): List of version IDs of the models to be displayed
        version_history (bool): Whether to display version_history instead of metadata
        json (bool): Whether to output raw json from API or pretty print metadata/version history. Defaults to False.
    """
    for vid in version_id:
        model = Model(vid)
        model.get_details_from_id(ctx.obj["jwt"], vid)
        if version_history:
            history = ModelVersionHistory(ctx.obj["jwt"], model)
            history.output_version_history(json)
        else:
            model.get_metadata(ctx.obj["jwt"])
            model.output_metadata(json)


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
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool
)
@click.pass_context
def datasets(
    ctx: Context,
    search: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    json: Optional[bool]
):
    """Displays a list of all available datasets
    \f
    Args:
        ctx (context): contains JWT for authentication
        search (Optional[str]): Search terms for elastic search. Format: "search terms"
        start_date (Optional[str]): Filter for datasets with a start date since given date. Format: DD/MM/YYYY
        end_date (Optional[str]): Filter for datasets with a end date up to given date. Format: DD/MM/YYYY
        json (Optional[bool]): Whether to output raw json from API or pretty print information. Defaults to False.
    """
    filters = dataset_filtering.process_datasets_filters(search, start_date, end_date)
    datasets_response = get_all_datasets(ctx.obj["jwt"], filters)
    if json:
        print_json(datasets_response)
    else:
        datasets = process_response_to_class_list(datasets_response["metadata"], Dataset)
        for dataset_model in datasets:
            dataset_model.output_dataset_details()


@get.command(help="Prints metadata or version history of a dataset version")
@click.option(
    "--version-history/--metadata",
    "-v/-m",
    default=False,
    help="Whether to display the version history of a dataset instead of the metadata. Default: -m",
)
@click.option(
    "--long/--short",
    "-l/-s",
    default=False,
    help="Displays extra metadata with the --metadata option. Default: -s",
    type=bool,
)
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool
)
@click.argument("id", nargs=1, required=True, type=str)
@click.argument("version-id", nargs=1, required=True, type=str)
@click.pass_context
def dataset(ctx: Context, id: str, version_id: str, long: bool, version_history: bool, json: bool):
    """Command to the the meta data relating to a given version of a dataset
    \f
    Args:
        ctx (Context): CLI context
        id (str): Dataset ID
        version_id (str): Dataset version ID
        long (bool): Flag to view additional metadata attributes
        version_history (bool): Flag to view version history in place of metadata
        json (bool): Flag to view json returned from API
    """
    metadata = get_latest_dataset_metadata(ctx.obj["jwt"], id, version_id)
    if not version_history:
        if json:
            print_json(metadata)
        else:
            dataset_meta = dataset_metadata.DatasetMetadata(metadata)
            dataset_meta.output_metadata_details(long)
    else:
        version_history = dataset_version_history.DatasetVersionHistory(
            ctx.obj["jwt"], metadata
        )
        version_history.process_version_history(json)


@get.command()
def workflows():
    pass


@get.command()
def groups():
    pass
