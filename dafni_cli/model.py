import click
import datetime as dt
from dateutil import parser
import json
import textwrap

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
    INPUT_DESCRIPTION_LINE_WIDTH


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
        click.echo(json.dumps(metadata_dict, indent=2))
        self.name = metadata_dict['metadata']['name']
        self.owner = metadata_dict['metadata']['owner']
        self.inputs = metadata_dict['spec']['inputs']
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

    def output_inputs(self) -> str:
        # Parameters
        parameters = self.inputs['env']
        titles = [parameter['title'] for parameter in parameters] + ["title"]
        defaults = [str(parameter['default']) for parameter in parameters] + ["default"]
        max_title_length = len(max(titles, key=len)) + 2
        max_default_length = len(max(defaults, key=len)) + 2
        inputs = f"{INPUT_TITLE_HEADER:{max_title_length}}" \
                 f" {INPUT_TYPE_HEADER:{INPUT_TYPE_COLUMN_WIDTH}}" \
                 f" {INPUT_MIN_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}" \
                 f" {INPUT_MAX_HEADER:{INPUT_MIN_MAX_COLUMN_WIDTH}}" \
                 f" {INPUT_DEFAULT_HEADER:{max_default_length}}" \
                 f" {INPUT_DESCRIPTION_HEADER}\n" \
                 + f"-" * (max_title_length +
                           INPUT_TYPE_COLUMN_WIDTH +
                           2 * INPUT_MIN_MAX_COLUMN_WIDTH +
                           max_default_length +
                           INPUT_DESCRIPTION_LINE_WIDTH) \
                 + "\n"
        for parameter in parameters:
            inputs += f"{parameter['title']:{max_title_length}} {parameter['type']:{INPUT_TYPE_COLUMN_WIDTH}} "
            if "min" in parameter and "max" in parameter:
                inputs += f"{parameter['min']:<{INPUT_MIN_MAX_COLUMN_WIDTH}} " \
                          f"{parameter['max']:<{INPUT_MIN_MAX_COLUMN_WIDTH}} "
            else:
                inputs += f" " * (INPUT_MIN_MAX_COLUMN_WIDTH + 1) * 2
            inputs += f"{parameter['default']:<{max_default_length}}" \
                      f"{parameter['desc']}\n"
        return inputs

    def output_model_details(self):
        """Prints relevant model attributes to command line"""
        click.echo("Name: " + self.display_name +
                   "     ID: " + self.version_id +
                   "     Date: " + self.creation_time.date().strftime(DATE_TIME_FORMAT))
        click.echo("Summary: " + self.summary)

    def output_model_metadata(self):
        """Prints the metadata for the model to command line."""
        click.echo("Name: " + self.display_name)
        click.echo("Date: " + self.creation_time.strftime('%B %d %Y'))
        click.echo("Summary: ")
        click.echo(self.summary + "\n")
        click.echo("Description: ")
        for paragraph in self.description.split("\n"):
            for line in textwrap.wrap(paragraph, width=120):
                click.echo(line)
        click.echo("\nInputs: ")
        click.echo(self.output_inputs())
        click.echo("Outputs: ")
        click.echo(self.outputs)
        pass


def create_model_list(model_dict_list: list) -> list:
    model_list = []
    for model_dict in model_dict_list:
        single_model = Model()
        single_model.get_details_from_dict(model_dict)
        model_list.append(single_model)
    return model_list


if __name__ == "__main__":
    jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE1MjE3NjE3LCJzdWIiOiI4ZDg1N2FjZi0yNjRmLTQ5Y2QtOWU3Zi0xZTlmZmQzY2U2N2EifQ.gaiPaXQ8SkHFQwen4ujMQD1pbJEY9Md--cd1V1mai9A"
    version_id = "9de4ad50-fd98-4def-9bfc-39378854e6a1"
    model = Model()
    model.get_details_from_id(jwt, version_id)
    model.get_metadata(jwt)
    model.output_model_metadata()
