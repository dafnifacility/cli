from datetime import datetime
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
    cli_get_workflow_instance,
    cli_get_workflow_parameter_set,
)
from dafni_cli.commands.options import filter_flag_option, json_option
from dafni_cli.consts import (
    DATE_INPUT_FORMAT,
    DATE_INPUT_FORMAT_VERBOSE,
    DATE_TIME_INPUT_FORMAT,
    DATE_TIME_INPUT_FORMAT_VERBOSE,
    TABLE_ACCESS_HEADER,
    TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH,
    TABLE_FINISHED_HEADER,
    TABLE_ID_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PARAMETER_SET_HEADER,
    TABLE_PUBLICATION_DATE_HEADER,
    TABLE_STARTED_HEADER,
    TABLE_STATUS_HEADER,
    TABLE_SUMMARY_HEADER,
    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
    TABLE_VERSION_ID_HEADER,
    TABLE_WORKFLOW_VERSION_ID_HEADER,
)
from dafni_cli.datasets import dataset_filtering
from dafni_cli.datasets.dataset import parse_datasets
from dafni_cli.datasets.dataset_metadata import parse_dataset_metadata
from dafni_cli.filtering import (
    creation_date_filter,
    end_filter,
    filter_multiple,
    publication_date_filter,
    start_filter,
    status_filter,
    text_filter,
)
from dafni_cli.models.model import parse_model, parse_models
from dafni_cli.utils import format_table, print_json
from dafni_cli.workflows.instance import parse_workflow_instance
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
@json_option
@click.pass_context
def models(
    ctx: Context,
    search: Optional[str],
    creation_date: datetime,
    publication_date: datetime,
    json: bool,
):
    """Displays list of model details with other options allowing
    more details to be listed, filters, and for the json to be displayed.

    Args:
        ctx (context): Contains user session for authentication
        search (Optional[str]): Search text to filter models by
        creation_date (datetime): For filtering by creation date. Format:
                             DATE_INPUT_FORMAT_VERBOSE
        publication_date (datetime): for filtering by publication date. Format:
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
        # Print brief details in a table
        rows = []
        for model_inst in filtered_models:
            rows.append(model_inst.get_brief_details())
        click.echo(
            format_table(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_VERSION_ID_HEADER,
                    TABLE_STATUS_HEADER,
                    TABLE_ACCESS_HEADER,
                    TABLE_PUBLICATION_DATE_HEADER,
                    TABLE_SUMMARY_HEADER,
                ],
                rows=rows,
                max_column_widths=[
                    TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH,
                    None,
                    None,
                    None,
                    None,
                    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
                ],
            )
        )


@get.command(help="Display metadata or version history of a model or models")
@click.argument("version-id", nargs=-1, required=True)
@click.option(
    "--version-history/--metadata",
    "-v/-m",
    default=False,
    help="Whether to display the version history of a model instead of the metadata. Default -m",
)
@json_option
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
                model_inst.output_details()


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
@json_option
@click.pass_context
def datasets(
    ctx: Context,
    search: Optional[str],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    json: Optional[bool],
):
    """
    Display a list of all available datasets

    Args:
        ctx (context): contains user session for authentication
        search (Optional[str]): Search terms for elastic search.
                                Format: "search terms"
        start_date (Optional[datetime]): Filter for datasets with a start date
                            since given date. Format: DATE_INPUT_FORMAT_VERBOSE
        end_date (Optional[datetime]): Filter for datasets with an end date up
                            to given date. Format: DATE_INPUT_FORMAT_VERBOSE
        json (Optional[bool]): Whether to output raw json from API or pretty
                               print information. Defaults to False.
    """
    filters = dataset_filtering.process_datasets_filters(search, start_date, end_date)
    dataset_dict_list = get_all_datasets(ctx.obj["session"], filters)
    if json:
        print_json(dataset_dict_list)
    else:
        dataset_list = parse_datasets(dataset_dict_list)
        for dataset_inst in dataset_list:
            dataset_inst.output_brief_details()


@get.command(help="Display metadata or version history of a particular dataset version")
@click.argument("version-id", nargs=1, required=True, type=str)
@click.option(
    "--long/--short",
    "-l/-s",
    default=False,
    help="Displays extra metadata with the --metadata option. Default: -s",
    type=bool,
)
@click.option(
    "--version-history/--metadata",
    "-v/-m",
    default=False,
    help="Whether to display the version history of a dataset instead of the metadata. Default: -m",
)
@json_option
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
@get.command(help="List and filter workflows")
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
@json_option
@click.pass_context
def workflows(
    ctx: Context,
    search: Optional[str],
    creation_date: Optional[datetime],
    publication_date: Optional[datetime],
    json: bool,
):
    """
    Display attributes of all workflows. Options allow more details to be listed,
    the list of workflows to be filtered, and for the json to be displayed.

    Args:
        ctx (context): contains user session for authentication
        search (Optional[str]): Search text to filter workflows by
        creation_date (Optional[datetime]): For filtering by creation date.
                                            Format: DATE_INPUT_FORMAT_VERBOSE
        publication_date (Optional[datetime]): For filtering by publication date.
                                            Format: DATE_INPUT_FORMAT_VERBOSE
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
        # Print brief details in a table
        rows = []
        for workflow_inst in filtered_workflows:
            rows.append(workflow_inst.get_brief_details())
        click.echo(
            format_table(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_VERSION_ID_HEADER,
                    TABLE_PUBLICATION_DATE_HEADER,
                    TABLE_SUMMARY_HEADER,
                ],
                rows=rows,
                max_column_widths=[
                    TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH,
                    None,
                    None,
                    TABLE_SUMMARY_MAX_COLUMN_WIDTH,
                ],
            )
        )


@get.command(help="Display metadata or version history of a workflow or workflows")
@click.argument("version-id", nargs=-1, required=True)
@click.option(
    "--version-history/--metadata",
    "-v/-m",
    default=False,
    help="Whether to display the version history of a workflow instead of the metadata. Default -m",
)
@json_option
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
                workflow_inst.output_details()


###############################################################################
# Workflow instance commands
###############################################################################
@get.command(help="List and filter workflow instances")
@click.argument("version-id", required=True)
@click.option(
    "--start",
    default=None,
    help=f"Filter instances submitted after a given date/time. Format: {DATE_INPUT_FORMAT_VERBOSE} or {DATE_TIME_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT, DATE_TIME_INPUT_FORMAT]),
)
@click.option(
    "--end",
    default=None,
    help=f"Filter instances that finished after a given date/time. Format: {DATE_INPUT_FORMAT_VERBOSE} or {DATE_TIME_INPUT_FORMAT_VERBOSE}",
    type=click.DateTime(formats=[DATE_INPUT_FORMAT, DATE_TIME_INPUT_FORMAT]),
)
@filter_flag_option("--cancelled", help="Filters instances with a 'Cancelled' status.")
@filter_flag_option("--error", help="Filters instances with a 'Error' status.")
@filter_flag_option(
    "--succeeded", "-s", help="Filters instances with a 'Succeeded' status."
)
@filter_flag_option("--failed", "-f", help="Filters instances with a 'Failed' status.")
@filter_flag_option("--omitted", help="Filters instances with an 'Omitted' status.")
@filter_flag_option("--pending", help="Filters instances with a 'Pending' status.")
@filter_flag_option("--running", help="Filters instances with a 'Running' status.")
@json_option
@click.pass_context
def workflow_instances(
    ctx: Context,
    version_id: str,
    start: Optional[datetime],
    end: Optional[datetime],
    cancelled: bool,
    error: bool,
    failed: bool,
    omitted: bool,
    pending: bool,
    running: bool,
    succeeded: bool,
    json: bool,
):
    """Display attributes of all workflows instances for a particular workflow
    version

    Args:
        ctx (context): Contains user session for authentication
        version_id (str): Version ID of the workflow to display the instances
                          of
        start (Optional[str]): For filtering by start date/time. Format:
                               DATE_INPUT_FORMAT_VERBOSE or
                               DATE_TIME_INPUT_FORMAT_VERBOSE
        end (Optional[str]): For filtering by start date/time. Format:
                             DATE_INPUT_FORMAT_VERBOSE or
                             DATE_TIME_INPUT_FORMAT_VERBOSE
        cancelled (bool): Whether to filter instances with a cancelled status
        failed (bool): Whether to filter instances with a failed status
        error (bool): Whether to filter instances with an error status
        running (bool): Whether to filter instances with a running status
        succeeded (bool): Whether to filter instances with a successful status
        json (bool): Whether to print the raw json returned by the DAFNI API
    """
    workflow_dict = cli_get_workflow(ctx.obj["session"], version_id)
    workflow_inst = parse_workflow(workflow_dict)

    # Apply filtering
    filters = []
    if start:
        filters.append(start_filter(start))
    if end:
        filters.append(end_filter(end))
    if cancelled:
        filters.append(status_filter("Cancelled"))
    if error:
        filters.append(status_filter("Error"))
    if failed:
        filters.append(status_filter("Failed"))
    if omitted:
        filters.append(status_filter("Omitted"))
    if pending:
        filters.append(status_filter("Pending"))
    if running:
        filters.append(status_filter("Running"))
    if succeeded:
        filters.append(status_filter("Succeeded"))

    filtered_instances, filtered_instance_dicts = filter_multiple(
        filters, workflow_inst.instances, workflow_dict["instances"]
    )

    # Output
    if json:
        print_json(filtered_instance_dicts)
    else:
        click.echo(
            format_table(
                headers=[
                    TABLE_ID_HEADER,
                    TABLE_WORKFLOW_VERSION_ID_HEADER,
                    TABLE_PARAMETER_SET_HEADER,
                    TABLE_STARTED_HEADER,
                    TABLE_FINISHED_HEADER,
                    TABLE_STATUS_HEADER,
                ],
                rows=[
                    instance.get_brief_details()
                    for instance in sorted(
                        filtered_instances, key=lambda inst: inst.finished_time
                    )
                ],
            )
        )


@get.command(help="Display information about a workflow instance")
@click.argument("instance-id", required=True)
@json_option
@click.pass_context
def workflow_instance(
    ctx: Context,
    instance_id: str,
    json: bool,
):
    """Display attributes of all workflows instances for a particular workflow
    version

    Args:
        ctx (context): Contains user session for authentication
        instance_id (str): Instance ID of the workflow instance to display
        json (bool): Whether to print the raw json returned by the DAFNI API
    """
    workflow_instance_dict = cli_get_workflow_instance(ctx.obj["session"], instance_id)

    # Output
    if json:
        print_json(workflow_instance_dict)
    else:
        workflow_instance_obj = parse_workflow_instance(workflow_instance_dict)
        workflow_instance_obj.output_details()


@get.command(help="Display information about a workflow's parameter set")
@click.argument("workflow-version-id", required=True)
@click.argument("parameter-set-id", required=True)
@json_option
@click.pass_context
def workflow_parameter_set(
    ctx: Context,
    workflow_version_id: str,
    parameter_set_id: str,
    json: bool,
):
    """Display details of a parameter set found in a particular workflow

    Args:
        ctx (context): Contains user session for authentication
        workflow_version_id (str): Version ID of the workflow the parameter
                                   set is found in
        parameter_set_id (str): ID of the parameter set
        json (bool): Whether to print the raw json returned by the DAFNI API
    """
    workflow_inst, parameter_set = cli_get_workflow_parameter_set(
        ctx.obj["session"], workflow_version_id, parameter_set_id
    )

    # Output
    if json:
        print_json(parameter_set.dictionary)
    else:
        parameter_set.output_details(workflow_inst.spec)
