import click
import datetime as dt
from dateutil import parser

from dafni_cli.API_requests import get_models_dicts, get_single_model_dict, get_model_metadata_dicts
from dafni_cli.login import DATE_TIME_FORMAT, login


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

    def output_model_details(self):
        """Prints relevant model attributes to command line"""
        click.echo("Name: " + self.display_name +
                   "     ID: " + self.version_id +
                   "     Date: " + self.creation_time.date().strftime(DATE_TIME_FORMAT))
        click.echo("Summary: " + self.summary)

    def output_model_metadata(self, ctx, model_version_id: str):
        """Displays the metadata for the model.

        Args:
            ctx (context): contains JWT for authentication
            model_version_id (str): Version ID for the model to display the metadata of
        """
        # TODO Implement this
        pass


def create_model_list(model_dict_list: list) -> list:
    model_list = []
    for model_dict in model_dict_list:
        single_model = Model()
        single_model.get_details_from_dict(model_dict)
        model_list.append(single_model)
    return model_list


if __name__ == "__main__":
    jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJsb2dpbi1hcHAtand0IiwiZXhwIjoxNjE0OTY3ODQ4LCJzdWIiOiI4ZDg1N2FjZi0yNjRmLTQ5Y2QtOWU3Zi0xZTlmZmQzY2U2N2EifQ.UxB_67FpglFaJR2pBlVw_mIJY2zQ5y6cNEG5ZRmW8WA"
    version_id = "0b4b0d0a-5b05-4e14-b382-9a5c9082315b"
    model = Model()
    model.get_details_from_id(jwt, version_id)
    model.output_model_details()