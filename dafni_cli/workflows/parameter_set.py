from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

import click
from tabulate import tabulate

from dafni_cli.api.parser import (
    ParserBaseObject,
    ParserParam,
    parse_datetime,
    parse_dict_retaining_keys,
)
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    TABLE_DATASET_VERSION_IDS_HEADER,
    TABLE_GENERATE_VALUES_HEADER,
    TABLE_NAME_HEADER,
    TABLE_PARAMETER_HEADER,
    TABLE_PATH_TO_DATA_HEADER,
    TABLE_STEPS_THAT_CONTAIN_DATASLOT_HEADER,
    TABLE_STEPS_THAT_CONTAIN_PARAMETER_HEADER,
    TABLE_VALUE_HEADER,
    TABLE_VALUES_HEADER,
)
from dafni_cli.utils import format_datetime, format_table
from dafni_cli.workflows.specification import (
    WorkflowSpecification,
    WorkflowSpecificationStep,
)


@dataclass
class WorkflowParameterSetMetadata(ParserBaseObject):
    """Dataclass representing the metadata of a parameter set in a DAFNI
       workflow

    Attributes:
        description (str): A rich description of the parameter set's function
        display_name (str): The display name of the parameter set
        name (str): Name of the parameter set
        publisher (str): The name of the person or organisation who has
                         published the parameter set
        workflow_version_id (str): Version id of the workflow
    """

    description: str
    display_name: str
    name: str
    publisher: str
    workflow_version_id: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("description", "description", str),
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("publisher", "publisher", str),
        ParserParam("workflow_version_id", "workflow_version", str),
    ]


@dataclass
class WorkflowParameterSetSpecDataslot(ParserBaseObject):
    """Dataclass representing a step dataslot as it appears in a workflow
    parameters specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:

        datasets (List[str]): List of version IDs of datasets that fill the
                              slot (Present for loop and model steps)

        The following are present only for the step type: model
        name (str): Name of the dataslot
        path (str): Path to the data in the dataset

        The following are only present for the step type: loop
        steps (str): Step IDs
        dataslot (str): Name of the dataslot being iterated
    """

    datasets: List[str]

    name: Optional[str] = None
    path: Optional[str] = None

    steps: List = field(default_factory=list)
    dataslot: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("datasets", "datasets"),
        ParserParam("name", "name", str),
        ParserParam("path", "path", str),
        ParserParam("steps", "steps"),
        ParserParam("dataslot", "dataslot"),
    ]


@dataclass
class WorkflowParameterSetSpecParameter(ParserBaseObject):
    """Dataclass representing a step parameter as it appears in a workflow
    parameters specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:
        The following are present only for the step type: model
        name (str): Name of the parameter
        value (str): Value of the parameter

        The following are present only for the step type: loop
        steps (List[str]): List of step IDs of steps this parameter is present in
        values (List[str]): Values of this parameter
        parameter (Optional[str]): Name of this parameter
        calculate_values (bool): Appears as 'Generate Values' on front end
    """

    name: Optional[str] = None
    value: Optional[Any] = None

    steps: List[str] = field(default_factory=list)
    values: List[Any] = field(default_factory=list)
    parameter: Optional[str] = None
    calculate_values: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("value", "value"),
        ParserParam("steps", "steps"),
        ParserParam("values", "values"),
        ParserParam("parameter", "parameter", str),
        ParserParam("calculate_values", "calculate_values"),
    ]


@dataclass
class WorkflowParameterSetSpecStep(ParserBaseObject):
    """Dataclass representing a step as it appears in a workflow parameters
    specification

    Not everything is parsed here as there can be a lot of variation and not
    all is currently needed.

    Attributes:
        dataslots (List[WorkflowParameterSetSpecDataslot]): List of dataslots
        kind (str): Type of step e.g. publisher, model
        parameters (List[WorkflowParameterSetSpecParameter]): List of parameters
        base_parameter_set (str): ID of a base parameter set (if applicable)
    """

    dataslots: List[WorkflowParameterSetSpecDataslot]
    kind: str
    parameters: List[WorkflowParameterSetSpecParameter]
    base_parameter_set: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("dataslots", "dataslots", WorkflowParameterSetSpecDataslot),
        ParserParam("kind", "kind", str),
        ParserParam("parameters", "parameters", WorkflowParameterSetSpecParameter),
        ParserParam("base_parameter_set", "base_parameter_set", str),
    ]

    def format_parameters(self) -> str:
        """Formats parameters into a string which prints as a table

        If there aren't any parameters will return a string stating that

        Returns:
            str: Formatted string that will appear as a table when
                 printed
        """
        if not self.parameters:
            return "No parameters"

        if self.kind == "model":
            return format_table(
                headers=[TABLE_PARAMETER_HEADER, TABLE_VALUE_HEADER],
                rows=[
                    [parameter.name, parameter.value] for parameter in self.parameters
                ],
            )
        elif self.kind == "loop":
            return format_table(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_STEPS_THAT_CONTAIN_PARAMETER_HEADER,
                    TABLE_GENERATE_VALUES_HEADER,
                    TABLE_VALUES_HEADER,
                ],
                rows=[
                    [
                        parameter.parameter,
                        "\n".join(parameter.steps),
                        parameter.calculate_values,
                        # Join requires all values to be strings
                        "\n".join([str(value) for value in parameter.values]),
                    ]
                    for parameter in self.parameters
                ],
            )

    def format_dataslots(self) -> str:
        """Formats data slots into a string which prints as a table

        If there aren't any dataslots will return a string stating that

        Returns:
            str: Formatted string that will appear as a table when
                 printed
        """
        if not self.dataslots:
            return "No dataslots"

        if self.kind == "model":
            return format_table(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_PATH_TO_DATA_HEADER,
                    TABLE_DATASET_VERSION_IDS_HEADER,
                ],
                rows=[
                    [dataslot.name, dataslot.path, "\n".join(dataslot.datasets)]
                    for dataslot in self.dataslots
                ],
            )
        elif self.kind == "loop":
            # Here dataslot.datasets is a list of lists, one for each
            # iteration

            return format_table(
                headers=[
                    TABLE_NAME_HEADER,
                    TABLE_STEPS_THAT_CONTAIN_DATASLOT_HEADER,
                    TABLE_DATASET_VERSION_IDS_HEADER,
                ],
                rows=[
                    [
                        dataslot.dataslot,
                        "\n".join(dataslot.steps),
                        "\n".join(
                            [
                                (f"Iteration - {i}: " + "\n".join(dataset_ids))
                                for i, dataset_ids in enumerate(dataslot.datasets)
                            ]
                        ),
                    ]
                    for dataslot in self.dataslots
                ],
            )


@dataclass
class WorkflowParameterSet(ParserBaseObject):
    """Dataclass representing a parameter set of a DAFNI workflow

    Should be identical to ParameterSetRead on swagger.

    Attributes:
        parameter_set_id (str): ID of the parameter set
        owner_id (str): ID of the parameter set owner
        creation_date (datetime): Date and time the parameter set was created
        publication_date (datetime): Date and time the parameter set was
                                     published
        kind (str): Type of DAFNI object (should be "P" for parameter set)
        api_version (str): Version of the DAFNI API used to retrieve the
                           parameter set data
        spec (Dict[str, WorkflowSpecificationStep]): Dictionary of step
                                       ID's and parameters for each step
        metadata (WorkflowParameterSetMetadata): Metadata of the parameter set
    """

    parameter_set_id: str
    owner_id: str
    creation_date: datetime
    publication_date: datetime
    kind: str
    api_version: str
    spec: Dict[str, WorkflowParameterSetSpecStep]
    metadata: WorkflowParameterSetMetadata

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("parameter_set_id", "id", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("kind", "kind", str),
        ParserParam("api_version", "api_version", str),
        ParserParam(
            "spec",
            "spec",
            parse_dict_retaining_keys(WorkflowParameterSetSpecStep),
        ),
        ParserParam("metadata", "metadata", WorkflowParameterSetMetadata),
    ]

    def output_details(self, workflow_spec: WorkflowSpecification):
        """Prints information about this parameter set to command line
        (used for get workflow-parameter-set)

        Args:
            workflow_spec (WorkflowSpecification): Workflow specification this
                                    parameter set comes from (needed to looking
                                    up step's themselves e.g. for their names)
        """

        # Info about the parameter set
        click.echo(self.metadata.display_name)
        click.echo()

        # Go through each step
        for step_id, step in self.spec.items():
            workflow_spec_step: WorkflowSpecificationStep = workflow_spec.steps[step_id]

            click.echo("-" * CONSOLE_WIDTH)
            click.echo(f"Step - {workflow_spec_step.name}")
            click.echo()

            # Check the type (Only model and loop steps are shown on front end,
            # and these are also the only kinds that actually get reported here)
            if workflow_spec_step.kind == "model":
                click.echo(f"Model version ID: {workflow_spec_step.model_version}")
                click.echo()

                click.echo(step.format_parameters())
                click.echo()

                # To match front end, also want to show additional inputs from
                # dependencies but matching up to the path
                included_from = []
                if workflow_spec_step.inputs:
                    for step_id in workflow_spec_step.inputs:
                        dependency = workflow_spec.steps[step_id]
                        included_from.append(dependency.name)

                click.echo(
                    f"Steps data included from: {', '.join(included_from) if included_from else 'No data included from previous steps'}"
                )
                click.echo(step.format_dataslots())
                click.echo()
            elif workflow_spec_step.kind == "loop":
                click.echo(
                    tabulate(
                        [
                            [
                                "Looping workflow version ID:",
                                workflow_spec_step.workflow_version,
                            ],
                            ["Iteration mode:", workflow_spec_step.iteration_mode],
                            [
                                "Base parameter set ID:",
                                step.base_parameter_set
                                if step.base_parameter_set
                                else "No base parameter set",
                            ],
                        ],
                        tablefmt="plain",
                    )
                )
                click.echo()

                click.echo("Parameters to iterate:")
                click.echo(step.format_parameters())
                click.echo()

                click.echo("Dataslots to iterate:")
                click.echo(step.format_dataslots())
                click.echo()
