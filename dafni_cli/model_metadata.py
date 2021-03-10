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
)


def optional_column(
    dictionary: dict, key: str, column_width: int = 0, alignment: str = "<"
):
    """Adds a value to a column, if the key exists in the dictionary
    and adds spaces of the appropriate width if not.
    Args:
         dictionary (dict): Dictionary with data inside
         key (str): Key of the data that is to be checked and added if present
         column_width (int): Number of spaces to be returned instead if the key is not present
         alignment (str): Specified alignment of column
    Returns:
        entry (str): Either the value of the entry to be put into the table, column_width number of spaces
    """
    if key in dictionary:
        if column_width > 0:
            entry = f"{dictionary[key]:{alignment}{column_width}}"
        elif column_width == 0:
            entry = f"{dictionary[key]}"
        else:
            raise ValueError(
                "Column width for optional column must be positive or zero"
            )
    else:
        entry = f" " * column_width
    return entry


class ModelMetadata:
    def __init__(self, metadata_dict: dict):
        self.json = metadata_dict
        if "inputs" in metadata_dict["spec"]:
            self.inputs = metadata_dict["spec"]["inputs"]
        if "outputs" in metadata_dict["spec"]:
            self.outputs = metadata_dict["spec"]["outputs"]
        self.owner = metadata_dict["metadata"]["owner"]
        self.name = metadata_dict["metadata"]["name"]

    def format_parameters(self) -> str:
        """Formats input parameters for the model into a string which prints as a table"""
        parameters = self.inputs["env"]
        titles = [parameter["title"] for parameter in parameters] + ["title"]
        defaults = ["default"]
        for parameter in parameters:
            if "default" in parameter:
                defaults.append("default")
        max_title_length = len(max(titles, key=len)) + 2
        max_default_length = len(max(defaults, key=len)) + 2
        # Setup headers
        params_table = (
            f"{INPUT_TITLE_HEADER:{max_title_length}}"
            f"{INPUT_TYPE_HEADER:{INPUT_TYPE_COLUMN_WIDTH}}"
            f"{INPUT_MIN_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
            f"{INPUT_MAX_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}"
            f"{INPUT_DEFAULT_HEADER:{max_default_length}}"
            f"{INPUT_DESCRIPTION_HEADER}\n"
            + f"-"
            * (
                max_title_length
                + INPUT_TYPE_COLUMN_WIDTH
                + 2 * INPUT_MIN_MAX_COLUMN_WIDTH
                + max_default_length
                + INPUT_DESCRIPTION_LINE_WIDTH
            )
            + "\n"
        )
        # Populate table
        for parameter in parameters:
            params_table += f"{parameter['title']:{max_title_length}}{parameter['type']:{INPUT_TYPE_COLUMN_WIDTH}}"
            params_table += optional_column(
                parameter, "min", INPUT_MIN_MAX_COLUMN_WIDTH
            )
            params_table += optional_column(
                parameter, "max", INPUT_MIN_MAX_COLUMN_WIDTH
            )
            params_table += optional_column(parameter, "default", max_default_length)
            params_table += f"{parameter['desc']}\n"
        return params_table

    def format_dataslots(self) -> Optional[str]:
        """Formats input data slots to print in a clear way"""
        if "dataslots" in self.inputs:
            dataslots = self.inputs["dataslots"]
            dataslots_list = ""
            for dataslot in dataslots:
                dataslots_list += "Name: " + dataslot["name"] + "\n"
                dataslots_list += "Path in container: " + dataslot["path"] + "\n"
                dataslots_list += "Required: {}\n".format(dataslot["required"])
                dataslots_list += "Default Datasets: \n"
                for default in dataslot["default"]:
                    # TODO print name using API call to databases
                    dataslots_list += "Name: "
                    dataslots_list += f'ID: {default["uid"]}     '
                    dataslots_list += f'Version ID: {default["uid"]}     '
                dataslots_list += "\n"
            return dataslots_list
        else:
            return None

    def format_outputs(self) -> str:
        """Formats output files into a string which prints as a table"""
        names = [output["name"] for output in self.outputs["datasets"]] + ["Name"]
        max_name_length = len(max(names, key=len)) + 2
        outputs_table = (
            f"{OUTPUT_NAME_HEADER:{max_name_length}}"
            f"{OUTPUT_FORMAT_HEADER:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            f"{OUTPUT_SUMMARY_HEADER}\n"
            + f"-"
            * (
                max_name_length
                + OUTPUT_FORMAT_COLUMN_WIDTH
                + OUTPUT_SUMMARY_COLUMN_WIDTH
            )
            + "\n"
        )
        for dataset in self.outputs["datasets"]:
            outputs_table += f"{dataset['name']:{max_name_length}}{dataset['type']:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            outputs_table += optional_column(dataset, "description")
            outputs_table += "\n"
        return outputs_table
