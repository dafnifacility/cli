import click
import textwrap
from typing import List, Optional, Union
from datetime import datetime as dt
from dateutil.parser import isoparse
from dafni_cli.consts import DATA_FORMATS


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
        instance.set_details_from_dict(class_dict)
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
        entry = f" " * column_width
    return entry


def process_date_filter(date_str: str) -> str:
    """Function to take a date str used for filtering on date
    and process into a format to submit to the DAFNI API's

    Args:
        date_str (str): Date Str in format dd/mm/yyyy

    Returns:
        str: Processed date str tp YYYY-MM-DDT00:00:00
    """
    return dt.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S")


def check_key_in_dict(
    input_dict: dict,
    key: str,
    nested_key: Optional[str] = None,
    default: Optional[str] = "N/A",
) -> Optional[Union[str, int]]:
    """Utility function to check a nested dict for a given
    key and nested key if applicable. If the keys exist, the
    associated value is returned, otherwise the default value is returned.

    Args:
        input_dict (dict): dict to check in for keys
        key (str): first key to check for
        nested_key (Optional[str], optional): A nested key to check for. Defaults to None.
        default (Optional[str], optional): default value if key(s) not found. Defaults to "N/A".

    Returns:
        Optional[Union[str, int]]: Value associated with given dict and key(s)
    """
    value = None
    if isinstance(input_dict, dict):
        if key in input_dict:
            if nested_key and isinstance(input_dict[key], dict):
                if nested_key in input_dict[key]:
                    value = input_dict[key][nested_key]
            elif not nested_key:
                value = input_dict[key]
    if value is not None:
        return value
    return default


def process_dict_datetime(
    input_dict: dict, key: str, nested_key: Optional[str] = None, default="N/A"
) -> str:
    """Utility function to check a nested dict for a given
    key and nested key if applicable. If the keys exist, the
    associated value is parsed to a datetime and then formatted to an
    applicable datetime string, otherwise the default value is returned.

    Args:
        input_dict (dict): dict to check in for keys
        key (str): first key to check for
        nested_key (Optional[str], optional): A nested key to check for. Defaults to None.
        default (Optional[str], optional): default value if key(s) not found. Defaults to "N/A".

    Returns:
        str: Parsed datetime associated with given dict and key(s)
    """
    value = check_key_in_dict(input_dict, key, nested_key, None)
    if value:
        try:
            return isoparse(value).strftime("%B %d %Y")
        except ValueError:
            return value
    return default


def output_table_row(
    columns: List[str], widths: List[int], alignment: str = "<", header: bool = False
) -> str:
    """Function to generate a table header for the given keys,
    with a dashed line of equal length underneath

    Args:
        columns (List[str]): Table Columns
        widths (List[int]): Width associated with each column
        alignment (str, optional): Direction to align header. Defaults to "<".

    Returns:
        str: String containing all Headers with associated spacing and line breaks
    """
    table_items = [
        f"{column:{alignment}{widths[idx]}}" for idx, column in enumerate(columns)
    ]
    table_str = " ".join(table_items)
    table_str += "\n"

    if header:
        table_str += "-" * sum(widths, len(columns))
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


def process_file_size(file_size: Union[int, float]) -> str:
    """Utility function to take in a file size in bytes
    and format into a tale ready format.
    This converts the size into appropriate units, with
    the units appended

    Args:
        file_size (Union[int, float]): File size in bytes

    Returns:
        str: Converted file size with applicable units
    """
    if not isinstance(file_size, (int, float)):
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
