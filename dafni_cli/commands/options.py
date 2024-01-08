from datetime import datetime

import click

from dafni_cli.consts import DATE_INPUT_FORMAT, DATE_INPUT_FORMAT_VERBOSE
from dafni_cli.datasets.dataset_metadata import (
    DATASET_METADATA_LANGUAGES,
    DATASET_METADATA_SUBJECTS,
    DATASET_METADATA_THEMES,
    DATASET_METADATA_UPDATE_FREQUENCIES,
)
from dafni_cli.utils import is_valid_email_address, is_valid_url


class URLParamType(click.ParamType):
    """URL parameter type for Click that checks if a string is a valid URL"""

    name = "url"

    def __init__(self, optional: bool = False):
        """
        Args:
            optional (bool): Whether an empty string should be accepted as
                             valid or not
        """
        self.optional = optional

    def convert(self, value, param, ctx):
        # Allow an empty string if optional is True, otherwise require the
        # URL to be valid
        if value == "":
            if self.optional:
                return value
            else:
                self.fail("Value cannot be an empty string")
        if is_valid_url(value):
            return value
        self.fail(f"'{value}' is not a valid URL")


def click_optional_tuple_none_callback(ctx, param, value):
    """By default click returns an empty tuple instead of None for options with
    multiple=True, this ensures None is returned instead for consistency

    To use supply callback=click_optional_tuple_none_callback to click.option
    """
    return None if len(value) == 0 else value


class EmailAddressParamType(click.ParamType):
    """Email address parameter type for Click that checks if a string is a
    valid email address"""

    name = "email_address"

    def convert(self, value, param, ctx):
        # Allow an empty string if optional is True, otherwise require the URL to be valid
        if is_valid_email_address(value):
            return value
        self.fail(f"'{value}' is not a valid email address")


def dataset_metadata_common_options(all_optional: bool):
    """Decorator function containing various optional arguments for modifying
    or creating dataset metadata

    Args:
        all_optional: Whether all arguments should be optional (used for
                      updating metadata rather than creating it)

    Here is a full list of the options that are added (all listed as not
    Optional are required unless all_optional=True)

        title (str): Dataset title
        description (str): Dataset description
        identifier (Optional[Tuple[str]]): Dataset identifiers
        subject (str): Dataset subject (One of DATASET_METADATA_SUBJECTS)
        theme (Optional[Tuple[str]]): Dataset themes (One of
                                      DATASET_METADATA_THEMES)
        language (str): Dataset language, one of DATASET_METADATA_LANGUAGES
        keywords (Tuple[str]): Dataset keywords used for data searches
        standard (Optional[Tuple[str, str]]): Dataset standard consisting of
                                a name and URL
        start_date (Optional[datetime]): Dataset start date
        end_date (Optional[datetime]): Dataset end date
        organisation (Tuple[str, str]): Name and URL of the organisation that
                                created the dataset
        person (Optional[Tuple[Tuple[str, str]]]): Name and ID of a person
                                involved in the creation of the dataset
        created_date (Optional[datetime]): Dataset creation date
        update_frequency (Optional[str]): Dataset update frequency, one of
                                DATASET_METADATA_UPDATE_FREQUENCIES
        publisher (Optional[Tuple[str, str]]): Dataset publisher name and ID
        contact (Optional[Tuple[str, str]]): Dataset contact point name
                                and email address
        license (str): URL to a license that applies to the dataset
        rights (Optional[str]): Description of any usage rights, restrictions
                                or citations required by users of the dataset
        version_message (str): Version message
    """

    # Arguments that will be used to indicate something as required
    # Will use the default required = False and have a default of None in the
    # case all_optional is True
    required_args = {"required": True}
    if all_optional:
        required_args = {"default": None}
    required_args_tuple = {
        **required_args,
        "callback": click_optional_tuple_none_callback,
    }

    def decorator(function):
        function = click.option(
            "--title",
            type=str,
            **required_args,
            help="Title of the dataset",
        )(function)
        function = click.option(
            "--description",
            type=str,
            **required_args,
            help="Description of the dataset",
        )(function)
        function = click.option(
            "--identifier",
            type=str,
            callback=click_optional_tuple_none_callback,
            multiple=True,
            help="Permanent URL of external identifier for this dataset (e.g. DOI). (Can have multiple)",
        )(function)
        function = click.option(
            "--subject",
            type=click.Choice(DATASET_METADATA_SUBJECTS),
            **required_args,
            help="Subject, one of those found at https://inspire.ec.europa.eu/metadata-codelist/TopicCategory",
        )(function)
        function = click.option(
            "--theme",
            type=click.Choice(DATASET_METADATA_THEMES),
            callback=click_optional_tuple_none_callback,
            multiple=True,
            help="Theme, one of those found at https://inspire.ec.europa.eu/Themes/Data-Specifications/2892. Can have multiple.",
        )(function)
        function = click.option(
            "--language",
            type=click.Choice(DATASET_METADATA_LANGUAGES),
            **required_args,
            help="Language",
        )(function)
        function = click.option(
            "--keyword",
            type=str,
            **required_args_tuple,
            multiple=True,
            help="Keyword used in data searches (Can have multiple)",
        )(function)
        function = click.option(
            "--standard",
            type=(str, URLParamType(optional=True)),
            default=None,
            help='Name and URL of a standard to which this dataset conforms (e.g. www.iso.org/standard/39229.html). Either value may be empty using "".',
        )(function)
        function = click.option(
            "--start-date",
            default=None,
            help=f"Start date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
            type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
        )(function)
        function = click.option(
            "--end-date",
            default=None,
            help=f"End date. Format: {DATE_INPUT_FORMAT_VERBOSE}",
            type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
        )(function)
        function = click.option(
            "--organisation",
            type=(str, URLParamType()),
            **required_args,
            help="Name and ID of the organisation that created the dataset. The ID must be a valid URL and can be a ror.org id, Companies House id or similar.",
        )(function)
        function = click.option(
            "--person",
            type=(str, URLParamType(optional=True)),
            callback=click_optional_tuple_none_callback,
            multiple=True,
            help='Name and ID of a person who created the dataset. Either value may be empty using "". When given the ID must be a valid URL, and can be an ORCID id or similar. (Can have multiple)',
        )(function)
        function = click.option(
            "--created-date",
            default=None if all_optional else datetime.now(),
            help=f"Created date. Format: {DATE_INPUT_FORMAT_VERBOSE}. Default: Today.",
            type=click.DateTime(formats=[DATE_INPUT_FORMAT]),
        )(function)
        function = click.option(
            "--update-frequency",
            type=click.Choice(DATASET_METADATA_UPDATE_FREQUENCIES),
            default=None,
            help="Update frequency.",
        )(function)
        function = click.option(
            "--publisher",
            type=(str, URLParamType(optional=True)),
            default=None,
            help='Publishing organisation name and ID. Either value may be empty using "". When given the ID must be a valid URL, and can be an ORCID id or similar.',
        )(function)
        function = click.option(
            "--contact",
            type=(str, EmailAddressParamType()),
            **required_args,
            help="Name and email address of the point of contact for queries about the dataset.",
        )(function)
        function = click.option(
            "--license",
            type=URLParamType(),
            default=None
            if all_optional
            else "https://creativecommons.org/licenses/by/4.0/",
            help="Permanent URL of an applicable license. Default: https://creativecommons.org/licenses/by/4.0/.",
        )(function)
        function = click.option(
            "--rights",
            type=str,
            default=None,
            help="Details of any usage rights, restrictions or citations required by users of the dataset.",
        )(function)
        function = click.option(
            "--version-message",
            "-m",
            type=str,
            **required_args,
            help="Version message to replace in any existing or provided metadata.",
        )(function)

        return function

    return decorator


def filter_flag_option(*param_decls: str, help: str):
    """Decorator function for constructing a click option that acts as
    a flag for filtering

    Args:
        *param_decls (str): See click.option
        help (str): Help text to pass to click.option
    """

    def decorator(function):
        function = click.option(
            *param_decls,
            is_flag=True,
            default=False,
            help=help,
            type=bool,
        )(function)

        return function

    return decorator


def json_option(function):
    """Decorator function for adding a --json click option for printing
    json output

    Flag will be named --json/--pretty and will be True or False
    """
    function = click.option(
        "--json/--pretty",
        "-j/-p",
        default=False,
        help="Prints raw json returned from API. Default: -p",
        type=bool,
    )(function)

    return function


def confirmation_skip_option(function):
    """Decorator function for adding a -y click option for skipping
    any confirmation prompts

    Flag will be named 'yes' and will be True or False
    """
    function = click.option(
        "--yes",
        "-y",
        is_flag=True,
        default=False,
        help="Flag for skipping any confirmation prompts",
    )(function)

    return function
