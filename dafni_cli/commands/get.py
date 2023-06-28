from typing import List, Optional

import click
from click import Context

from dafni_cli.api.datasets_api import get_all_datasets
from dafni_cli.api.models_api import get_all_models
from dafni_cli.api.session import DAFNISession
from dafni_cli.api.workflows_api import get_all_workflows
from dafni_cli.commands.helpers import (
    cli_get_latest_dataset_metadata,
    cli_get_model,
    cli_get_workflow,
)
from dafni_cli.consts import DATE_INPUT_FORMAT, DATE_INPUT_FORMAT_VERBOSE
from dafni_cli.datasets import dataset_filtering
from dafni_cli.datasets.dataset import parse_datasets
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.filtering import (
    creation_date_filter,
    filter_multiple,
    publication_date_filter,
    text_filter,
)
from dafni_cli.models.model import parse_model, parse_models
from dafni_cli.utils import print_json
from dafni_cli.workflows.workflow import parse_workflow, parse_workflows


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
    "--search",
    default=None,
    help="Search text to filter by. Models with this text in either their display name or summary will be displayed.",
    type=str,
)
@click.option(
    "--creation-date",
    default=None,
    help=f"Filter for models created since given date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
)
@click.option(
    "--publication-date",
    default=None,
    help=f"Filter for models published since given date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
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
    ctx: Context,
    long: bool,
    search: Optional[str],
    creation_date: str,
    publication_date: str,
    json: bool,
):
    """Displays list of model details with other options allowing
        more details to be listed, filters, and for the json to be displayed.

    Args:
        ctx (context): contains user session for authentication
        long (bool): whether to print the description of each model as well
        search (Optional[str]): Search text to filter models by
        creation_date (str): for filtering by creation date. Format:
                             DATE_INPUT_FORMAT_VERBOSE
        publication_date (str): for filtering by publication date. Format:
                                DATE_INPUT_FORMAT_VERBOSE
        json (bool): whether to print the raw json returned by the DAFNI API
    """
    model_dict_list = get_all_models(ctx.obj["session"])
    model_list = parse_models(model_dict_list)

    # Apply filtering
    filters = []
    if search:
        filters.append(text_filter(search))
    if creation_date:
        filters.append(creation_date_filter(creation_date))
    if publication_date:
        filters.append(publication_date_filter(publication_date))

    filtered_models, filtered_model_dicts = filter_multiple(
        filters, model_list, model_dict_list
    )

    # Output
    if json:
        print_json(filtered_model_dicts)
    else:
        for model_inst in filtered_models:
            model_inst.output_details(long)


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
        # Attempt to get the model
        model_dictionary = cli_get_model(ctx.obj["session"], vid)

        if version_history:
            if json:
                for version_json in model_dictionary["version_history"]:
                    print_json(version_json)
            else:
                model_inst = parse_model(model_dictionary)
                model_inst.output_version_history()
        else:
            if json:
                print_json(model_dictionary)
            else:
                model_inst = parse_model(model_dictionary)
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
    help=f"Filter for datasets with a start date since given date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
)
@click.option(
    "--end-date",
    default=None,
    help=f"Filter for datasets with a end date up to given date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
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
        start_date (Optional[str]): Filter for datasets with a start date since given date. Format:
                                    DATE_INPUT_FORMAT_VERBOSE
        end_date (Optional[str]): Filter for datasets with a end date up to given date. Format:
                                  DATE_INPUT_FORMAT_VERBOSE
        json (Optional[bool]): Whether to output raw json from API or pretty print information. Defaults to False.
    """
    filters = dataset_filtering.process_datasets_filters(search, start_date, end_date)
    dataset_dict_list = get_all_datasets(ctx.obj["session"], filters)
    if json:
        print_json(dataset_dict_list)
    else:
        dataset_list = parse_datasets(dataset_dict_list)
        for dataset_inst in dataset_list:
            dataset_inst.output_brief_details()


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
@click.argument("version-id", nargs=1, required=True, type=str)
@click.pass_context
def dataset(
    ctx: Context,
    version_id: str,
    long: bool,
    version_history: bool,
    json: bool,
):
    """Command to the the meta data relating to a given version of a dataset

    Args:
        ctx (Context): CLI context
        version_id (str): Dataset version ID
        long (bool): Flag to view additional metadata attributes
        version_history (bool): Flag to view version history in place of metadata
        json (bool): Flag to view json returned from API
    """
    # Attempt to get the metadata
    metadata = cli_get_latest_dataset_metadata(ctx.obj["session"], version_id)

    if not version_history:
        if json:
            print_json(metadata)
        else:
            metadata_inst = parse_dataset_metadata(metadata)
            metadata_inst.output_details(long)
    else:
        if json:
            print_json(metadata["version_history"])
        else:
            metadata_inst = parse_dataset_metadata(metadata)
            click.echo(f"{metadata_inst.title}\n")
            metadata_inst.version_history.output_version_history()


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
    "--search",
    default=None,
    help="Search text to filter by. Workflows with this text in either their display name or summary will be displayed.",
    type=str,
)
@click.option(
    "--creation-date",
    default=None,
    help=f"Filter for workflows created since given date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
)
@click.option(
    "--publication-date",
    default=None,
    help=f"Filter for workflows published since given date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
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
    ctx: Context,
    long: bool,
    search: Optional[str],
    creation_date: Optional[str],
    publication_date: Optional[str],
    json: bool,
):
    """
    Display attributes of all workflows. Options allow more details to be listed,
    the list of workflows to be filtered, and for the json to be displayed.

    Args:
        ctx (context): contains user session for authentication
        long (bool): whether to print the description of each model as well
        search (Optional[str]): Search text to filter workflows by
        creation_date (Optional[str]): for filtering by creation date. Format:
                                       DATE_INPUT_FORMAT_VERBOSE
        publication_date (Optional[str]): for filtering by publication date. Format:
                                          DATE_INPUT_FORMAT_VERBOSE
        json (bool): whether to print the raw json returned by the DAFNI API
    """
    workflow_dict_list = get_all_workflows(ctx.obj["session"])
    workflow_list = parse_workflows(workflow_dict_list)

    # Apply filtering
    filters = []
    if search:
        filters.append(text_filter(search))
    if creation_date:
        filters.append(creation_date_filter(creation_date))
    if publication_date:
        filters.append(publication_date_filter(publication_date))

    filtered_workflows, filtered_workflow_dicts = filter_multiple(
        filters, workflow_list, workflow_dict_list
    )

    # Output
    if json:
        print_json(filtered_workflow_dicts)
    else:
        for workflow_inst in filtered_workflows:
            workflow_inst.output_details(long)


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
        # Attempt to get the workflow
        workflow_dictionary = cli_get_workflow(ctx.obj["session"], vid)

        if version_history:
            if json:
                for version_json in workflow_dictionary["version_history"]:
                    print_json(version_json)
            else:
                workflow_inst = parse_workflow(workflow_dictionary)
                workflow_inst.output_version_history()
        else:
            if json:
                print_json(workflow_dictionary)
            else:
                workflow_inst = parse_workflow(workflow_dictionary)
                workflow_inst.output_info()


###############################################################################
# Workflow instance commands
###############################################################################
@get.command(help="List and filter workflow instances")
@click.argument("version-id", required=True)
@click.option(
    "--json/--pretty",
    "-j/-p",
    default=False,
    help="Prints raw json returned from API. Default: -p",
    type=bool,
)
@click.pass_context
def workflow_instances(
    ctx: Context,
    version_id: str,
    json: bool,
):
    """Display attributes of all workflows instances for a particular workflow
    version

    Args:
        ctx (context): Contains user session for authentication
        version_id (str): Version ID of the workflow to display the instances
                          of
        json (bool): Whether to print the raw json returned by the DAFNI API
    """
    workflow_dict = cli_get_workflow(ctx.obj["session"], version_id)
    workflow_inst = parse_workflow(workflow_dict)

    # Output
    if json:
        print_json(workflow_dict["instances"])
    else:
        click.echo(workflow_inst.format_instances())
