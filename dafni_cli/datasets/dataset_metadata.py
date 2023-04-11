from io import BytesIO
from typing import List, Optional, Tuple

import click

from dafni_cli.api.minio_api import minio_get_request
from dafni_cli.consts import CONSOLE_WIDTH, DATA_FORMATS, TAB_SPACE
from dafni_cli.utils import (check_key_in_dict, output_table,
                             process_dict_datetime, process_file_size,
                             prose_print)


class DataFile:
    """Class to represent the DAFNI Dataset File
    client model

    Methods:
        __init__(): DataFile constructor

    Attributes:
        name (str): File Name
        size (str): File Size
        format (str): File Format
        download (str): File Download URL
        contents (BytesIO): Downloaded File Contents
    """

    def __init__(self, file_dict: Optional[dict] = None):
        """DataFile Constructor

        Args:
            file_dict (Optional[dict], optional): DataFile Client model to map. Defaults to None.
        """
        self.name = None
        self.size = None
        self.format = None
        self.download = None
        self.contents = None

        if file_dict:
            self.set_attributes_from_dict(file_dict)

    def set_attributes_from_dict(self, file_dict: dict):
        """Function to set the DataFile attributes based on a given
        Dataset metadata client model

        Args:
            file_dict (dict): [description]
        """
        self.name = check_key_in_dict(file_dict, ["spdx:fileName"])
        self.size = process_file_size(
            check_key_in_dict(file_dict, ["dcat:byteSize"], default=None)
        )
        self.format = DATA_FORMATS.get(
            check_key_in_dict(file_dict, ["dcat:mediaType"]), ""
        )
        self.download = check_key_in_dict(file_dict, ["dcat:downloadURL"], default=None)

    def download_contents(self, jwt: str):
        """Function downloads the file using the download url,
        and saves the contents as a BytesIO object to self.contents

        Args:
            jwt (str): Users JWT
        """
        self.contents = BytesIO(minio_get_request(self.download, jwt, content=True))


class DatasetMetadata:
    """Class to represent the DAFNI Dataset
    Metadata client model

    Methods:
        __init__(): DatasetMetadata constructor
        set_attributes_from_dict(jwt (str), dataset (dict)): Sets the dataset metadata attributes from given client model dict
        output_metadata_details(): Prints key information of the dataset metadata to console.
        output_datafiles_table(): Prints a table to the console of all File related information
        output_metadata_extra_details(): Prints extra details relating to the Dataset Metadata

    Attributes:
        created (str): Date the dataset was created
        creator (str): Creator of the dataset
        contact (str): Contact relating to the dataset
        description (str): Description of the dataset
        identifier (str): List of identifiers relating to the dataset
        location (str): Location the Dataset relates to
        start_date (str): Dataset start date if applicable
        end_date (str): Dataset end date if applicable
        files (List[DataFile]): Files associated with the dataset
        keywords (List[str]): Key words relating to the dataset e.g. Transportation
        themes (List[str]): Themes relating to dataset
        publisher (str): Entity responsible for publishing the dataset
        issued (str): Date the dataset was issued
        rights (str): The user rights linked to the Dataset
        language (str): The langauge used for the dataset
        standard (str): Any related standards associated
        update (str): Update Frequency
    """

    def __init__(self, dataset_dict: Optional[dict] = None):
        """DatasetMetadata constructor"""
        self.created = None
        self.creator = None
        self.contact = None
        self.description = None
        self.identifier = None
        self.location = None
        self.start_date = None
        self.end_date = None
        self.files = []
        self.keywords = []
        self.themes = None
        self.publisher = None
        self.issued = None
        self.rights = None
        self.language = None
        self.standard = None
        self.update = None
        self.title = None
        self.dataset_id = None
        self.version_id = None

        if dataset_dict:
            self.set_attributes_from_dict(dataset_dict)

    def set_attributes_from_dict(self, dataset_dict: dict):
        """Helper function to populate the DatasetMetadata details
        based on a given DAFNI Dataset metadata client model

        Args:
            dataset_dict (dict): DAFNI Dataset metadata client model
        """
        # Standard Metadata
        self.created = process_dict_datetime(dataset_dict, ["dct:created"])
        if check_key_in_dict(dataset_dict, ["dct:creator"], default=None):
            self.creator = dataset_dict["dct:creator"][0]["foaf:name"]
        self.contact = check_key_in_dict(
            dataset_dict, ["dcat:contactPoint", "vcard:hasEmail"]
        )
        self.description = check_key_in_dict(dataset_dict, ["dct:description"])
        self.identifier = check_key_in_dict(dataset_dict, ["dct:identifier"])
        self.location = check_key_in_dict(dataset_dict, ["dct:spatial", "rdfs:label"])
        self.start_date = process_dict_datetime(
            dataset_dict, ["dct:PeriodOfTime", "time:hasBeginning"]
        )
        self.end_date = process_dict_datetime(
            dataset_dict, ["dct:PeriodOfTime", "time:hasEnd"]
        )
        self.keywords = check_key_in_dict(dataset_dict, ["dcat:keyword"])

        # Process Files
        if check_key_in_dict(dataset_dict, ["dcat:distribution"], default=None):
            self.files = [
                DataFile(file_dict) for file_dict in dataset_dict["dcat:distribution"]
            ]

        # Additional Metadata fields
        self.themes = check_key_in_dict(dataset_dict, ["dcat:theme"])
        self.publisher = check_key_in_dict(dataset_dict, ["dct:publisher", "foaf:name"])
        self.issued = process_dict_datetime(dataset_dict, ["dct:issued"])
        self.rights = check_key_in_dict(dataset_dict, ["dct:rights"])
        self.language = check_key_in_dict(dataset_dict, ["dct:language"])
        self.standard = check_key_in_dict(dataset_dict, ["dct:conformsTo", "label"])
        self.update = check_key_in_dict(dataset_dict, ["dct:accrualPeriodicity"])

        # Version History Fields
        self.dataset_id = check_key_in_dict(dataset_dict, ["@id", "dataset_uuid"])
        self.title = check_key_in_dict(dataset_dict, ["dct:title"])
        self.version_id = check_key_in_dict(dataset_dict, ["@id", "version_uuid"])

    def output_metadata_details(self, long: bool = False):
        """Function to output details relating to the Dataset.
        The default behavior is to print all standard metadata and
        a table relating to the associated files.
        If the long option is given, the additional metadata fields are
        also printed to the console

        Args:
            long (bool, optional): Flag to print additional metadata. Defaults to False.
        """
        click.echo(f"\nCreated: {self.created}")
        click.echo(f"Creator: {self.creator}")
        click.echo(f"Contact: {self.contact}")
        click.echo("Description:")
        prose_print(self.description, CONSOLE_WIDTH)
        click.echo("Identifier: ")
        prose_print(" ".join(self.identifier), CONSOLE_WIDTH)
        click.echo(f"Location: {self.location}")
        click.echo(f"Start date: {self.start_date}")
        click.echo(f"End date: {self.end_date}")
        click.echo(f"Key Words:\n {self.keywords}")

        # DataFiles table
        self.output_datafiles_table()

        if long:
            self.output_metadata_extra_details()

    def output_datafiles_table(self):
        """Function to print the datafiles table to the console
        for all associated files
        """
        click.echo("\nData Files")
        # Setup table data
        columns = ["Name", "Size", "Format"]
        name_width = max([len(datafile.name) for datafile in self.files])
        widths = [name_width, 10, 6]
        rows = [
            [datafile.name, datafile.size, datafile.format] for datafile in self.files
        ]
        # Print table to console
        click.echo(output_table(columns, widths, rows))

    def output_metadata_extra_details(self):
        """Function to print additional metadata to the
        console relating to the dataset
        """
        click.echo(f"Themes:\n{self.themes}")
        click.echo(f"Publisher: {self.publisher}")
        click.echo(f"Issued: {self.issued}")
        click.echo("Rights:")
        prose_print(self.rights, CONSOLE_WIDTH)
        click.echo(f"Language: {self.language}")
        click.echo(f"Standard: {self.standard}")
        click.echo(f"Update Frequency: {self.update}")

    def output_version_details(self):
        """Prints relevant dataset attributes to command line"""
        click.echo(f"\nTitle: {self.title}")
        click.echo(f"ID: {self.dataset_id}")
        click.echo(f"Version ID: {self.version_id}")
        click.echo(f"Publisher: {self.publisher}")
        click.echo(f"From: {self.start_date}{TAB_SPACE}To: {self.end_date}")
        click.echo("Description: ")
        prose_print(self.description, CONSOLE_WIDTH)

    def download_dataset_files(self, jwt: str) -> Tuple[List[str], List[BytesIO]]:
        """Function downloads all associated Files, and returns a tuple with
        containing a list of all file names, and a list of all file contents

        Args:
            jwt (str): Users JWT

        Returns:
            Tuple[List[str], List[BytesIO]]: Tuple of all File names and File contents
        """
        file_names = []
        file_contents = []
        for data_file in self.files:
            data_file.download_contents(jwt)
            file_names.append(data_file.name)
            file_contents.append(data_file.contents)

        return file_names, file_contents
