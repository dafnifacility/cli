import json
import textwrap
from datetime import datetime as dt
from io import BytesIO
from typing import List, Optional, Union
from zipfile import ZipFile

import click
from dateutil.parser import isoparse


def prose_print(prose: str, width: int):
    """
    Prints string as separate paragraphs with appropriate line breaks at specified line lengths
    Args:
        prose (str): string to print as prose
        width (int): width of the lines before a new line
    """
    for paragraph in prose.split("\n"):
        for line in textwrap.wrap(paragraph, width=width):
            click.echo(line)


def process_response_to_class_list(response: List[dict], class_instance: object):
    """
    Produces a list of objects of a specified class from a list of dictionaries obtained from the DAFNI API.

    Args:
        response (list[dict]): List of dictionaries returned from the DAFNI API.
        class_instance (object): Class to create a list of.

    Returns:
        class_list (list[object]): List of objects with the attributes populated from the dictionaries.
    """
    class_list = []
    for class_dict in response:
        instance = class_instance()
        instance.set_attributes_from_dict(class_dict)
        class_list.append(instance)
    return class_list


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
        entry_string = str(dictionary[key])
        if column_width > 0:
            entry = f"{entry_string:{alignment}{column_width}}"
        elif column_width == 0:
            entry = entry_string
        else:
            raise ValueError("Column width for optional column must be non-negative")
    else:
        entry = " " * column_width
    return entry


def process_date_filter(date_str: str) -> str:
    """Function to take a date str used for filtering on date
    and process into a format to submit to the DAFNI API's

    Args:
        date_str (str): Date Str in format dd/mm/yyyy

    Returns:
        str: Processed date str to YYYY-MM-DDT00:00:00
    """
    # TODO use this datetime format (ISO8601) and use as a constant here
    return dt.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S")


# TODO remove this whole function and use dict.get(key, default)
def check_key_in_dict(
    input_dict: dict,
    keys: List[str],
    default: Optional[Union[str, int, dict, bool]] = "N/A",
) -> Optional[Union[str, int, dict, bool]]:
    """Utility function to check a nested dict for a given
    key and nested keys if applicable. If the keys exist, the
    associated value is returned, otherwise the default value is returned.

    Args:
        input_dict (dict): dict to check in for keys
        keys (List[str]): keys to check for, with nested keys being subsequent elements of the list
        default (Union[str, int, dict, bool], optional): default value if key(s) not found. Defaults to "N/A".

    Returns:
        Union[str, int, dict, bool], optional: Value associated with given dict and key(s)
    """
    _element = None
    if isinstance(input_dict, dict):
        _element = input_dict
        for key in keys:
            try:
                _element = _element[key]
            except BaseException:
                return default

    if _element is not None:
        return _element
    return default


# TODO change to process_datetime
def process_dict_datetime(input_dict: dict, keys: List[str], default="N/A") -> str:
    """Utility function to check a nested dict for a given
    key and nested key if applicable. If the keys exist, the
    associated value is parsed to a datetime and then formatted to an
    applicable datetime string, otherwise the default value is returned.
    This function will only parse datetimes in the ISO date format

    Args:
        input_dict (dict): dict to check in for keys
        keys (List[str]): keys to check for
        nested_key (Optional[str], optional): A nested key to check for. Defaults to None.
        default (Optional[str], optional): default value if key(s) not found. Defaults to "N/A".

    Returns:
        str: Parsed datetime associated with given dict and key(s)
    """
    value = check_key_in_dict(input_dict, keys, None)
    if value:
        try:
            return isoparse(value).strftime("%B %d %Y")
        except ValueError:
            return value
    return default


def output_table_row(
    entries: List[str], widths: List[int], alignment: str = "<", header: bool = False
) -> str:
    """Function to generate a table row given values and column widths.
    If the header argument is set to true, a dashed line of equal length is added underneath.

    Args:
        entries (List[str]): Table Values
        widths (List[int]): Width associated with each column
        alignment (str, optional): Direction to align entry. Defaults to "<".
        header (bool): Flag to set if the given row is the table header. Defaults to False.

    Returns:
        str: String containing all entries with associated spacing and line breaks
    """
    table_items = [
        f"{value:{alignment}{widths[idx]}}" for idx, value in enumerate(entries)
    ]
    table_str = " ".join(table_items)
    table_str += "\n"

    if header:
        table_str += "-" * sum(widths, len(entries))
        table_str += "\n"

    return table_str


def output_table(
    columns: List[str], widths: List[int], values: List[List], alignment: str = "<"
) -> str:
    """Function to generate a table of data in the command console

    Args:
        columns (List[str]): Column names
        widths (List[int]): Column widths, where values are > 0
        values (List[List]): List of rows to display in table
        alignment (str, optional): Alignment option for table contents. Defaults to "<".

    Returns:
        str: Table str with required spacing and line breaks for console
    """
    table_str = output_table_row(columns, widths, alignment, header=True)
    rows = [output_table_row(row, widths, alignment) for row in values]
    table_str += "".join(rows)

    return table_str


def process_file_size(file_size: str) -> str:
    """Utility function to take in a file size in bytes
    and format into a table ready format.
    This converts the size into appropriate units, with
    the units appended

    Args:
        file_size (str): File size in bytes

    Returns:
        str: Converted file size with applicable units
    """
    try:
        file_size = float(file_size)
    except BaseException:
        return ""

    if file_size < 1e3:
        return f"{file_size} B"
    elif file_size >= 1e3 and file_size < 1e6:
        size = round(file_size / 1e3, 1)
        return f"{size} KB"
    elif file_size >= 1e6 and file_size < 1e9:
        size = round(file_size / 1e6, 1)
        return f"{size} MB"
    else:
        size = round(file_size / 1e9, 1)
        return f"{size} GB"


def argument_confirmation(
    argument_names: List[str],
    arguments: List[str],
    confirmation_message: str,
    additional_messages: Optional[List[str]] = None,
):
    """Function to display the arguments and options chosen by the user
    and ask for confirmation

    Args:
        argument_names (List[str]): List of the names of the arguments/options for the command
        arguments (List[str]): List of values chosen for each corresponding argument/option
        confirmation_message (str): String to display after arguments which prompts the user to confirm or reject
        additional_messages (Optional[List[str]]): Other messages to be added after options are listed
    """
    for i, value in enumerate(argument_names):
        click.echo(f"{value}: {arguments[i]}")
    if additional_messages:
        for message in additional_messages:
            click.echo(message)
    click.confirm(confirmation_message, abort=True)


def write_files_to_zip(
    zip_path: str, file_names: List[str], file_contents: List[BytesIO]
) -> None:
    """Function to compress a list of files to a zip folder, and write to disk

    Args:
        zip_path (str): Full path including file name to write to
        file_names (List[str]): List of all file names
        file_contents (List[BytesIO]): List of file contents, 1 for each name
    """
    with ZipFile(zip_path, "w") as zipObj:
        for idx, file_name in enumerate(file_names):
            with zipObj.open(file_name, "w") as zip_file:
                zip_file.write(file_contents[idx].getvalue())


def print_json(response: Union[dict, List[dict]]) -> None:
    """Takes dictionary or list of dictionary and pretty prints to command line

    Args:
        response (Union[dict, List[dict]]): Dictionary or list of dictionaries to pretty print
    """
    click.echo(json.dumps(response, indent=2, sort_keys=True))
