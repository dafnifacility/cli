from typing import Optional

from dafni_cli.consts import (
    INPUT_TITLE_HEADER,
    INPUT_TYPE_HEADER,
    INPUT_MIN_HEADER,
    INPUT_MAX_HEADER,
    INPUT_DEFAULT_HEADER,
    INPUT_DESCRIPTION_HEADER,
    INPUT_TYPE_COLUMN_WIDTH,
    INPUT_MIN_MAX_COLUMN_WIDTH,
    INPUT_DESCRIPTION_LINE_WIDTH,
    OUTPUT_NAME_HEADER,
    OUTPUT_FORMAT_HEADER,
    OUTPUT_SUMMARY_HEADER,
    OUTPUT_FORMAT_COLUMN_WIDTH,
    OUTPUT_SUMMARY_COLUMN_WIDTH,
    TAB_SPACE,
)
from dafni_cli.utils import optional_column


def params_table_header(title_column_width: int, default_column_width: int) -> str:
    """
    Formats the header row and the dashed line for the input parameters table
    Args:
        title_column_width (int): width of the title column to fit the longest title (or "title") plus a buffer
        default_column_width (int): width of the default column to fit the longest default (or "default") plus a buffer

    Returns:
        str: Formatted string for the header and dashed line of the parameters table
    """
    header = (
        f"{INPUT_TITLE_HEADER:{title_column_width}}"
        f"{INPUT_TYPE_HEADER:{INPUT_TYPE_COLUMN_WIDTH}}"
        f"{INPUT_MIN_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
        f"{INPUT_MAX_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
        f"{INPUT_DEFAULT_HEADER:{default_column_width}}"
        f"{INPUT_DESCRIPTION_HEADER}\n"
        + f"-"
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


def outputs_table_header(name_column_width: int) -> str:
    """
    Formats the header row and the dashed line for the output parameters table
    Args:
        name_column_width (int): width of the name column to fit the longest name (or "name") plus a buffer

    Returns:
        str: Formatted string for the header and dashed line of the outputs table
    """
    header = (
        f"{OUTPUT_NAME_HEADER:{name_column_width}}"
        f"{OUTPUT_FORMAT_HEADER:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
        f"{OUTPUT_SUMMARY_HEADER}\n"
        + f"-"
        * (name_column_width + OUTPUT_FORMAT_COLUMN_WIDTH + OUTPUT_SUMMARY_COLUMN_WIDTH)
        + "\n"
    )
    return header


class ModelMetadata:
    """
    Contains metadata of a model uploaded to DAFNI.

    Methods:
        format_parameters: Formats the parameter inputs to be displayed in a clear way
        format_dataslots: Formats the dataslots inputs to be displayed in a clear way
        format_outputs: Formats the outputs to be displayed in a clear way

    Attributes:
        dictionary: Python dictionary with all the metadata obtained from the DAFNI API
        inputs: Python dictionary containing the parameter and dataslot input details for the model
        outputs: Python dictionary containing the output file details for the model
        owner: User ID of the publisher of the model
    """

    def __init__(self, metadata_dict: dict):
        """
        Initialises the metadata properties from the metadata dictionary.
        Args:
            metadata_dict (dict): Dictionary from the DAFNI API containing the metadata.
        """
        self.dictionary = metadata_dict
        if "inputs" in metadata_dict["spec"]:
            self.inputs = metadata_dict["spec"]["inputs"]
        else:
            self.inputs = None
        if "outputs" in metadata_dict["spec"]:
            self.outputs = metadata_dict["spec"]["outputs"]
        else:
            self.outputs = None
        self.owner = metadata_dict["metadata"]["owner"]

    def format_parameters(self) -> str:
        """
        Formats input parameters for the model into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed.
        """
        parameters = self.inputs["env"]
        titles = [parameter["title"] for parameter in parameters] + ["title"]
        defaults = ["default"]
        for parameter in parameters:
            if "default" in parameter:
                defaults.append(str(parameter["default"]))
        title_column_width = len(max(titles, key=len)) + 2
        default_column_width = len(max(defaults, key=len)) + 2
        # Setup headers
        params_table = params_table_header(title_column_width, default_column_width)
        # Populate table
        for parameter in parameters:
            params_table += f"{parameter['title']:{title_column_width}}{parameter['type']:{INPUT_TYPE_COLUMN_WIDTH}}"
            params_table += optional_column(
                parameter, "min", INPUT_MIN_MAX_COLUMN_WIDTH
            )
            params_table += optional_column(
                parameter, "max", INPUT_MIN_MAX_COLUMN_WIDTH
            )
            params_table += optional_column(parameter, "default", default_column_width)
            params_table += f"{parameter['desc']}\n"
        return params_table

    def format_dataslots(self) -> Optional[str]:
        """
        Formats input data slots to print in a clear way

        Returns:
            Optional[str]: Formatted string that will present the dataslots clearly when printed.
        """
        if "dataslots" in self.inputs:
            dataslots = self.inputs["dataslots"]
            dataslots_list = ""
            for dataslot in dataslots:
                dataslots_list += "Name: " + dataslot["name"] + "\n"
                dataslots_list += "Path in container: " + dataslot["path"] + "\n"
                dataslots_list += f"Required: {dataslot['required']}\n"
                dataslots_list += "Default Datasets: \n"
                for default in dataslot["default"]:
                    # TODO print name using API call to databases
                    dataslots_list += "Name: "
                    dataslots_list += f'ID: {default["uid"]}' + TAB_SPACE
                    dataslots_list += f'Version ID: {default["versionUid"]}' + TAB_SPACE
                dataslots_list += "\n"
            return dataslots_list
        else:
            return None

    def format_outputs(self) -> str:
        """
        Formats output files into a string which prints as a table

        Returns:
            str: Formatted string that will appear as a table when printed.
        """
        names = [output["name"] for output in self.outputs["datasets"]] + ["Name"]
        max_name_length = len(max(names, key=len)) + 2
        outputs_table = outputs_table_header(max_name_length)
        for dataset in self.outputs["datasets"]:
            outputs_table += f"{dataset['name']:{max_name_length}}"
            outputs_table += f"{dataset['type']:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            outputs_table += optional_column(dataset, "description")
            outputs_table += "\n"
        return outputs_table
