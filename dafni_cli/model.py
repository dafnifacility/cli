import click
import datetime as dt
from dateutil import parser
import json
import textwrap
from typing import Optional

from dafni_cli.API_requests import get_models_dicts, get_single_model_dict, get_model_metadata_dicts
from dafni_cli.login import DATE_TIME_FORMAT, login

from dafni_cli.consts import INPUT_TITLE_HEADER, \
    INPUT_TYPE_HEADER, \
    INPUT_MIN_HEADER, \
    INPUT_MAX_HEADER, \
    INPUT_DEFAULT_HEADER, \
    INPUT_DESCRIPTION_HEADER, \
    INPUT_TYPE_COLUMN_WIDTH, \
    INPUT_MIN_MAX_COLUMN_WIDTH, \
    INPUT_DESCRIPTION_LINE_WIDTH, \
    OUTPUT_NAME_HEADER, \
    OUTPUT_FORMAT_HEADER, \
    OUTPUT_SUMMARY_HEADER, \
    OUTPUT_FORMAT_COLUMN_WIDTH, \
    OUTPUT_SUMMARY_COLUMN_WIDTH, \
    CONSOLE_WIDTH


def optional_column(dictionary: dict, key: str, column_width: int = 0, alignment: str = "<"):
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
            raise Exception("Column width for optional column must be positive or zero")
    else:
        entry = f" " * column_width
    return entry


class Model:

    def __init__(self, identifier=None):
        self.version_id = identifier
        self.display_name = None
        self.summary = None
        self.description = None
        self.creation_time = None
        self.publication_time = None
        self.version_tags = None
        self.container = None
        self.name = None
        self.inputs = None
        self.outputs = None
        self.owner = None
        pass

    def get_details_from_dict(self, model_dict: dict):
        self.display_name = model_dict['name']
        self.summary = model_dict['summary']
        self.description = model_dict['description']
        self.creation_time = parser.isoparse(model_dict['creation_date'])
        self.publication_time = parser.isoparse(model_dict['publication_date'])
        self.version_id = model_dict['id']
        self.version_tags = model_dict['version_tags']
        self.container = model_dict['container']

    def get_details_from_id(self, jwt_string: str, version_id_string: str):
        model_dict = get_single_model_dict(jwt_string, version_id_string)
        self.get_details_from_dict(model_dict)

    def get_metadata(self, jwt_string: str):
        metadata_dict = get_model_metadata_dicts(jwt_string, self.version_id)
        self.name = metadata_dict['metadata']['name']
        self.owner = metadata_dict['metadata']['owner']
        if 'inputs' in metadata_dict['spec']:
            self.inputs = metadata_dict['spec']['inputs']
        if 'outputs' in metadata_dict['spec']:
            self.outputs = metadata_dict['spec']['outputs']

    def filter_by_date(self, key: str, date: str) -> bool:
        """Filters models based on the date given as an option.
            Args:
                key (str): Key for MODEL_DICT in which date is contained
                date (str): Date for which models are to be filtered on: format DD/MM/YYYY

            Returns:
                bool: Whether to display the model based on the filter
        """
        day, month, year = date.split("/")
        date = dt.date(int(year), int(month), int(day))
        if key == "creation":
            return self.creation_time.date() >= date
        elif key == "publication":
            return self.publication_time.date() >= date
        else:
            raise Exception("Key should be CREATION or PUBLICATION")

    def format_parameters(self) -> str:
        """Formats input parameters for the model into a string which prints as a table"""
        parameters = self.inputs['env']
        titles = [parameter['title'] for parameter in parameters] + ["title"]
        defaults = ["default"]
        for parameter in parameters:
            if 'default' in parameter:
                defaults.append('default')
        max_title_length = len(max(titles, key=len)) + 2
        max_default_length = len(max(defaults, key=len)) + 2
        # Setup headers
        params_table = f"{INPUT_TITLE_HEADER:{max_title_length}}" \
                       f"{INPUT_TYPE_HEADER:{INPUT_TYPE_COLUMN_WIDTH}}" \
                       f"{INPUT_MIN_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}" \
                       f"{INPUT_MAX_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}" \
                       f"{INPUT_DEFAULT_HEADER:{max_default_length}}" \
                       f"{INPUT_DESCRIPTION_HEADER}\n" \
                       + f"-" * (max_title_length +
                                 INPUT_TYPE_COLUMN_WIDTH +
                                 2 * INPUT_MIN_MAX_COLUMN_WIDTH +
                                 max_default_length +
                                 INPUT_DESCRIPTION_LINE_WIDTH) \
                       + "\n"
        # Populate table
        for parameter in parameters:
            params_table += f"{parameter['title']:{max_title_length}}{parameter['type']:{INPUT_TYPE_COLUMN_WIDTH}}"
            params_table += optional_column(parameter, "min", INPUT_MIN_MAX_COLUMN_WIDTH)
            params_table += optional_column(parameter, "max", INPUT_MIN_MAX_COLUMN_WIDTH)
            params_table += optional_column(parameter, "default", max_default_length)
            params_table += f"{parameter['desc']}\n"
        return params_table

    def format_dataslots(self) -> Optional[str]:
        """Formats input data slots to print in a clear way"""
        if 'dataslots' in self.inputs:
            dataslots = self.inputs['dataslots']
            dataslots_list = ''
            for dataslot in dataslots:
                dataslots_list += 'Name: ' + dataslot['name'] + '\n'
                dataslots_list += 'Path in container: ' + dataslot['path'] + '\n'
                dataslots_list += 'Required: {}\n'.format(dataslot['required'])
                dataslots_list += 'Default Datasets: \n'
                for default in dataslot['default']:
                    # TODO print name using API call to databases
                    dataslots_list += 'Name: '
                    dataslots_list += f'ID: {default["uid"]}     '
                    dataslots_list += f'Version ID: {default["uid"]}     '
                dataslots_list += '\n'
            return dataslots_list
        else:
            return None

    def format_outputs(self) -> str:
        """Formats output files into a string which prints as a table"""
        names = [output['name'] for output in self.outputs['datasets']] + ["Name"]
        max_name_length = len(max(names, key=len)) + 2
        outputs_table = f"{OUTPUT_NAME_HEADER:{max_name_length}}" \
                        f"{OUTPUT_FORMAT_HEADER:{OUTPUT_FORMAT_COLUMN_WIDTH}}" \
                        f"{OUTPUT_SUMMARY_HEADER}\n" \
                        + f"-" * (max_name_length
                                  + OUTPUT_FORMAT_COLUMN_WIDTH
                                  + OUTPUT_SUMMARY_COLUMN_WIDTH) \
                        + "\n"
        for dataset in self.outputs['datasets']:
            outputs_table += f"{dataset['name']:{max_name_length}}{dataset['type']:{OUTPUT_FORMAT_COLUMN_WIDTH}}"
            outputs_table += optional_column(dataset, "description")
            outputs_table += '\n'
        return outputs_table

    def output_model_details(self):
        """Prints relevant model attributes to command line"""
        click.echo("Name: " + self.display_name +
                   "     ID: " + self.version_id +
                   "     Date: " + self.creation_time.date().strftime('%B %d %Y'))
        click.echo("Summary: " + self.summary)

    def output_model_metadata(self):
        """Prints the metadata for the model to command line."""
        click.echo("Name: " + self.display_name)
        click.echo("Date: " + self.creation_time.strftime('%B %d %Y'))
        click.echo("Summary: ")
        click.echo(self.summary)
        click.echo("Description: ")
        for paragraph in self.description.split("\n"):
            for line in textwrap.wrap(paragraph, width=CONSOLE_WIDTH):
                click.echo(line)
        click.echo("")
        if self.inputs:
            click.echo("Input Parameters: ")
            click.echo(self.format_parameters())
            click.echo("Input Data Slots: ")
            click.echo(self.format_dataslots())
        if self.outputs:
            click.echo("Outputs: ")
            click.echo(self.format_outputs())
        pass


def create_model_list(model_dict_list: list) -> list:
    model_list = []
    for model_dict in model_dict_list:
        single_model = Model()
        single_model.get_details_from_dict(model_dict)
        model_list.append(single_model)
    return model_list

if __name__ == "__main__":
    jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE1MzA5OTE2LCJzdWIiOiI4ZDg1N2FjZi0yNjRmLTQ5Y2QtOWU3Zi0xZTlmZmQzY2U2N2EifQ.QyniuWaDD0unfS9ydwvz9e0l_SamDLRg8a8fftooyl0"
    version_id = []
    #version_id.append("0b4b0d0a-5b05-4e14-b382-9a5c9082315b") # COVID
    #version_id.append("a2dc91ea-c243-4232-8d2e-f951fc5f8248") # Transform
    #version_id.append("d0942631-158c-4cd2-a75f-ec7ec5798381") # SIMIM
    version_id.append("399cdaac-aab6-494d-870a-66de8a4217bb") # Spatial Housing
    #version_id.append("ef4b22c8-63be-4b53-ba7c-c1cf301774b2") # Non-spatial Housing
    #version_id.append("9de4ad50-fd98-4def-9bfc-39378854e6a1") # 5G
    for id in version_id:
        model = Model()
        model.get_details_from_id(jwt, id)
        model.get_metadata(jwt)
        model.output_model_metadata()