from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, List, Optional

import click

from dafni_cli.api.parser import ParserBaseObject, ParserParam, parse_datetime
from dafni_cli.consts import (
    CONSOLE_WIDTH,
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_DESCRIPTION_LINE_WIDTH,
    INPUT_MAX_HEADER,
    INPUT_MIN_HEADER,
    INPUT_MIN_MAX_COLUMN_WIDTH,
    INPUT_TITLE_HEADER,
    INPUT_TYPE_COLUMN_WIDTH,
    INPUT_TYPE_HEADER,
    OUTPUT_FORMAT_COLUMN_WIDTH,
    OUTPUT_FORMAT_HEADER,
    OUTPUT_NAME_HEADER,
    OUTPUT_SUMMARY_COLUMN_WIDTH,
    OUTPUT_SUMMARY_HEADER,
    TAB_SPACE,
)
from dafni_cli.utils import optional_column_new, print_json, prose_print


@dataclass
class ModelMetadata(ParserBaseObject):
    """Dataclass representing a DAFNI model's metadata

    Attributes:
        description (str): A rich description of the Model's function
        display_name (str): The display name of the Model
        name (str): Name of the model
        publisher (str): The name of the person or organisation who has
                         published the Model
        summary (str): A short summary of the Model's function
        source_code: A URL pointing to the source code for this Model
        status: Status of model ingest
                    P - Pending
                    F - Failed
                    L - Live
                    S - Superseded
                    D - Deprecated
    """

    description: str
    display_name: str
    name: str
    publisher: str
    summary: str
    source_code: str
    status: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("description", "description", str),
        ParserParam("display_name", "display_name", str),
        ParserParam("name", "name", str),
        ParserParam("publisher", "publisher", str),
        ParserParam("summary", "summary", str),
        ParserParam("source_code", "source_code", str),
        ParserParam("status", "status", str),
    ]


@dataclass
class ModelAuth(ParserBaseObject):
    """Dataclass representing the access the user has for a DAFNI model

    Attributes:
        asset_id (str): ID of the model
        view (bool): View access
        read (bool): Read access
        update (bool): Update access
        destroy (bool): Deletion access
        reason (str): Reason user has access to view this model
    """

    asset_id: str
    view: bool
    read: bool
    update: bool
    destroy: bool
    reason: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("asset_id", "asset_id", str),
        ParserParam("view", "view"),
        ParserParam("read", "read"),
        ParserParam("update", "update"),
        ParserParam("destroy", "destroy"),
        ParserParam("reason", "reason", str),
    ]


@dataclass
class ModelDataslot(ParserBaseObject):
    """Dataclass representing an input dataslot for a DAFNI
       model

    Attributes:
        name (str): Name of the slot
        path (str): Path of the file expected in the container
        defaults (List[str]): List of default dataset ids
        required (str): Whether the slot is required
        description (str): Description of the slot
    """

    name: str
    path: str
    defaults: List[str]
    required: bool
    description: str

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("path", "path", str),
        ParserParam("defaults", "default"),
        ParserParam("required", "required"),
        ParserParam("description", "description"),
    ]


@dataclass
class ModelParameter(ParserBaseObject):
    """Dataclass representing an input parameter for a DAFNI model

    Attributes:
        name (str): Name of the parameter
        type (str): Type of the parameter
        title(str): Title of the parameter
        required (bool): Whether the parameter is required
        description (str): Description of the model parameter
        default (Any): Default value of the parameter
    """

    name: str
    type: str
    title: str
    required: bool
    description: str
    default: Optional[Any] = None

    # TODO: Left over from refactor, may no longer be needed
    # (printed in format_parameters in ModelInputs but untouched for 2 years)
    min: Optional[str] = None
    max: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("type", "type", str),
        ParserParam("title", "title"),
        ParserParam("required", "required"),
        ParserParam("description", "description"),
        ParserParam("default", "default"),
        ParserParam("min", "min"),
        ParserParam("max", "max"),
    ]


@dataclass
class ModelInputs(ParserBaseObject):
    """Dataclass representing inputs for a DAFNI model

    Attributes:
        parameters (List[ModelParameters]): List of parameters for the model
        dataslots (List[ModelDataslot]): List of dataslots for the model
    """

    parameters: List[ModelParameter]
    dataslots: List[ModelDataslot] = field(default_factory=list)

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("parameters", "parameters", ModelParameter),
        ParserParam("dataslots", "dataslots", ModelDataslot),
    ]

    # TODO: Couldn't we use tabulate or something for this?
    @staticmethod
    def params_table_header(title_column_width: int, default_column_width: int) -> str:
        """Formats the header row and the dashed line for an input parameters
           table

        Args:
            title_column_width (int): Width of the title column to fit the
                                      longest title (or "title") plus a buffer
            default_column_width (int): Width of the default column to fit the
                                        longest default (or "default") plus a
                                        buffer

        Returns:
            str: Formatted string for the header and dashed line of the
                 parameters table
        """

        header = (
            f"{INPUT_TITLE_HEADER:{title_column_width}}"
            f"{INPUT_TYPE_HEADER:{INPUT_TYPE_COLUMN_WIDTH}}"
            f"{INPUT_MIN_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
            f"{INPUT_MAX_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
            f"{INPUT_DEFAULT_HEADER:{default_column_width}}"
            f"{INPUT_DESCRIPTION_HEADER}\n"
            + "-"
            * (
                title_column_width
                + INPUT_TYPE_COLUMN_WIDTH
                + 2 * INPUT_MIN_MAX_COLUMN_WIDTH
                + default_column_width
                + INPUT_DESCRIPTION_LINE_WIDTH
            )
            + "\n"
        )
        return header

    def format_parameters(self) -> str:
        """Formats input parameters for a model into a string which prints as
           a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """

        titles = [parameter.title for parameter in self.parameters] + ["title"]
        defaults = ["default"]
        for parameter in self.parameters:
            if parameter.default is not None:
                defaults.append(str(parameter.default))
        title_column_width = len(max(titles, key=len)) + 2
        default_column_width = len(max(defaults, key=len)) + 2
        # Setup headers
        params_table = ModelInputs.params_table_header(
            title_column_width, default_column_width
        )
        # Populate table
        for parameter in self.parameters:
            params_table += f"{parameter.title:{title_column_width}}{parameter.type:{INPUT_TYPE_COLUMN_WIDTH}}"
            params_table += optional_column_new(
                parameter.min, INPUT_MIN_MAX_COLUMN_WIDTH
            )
            params_table += optional_column_new(
                parameter.max, INPUT_MIN_MAX_COLUMN_WIDTH
            )
            params_table += optional_column_new(parameter.default, default_column_width)
            params_table += f"{parameter.description}\n"
        return params_table

    def format_dataslots(self) -> Optional[str]:
        """Formats input data slots to print in a clear way

        Returns:
            Optional[str]: Formatted string that will present the dataslots
                           clearly when printed
        """

        if self.dataslots:
            dataslots_list = ""
            for dataslot in self.dataslots:
                dataslots_list += "Name: " + dataslot.name + "\n"
                dataslots_list += "Path in container: " + dataslot.path + "\n"
                dataslots_list += f"Required: {dataslot.required}\n"
                dataslots_list += "Default Datasets: \n"
                for default in dataslot.defaults:
                    # TODO print name using API call to databases
                    dataslots_list += "ID: " + default + TAB_SPACE
                    # dataslots_list += f'ID: {default["uid"]}' + TAB_SPACE
                    # dataslots_list += f'Version ID: {default["versionUid"]}' + TAB_SPACE
                dataslots_list += "\n"
            return dataslots_list
        return None


@dataclass
class ModelOutputDataset(ParserBaseObject):
    """Dataclass containing information on an output dataset from a model

    Attributes:
        name (str): Name of the dataset output
        type (str): Type of the dataset output
        description (str): Description of the dataset output
    """

    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("name", "name", str),
        ParserParam("type", "type", str),
        ParserParam("description", "description", str),
    ]


@dataclass
class ModelOutputs(ParserBaseObject):
    """Dataclass representing outputs for a DAFNI model

    Attributes:
        datasets (List[ModelOutputDataset]): List of output datasets
    """

    datasets: List[ModelOutputDataset]

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("datasets", "datasets", ModelOutputDataset),
    ]

    @staticmethod
    def outputs_table_header(name_column_width: int) -> str:
        """Formats the header row and the dashed line for the output parameters
           table

        Args:
            name_column_width (int): Width of the name column to fit the
                                     longest name (or "name") plus a buffer

        Returns:
            str: Formatted string for the header and dashed line of the outputs table
        """
        header = (
            f"{OUTPUT_NAME_HEADER:{name_column_width}}"
            f"{OUTPUT_FORMAT_HEADER:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            f"{OUTPUT_SUMMARY_HEADER}\n"
            + "-"
            * (
                name_column_width
                + OUTPUT_FORMAT_COLUMN_WIDTH
                + OUTPUT_SUMMARY_COLUMN_WIDTH
            )
            + "\n"
        )
        return header

    def format_outputs(self) -> str:
        """Formats output files into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed
        """
        names = [dataset.name for dataset in self.datasets] + ["Name"]
        max_name_length = len(max(names, key=len)) + 2
        outputs_table = ModelOutputs.outputs_table_header(max_name_length)

        # The dataset outputs fields are not mandatory and any or all of them might not
        # exist. Unset fields will be reported as "Unknown" in the formatted output.
        for dataset in self.datasets:
            outputs_table += f"{dataset.name or 'Unknown':{max_name_length}}"
            outputs_table += f"{dataset.type or 'Unknown':{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            outputs_table += optional_column_new(dataset.description)
            outputs_table += "\n"
        return outputs_table


@dataclass
class ModelSpec(ParserBaseObject):
    """Dataclass representing the specification of a model (containing
       the image url and inputs)

    Attributes:
        image_url (str): URL of the image of the model
        inputs (ModelInputs): Structure containing the input of the model
    """

    image_url: str
    inputs: Optional[ModelInputs] = None
    outputs: Optional[ModelOutputs] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("image_url", "image", str),
        ParserParam("inputs", "inputs", ModelInputs),
        ParserParam("outputs", "outputs", ModelOutputs),
    ]


@dataclass
class ModelVersion(ParserBaseObject):
    """Dataclass containing information on a historic version of a model

    Attributes:
        version_id (str): ID of the version
        version_message (str): Message labelling the model version
        version_tags (List[str]): Version tags e.g. 'latest'
        publication_date: Date and time this version was published
    """

    version_id: str
    version_message: str
    version_tags: List[str]
    publication_date: datetime

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("version_id", "id", str),
        ParserParam("version_message", "version_message", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("publication_date", "publication_date", parse_datetime),
    ]


@dataclass
class Model(ParserBaseObject):
    """Dataclass representing a DAFNI model

    Attributes:
        api_version(str): Version of the DAFNI API used to retrieve model data
        model_id (str): Model version ID
        container (str): Name of the docker image the model should be run in
        container_version (str): Version of the docker image
        kind (str): Type of DAFNI object (should be "M" for model)
        owner_id (str): ID of the model owner
        parent (str): Parent model ID
        type (str): Type of dafni object ("model")
        creation_date (datetime): Date and time the model was created
        publication_date (datetime): Date and time the model was published
        ingest_completed_date (datetime): Date and time the model finished
                                          ingesting
        version_message (str): Message attached when the model was updated to
                               this model version
        version_tags (List[str]): Any tags created by the publisher for this
                                  model version
        version_history (List[ModelVersion]): Full version history of the
                                              model
        auth (ModelAuth): Authentication credentials giving the permissions
                          the current user has on the model
        metadata (ModelMetadata): Metadata of the model
        spec (ModelSpec): Model specification - includes the image url and its
                          inputs
    """

    api_version: str
    model_id: str
    container: str
    container_version: str
    kind: str
    owner_id: str
    parent_id: str
    type: str
    creation_date: datetime
    publication_date: datetime
    ingest_completed_date: datetime
    version_message: str
    version_tags: List[str]
    version_history: List[ModelVersion]
    auth: ModelAuth
    metadata: ModelMetadata
    spec: ModelSpec

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("api_version", "api_version", str),
        ParserParam("model_id", "id", str),
        ParserParam("container", "container", str),
        ParserParam("container_version", "container_version", str),
        ParserParam("kind", "kind", str),
        ParserParam("owner_id", "owner", str),
        ParserParam("parent_id", "parent", str),
        ParserParam("type", "api_version", str),
        ParserParam("creation_date", "creation_date", parse_datetime),
        ParserParam("publication_date", "publication_date", parse_datetime),
        ParserParam("ingest_completed_date", "ingest_completed_date", parse_datetime),
        ParserParam("version_message", "version_message", str),
        ParserParam("version_tags", "version_tags"),
        ParserParam("version_history", "version_history", ModelVersion),
        ParserParam("auth", "auth", ModelAuth),
        ParserParam("metadata", "metadata", ModelMetadata),
        ParserParam("spec", "spec", ModelSpec),
    ]

    # TODO: Replace with .filter???
    def filter_by_date(self, key: str, date: str) -> bool:
        """Returns whether a particular date is greater than or equal to the
           creation/publication date of this model.

        Args:
            key (str): Key for which date to check must be either 'creation'
                       or 'publication'
            date (str): Date for which models are to be filtered on - format
                        DD/MM/YYYY

        Returns:
            bool: Whether the given date is greater than or equal to the
                  chosen date
        """
        day, month, year = date.split("/")
        date = datetime.date(int(year), int(month), int(day))
        if key.lower() == "creation":
            return self.creation_date.date() >= date
        if key.lower() == "publication":
            return self.publication_date.date() >= date
        raise KeyError("Key should be 'creation' or 'publication'")

    def output_details(self, long: bool = False):
        """Prints relevant model attributes to command line

        Args:
            long (bool): Whether to print with the (potentially long)
                         description
        """
        click.echo(
            "Name: "
            + self.metadata.display_name
            + TAB_SPACE
            + "ID: "
            + self.model_id
            + TAB_SPACE
            + "Date: "
            + self.creation_date.date().strftime("%B %d %Y")
        )
        click.echo("Summary: " + self.metadata["summary"])
        if long:
            click.echo("Description: ")
            prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")

    def output_info(self):
        """Prints information about the model to command line
        """

        click.echo("Name: " + self.metadata.display_name)
        click.echo("Date: " + self.creation_date.strftime("%B %d %Y"))
        click.echo("Summary: ")
        click.echo(self.metadata.summary)
        click.echo("Description: ")
        prose_print(self.metadata.description, CONSOLE_WIDTH)
        click.echo("")
        if self.spec.inputs is not None:
            click.echo("Input Parameters: ")
            click.echo(self.spec.inputs.format_parameters())
            click.echo("Input Data Slots: ")
            click.echo(self.spec.inputs.format_dataslots())
        if self.spec.outputs is not None:
            click.echo("Outputs: ")
            click.echo(self.spec.outputs.format_outputs())

    def output_version_details(self) -> str:
        """Prints model ID, display name, publication date and version
        message on one line
        """
        return (
            "ID: "
            + self.model_id
            + TAB_SPACE
            + "Name: "
            + self.metadata.display_name
            + TAB_SPACE
            + "Publication date: "
            + self.publication_date.date().strftime("%B %d %Y")
            + TAB_SPACE
            + "Version message: "
            + self.version_message
        )
