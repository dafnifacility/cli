from typing import List, Optional

import click
from click import Context

from dafni_cli.api.datasets_api import (get_all_datasets,
                                        get_latest_dataset_metadata)
from dafni_cli.api.models_api import get_all_models, get_model
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_all_workflows
from dafni_cli.datasets import dataset_filtering
from dafni_cli.datasets.dataset import Dataset
from dafni_cli.datasets.dataset_metadata import DatasetMetadata
from dafni_cli.model.model import Model
from dafni_cli.utils import print_json, process_response_to_class_list
from dafni_cli.workflow.version_history import WorkflowVersionHistory
from dafni_cli.workflow.workflow import Workflow


@click.group(help="Lists entities available to the user")
@click.pass_context
def get(ctx: Context):
    """Lists entities available to the user from
    models, datasets, workflows, groups, depending on command.

    Args:
        ctx (Context): Context containing the user session.
    """
    ctx.ensure_object(dict)
    ctx.obj["session"] = DAFNISession()


###############################################################################
# Models commands
###############################################################################
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
    type=bool,
)
@click.pass_context
def models(
    ctx: Context, long: bool, creation_date: str, publication_date: str, json: bool
):
    """Displays list of model details with other options allowing
        more details to be listed, filters, and for the json to be displayed.

    Args:
        ctx (context): contains user session for authentication
        long (bool): whether to print the description of each model as well
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
        json (bool): whether to print the raw json returned by the DAFNI API
    """
    model_dict_list = get_all_models(ctx.obj["session"])
    model_list: List[Model] = ParserBaseObject.parse_from_dict_list(
        Model, model_dict_list
    )

    filtered_model_dict_list = []
    for model_inst, model_dict in zip(model_list, model_dict_list):
        date_filter = True
        if creation_date:
            date_filter = model_inst.filter_by_date("creation", creation_date)
        if publication_date:
            date_filter = model_inst.filter_by_date("publication", publication_date)
        if date_filter:
            if json:
                filtered_model_dict_list.append(model_dict)
            else:
                model_inst.output_details(long)
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
    type=bool,
)
@click.pass_context
def model(ctx: Context, version_id: List[str], version_history: bool, json: bool):
    """Displays the metadata for one or more model versions

    Args:
        ctx (Context): contains user session for authentication
        version_id (list[str]): List of version IDs of the models to be displayed
        version_history (bool): Whether to display version_history instead of metadata
        json (bool): Whether to output raw json from API or pretty print metadata/version history. Defaults to False.
    """
    for vid in version_id:
        model_dictionary = get_model(ctx.obj["session"], vid)

        if version_history:
            if json:
                for version_json in model_dictionary["version_history"]:
                    print_json(version_json)
            else:
                model_inst: Model = ParserBaseObject.parse_from_dict(
                    Model, model_dictionary
                )
                model_inst.output_version_history()
        else:
            if json:
                print_json(model_dictionary)
            else:
                model_inst: Model = ParserBaseObject.parse_from_dict(
                    Model, model_dictionary
                )
                model_inst.output_info()


###############################################################################
# Datasets commands
###############################################################################
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
    type=bool,
)
@click.pass_context
def datasets(
    ctx: Context,
    search: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    json: Optional[bool],
):
    """
    Display a list of all available datasets

    Args:
        ctx (context): contains user session for authentication
        search (Optional[str]): Search terms for elastic search. Format: "search terms"
        start_date (Optional[str]): Filter for datasets with a start date since given date. Format: DD/MM/YYYY
        end_date (Optional[str]): Filter for datasets with a end date up to given date. Format: DD/MM/YYYY
        json (Optional[bool]): Whether to output raw json from API or pretty print information. Defaults to False.
    """
    filters = dataset_filtering.process_datasets_filters(search, start_date, end_date)
    datasets_response = get_all_datasets(ctx.obj["session"], filters)
    if json:
        print_json(datasets_response)
    else:
        dataset_list = ParserBaseObject.parse_from_dict_list(
            Dataset, datasets_response["metadata"]
        )
        for dataset_model in dataset_list:
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
    type=bool,
)
@click.argument("id", nargs=1, required=True, type=str)
@click.argument("version-id", nargs=1, required=True, type=str)
@click.pass_context
def dataset(
    ctx: Context,
    id: str,
    version_id: str,
    long: bool,
    version_history: bool,
    json: bool,
):
    """Command to the the meta data relating to a given version of a dataset

    Args:
        ctx (Context): CLI context
        id (str): Dataset ID
        version_id (str): Dataset version ID
        long (bool): Flag to view additional metadata attributes
        version_history (bool): Flag to view version history in place of metadata
        json (bool): Flag to view json returned from API
    """
    metadata = get_latest_dataset_metadata(ctx.obj["session"], id, version_id)

    if not version_history:
        if json:
            print_json(metadata)
        else:
            dataset_meta: DatasetMetadata = ParserBaseObject.parse_from_dict(
                DatasetMetadata, metadata
            )
            dataset_meta.output_metadata_details(long)
    else:
        dataset_meta: DatasetMetadata = ParserBaseObject.parse_from_dict(
            DatasetMetadata, metadata
        )
        dataset_meta.version_history.process_version_history(ctx.obj["session"], json)


###############################################################################
# Workflows commands
###############################################################################
@get.command(help="List and filter models")
@click.option(
    "--long/--short",
    "-l/-s",
    default=False,
    help="Also displays the description of each workflow. Default: -s",
    type=bool,
)
@click.option(
    "--creation-date",
    default=None,
    help="Filter for workflows created since given date. Format: DD/MM/YYYY",
    type=str,
)
@click.option(
    "--publication-date",
    default=None,
    help="Filter for workflows published since given date. Format: DD/MM/YYYY",
    type=str,
)
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool,
)
@click.pass_context
def workflows(
    ctx: Context, long: bool, creation_date: str, publication_date: str, json: bool
):
    """
    Display attributes of all workflows. Options allow more details to be listed,
    the list of workflows to be filtered, and for the json to be displayed.

    Args:
        ctx (context): contains user session for authentication
        long (bool): whether to print the description of each model as well
        creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
        publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
        json (bool): whether to print the raw json returned by the DAFNI API
    """
    workflow_dict_list = get_all_workflows(ctx.obj["session"])
    workflow_list = process_response_to_class_list(workflow_dict_list, Workflow)
    filtered_workflow_dict_list = []
    for workflow in workflow_list:
        date_filter = True
        if creation_date:
            date_filter = workflow.filter_by_date("creation", creation_date)
        if publication_date:
            date_filter = workflow.filter_by_date("publication", publication_date)
        if date_filter:
            if json:
                filtered_workflow_dict_list.append(workflow.dictionary)
            else:
                workflow.output_details(long)
    if json:
        print_json(filtered_workflow_dict_list)


@get.command(
    help="Display metadata or version history of a particular workflow or workflows"
)
@click.argument("version-id", nargs=-1, required=True)
@click.option(
    "--version-history/--metadata",
    "-v/-m",
    default=False,
    help="Whether to display the version history of a workflow instead of the metadata. Default -m",
)
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool,
)
@click.pass_context
def workflow(ctx: Context, version_id: List[str], version_history: bool, json: bool):
    """
    Displays the metadata for a workflow, for one or more versions of that workflow
    from its version history.

    Args:
        ctx (Context): contains user session for authentication
        version_id (list[str]): List of version IDs of the workflows to be displayed
        version_history (bool): Whether to display version_history instead of metadata
        json (bool): Whether to output raw json from API or pretty print metadata/version history. Defaults to False.
    """
    for vid in version_id:
        workflow = Workflow(vid)
        workflow.get_attributes_from_id(ctx.obj["session"], vid)

        if version_history:
            history = WorkflowVersionHistory(ctx.obj["session"], workflow)
            history.output_version_history(json)
        else:
            workflow.get_metadata(ctx.obj["session"])
            workflow.output_metadata(json)


@get.command()
def groups():
    pass
