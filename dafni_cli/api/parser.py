from dataclasses import dataclass
from typing import Callable, ClassVar, List, Optional, Union

from dateutil.parser import isoparse


@dataclass
class ParserParam:
    """Dataclass for storing information about a parameter to be assigned from
       a dictionary using ParserBaseObject's 'parse_from_dict' function

    In general this is used to define how to map a parameter from a dictionary
    to a class instance using its name in the object it will be parsed to, the
    name in the dictionary and a parameter determining how the data will be
    interpreted.

    Args:
        name (str): Name of the parameter in the dataclass type being parsed.
                    This is what will be assigned by the parser.
        keys (str or List[str]): Key(s) for accessing the parameter from its
                                 dictionary form. When multiple keys are given
                                 as a list it is assumed they are nested.
        parser (type, function or None): The effect depends on the type of
                                         this parameter:

            type:  The __init__ function will be called by the parser using data
                   found with the given key(s). E.g. str => str(data).

                   If the type is a subclass of ParserBaseObject then the parser
                   will parse and return this object assuming the data at the
                   given key is a dictionary itself or in the case the data is
                   a list, then a list of dictionaries representing this type.
            function: The function will be applied on the data e.g.
                      parse_datetime => parse_datetime(data)
            None: When None it is assumed no processing should be applied e.g.
                  for the parameter is known to be a list of strings.
    """

    name: str
    keys: Union[str, List[str]]
    datatype: Optional[Union[type, callable]] = None


class ParserBaseObject:
    """Base class for an object to be parsed from a dictionary using descriptions
    of how they map onto class parameters.

    Dataclasses that will be parsed from a dictionary should inherit from this
    and assign '_parser_params'. Any values that are Optional and are not
    necessarily assigned by the dict should be assigned with defaults in the
    dataclass.

    Attributes:
        _dict: Dictionary representation used to construct this object (useful
               for outputs with --json options)
        _parser_params (List[ParserParam]): List of ParserParam structures -
                                Each describes how to parse a dictionary to
                                the subclass inheriting from this. This is
                                a ClassVar as we do not want to assign it
                                every time an instance is created.
                                See ParserParams for more information/
    """

    _dict: dict = {}
    _parser_params: ClassVar[List[ParserParam]] = []

    @staticmethod
    def parse_from_dict(dataclass_type: type, dictionary: dict):
        """
        Parses a dictionary to a subclass inheriting from ParserBaseObject
        using its assigned _parser_params.

        Generally this function goes through each _parser_param in turn and
        assigning the attributes in the returned 'dataclass_type' instance
        by applying them as described in the docstring for ParserParam. If
        a particular ParserParam type inherits from ParserBaseObject and
        the corresponding dictionary data is a list, it will be assumed that
        each element in that list should be parsed to the type.

        Any default values in the dataclass will be used if either the key
        for a particular ParserParam is not found in the dictionary, or its
        found and the value parsed by it is None.
        If any variables in the dataclass do not have default values and are
        not found in the dictionary this will give an error.

        Args:
            dataclass_type (Type[ParserBaseObject]): Dataclass type to parse
                                                     the dictionary to
            dictionary (dict): Dictionary containing the data to be parsed

        Raises:
            TypeError: If a parameter is missing either in _parsed_params or
                       if it is found to be None after parsing and the
                       corresponding attribute in the 'dataclass_type' does
                       not have a default value assigned.
        """

        # To construct the dataclass - we want a dictionary containing all
        # of the parsed parameters
        parsed_params = {}

        # Each ParserParam equates to one attribute in the dataclass
        for param in dataclass_type._parser_params:
            # When keys is a list, we assume there is nesting of the
            # dictionary and get the nested value
            if isinstance(param.keys, list):
                parsed_param = dictionary
                for key in param.keys:
                    parsed_param = parsed_param.get(key)
                    if parsed_param is None:
                        break
            else:
                # No nesting
                parsed_param = dictionary.get(param.keys)

            # Only assign the value in parsed_params if it the value
            # is not None - this allows defaults defined in the dataclass
            # to take effect if the key was either not found in the dictionary
            # or if the value parsed from the dictionary itself is None
            if parsed_param is not None:
                # Here we parse the value of the parameter (unless the
                # datatype is None in which case we leave it as is)
                if param.datatype is not None:
                    # Recursive parse if the datatype is also a subclass
                    if isinstance(param.datatype, type) and issubclass(
                        param.datatype, ParserBaseObject
                    ):
                        # Automatically parse lists to lists of structures
                        if isinstance(parsed_param, list):
                            parsed_param = ParserBaseObject.parse_from_dict_list(
                                param.datatype, parsed_param
                            )
                        else:
                            parsed_param = ParserBaseObject.parse_from_dict(
                                param.datatype, parsed_param
                            )
                    else:
                        # Apply any constructor/function as required
                        parsed_param = param.datatype(parsed_param)

                parsed_params[param.name] = parsed_param

        # Convert to the dataclass type
        try:
            parsed_obj = dataclass_type(**parsed_params)
            parsed_obj._dict = dictionary
            return parsed_obj
        except TypeError as err:
            # Slightly more descriptive error message
            raise TypeError(
                f"At least one class attribute in '{dataclass_type.__name__}' "
                "was either missing from the dictionary or was parsed to be "
                "'None' but doesn't have a default value."
            ) from err

    @staticmethod
    def parse_from_dict_list(dataclass_type: type, dictionaries: List[dict]) -> List:
        """Parses a list of dictionaries to a list of objects

        Args:
            dataclass_type (Type[ParserBaseObject]): Dataclass type to parse
                                                     the dictionary to
            dictionaries (dict): List of dictionaries containing the data to
                                 be parsed
        """
        return [
            ParserBaseObject.parse_from_dict(dataclass_type, dictionary)
            for dictionary in dictionaries
        ]

    @property
    def dictionary(self):
        """Returns the dictionary used to assign the parameters in this object"""
        return self._dict


# Below follows some utility functions for parsing types


def parse_datetime(value: str):
    """Converts a datetime string to a datetime object using isoparse"""
    return isoparse(value)


def parse_dict_retaining_keys(dataclass_type: type) -> Callable[[dict], dict]:
    """Returns a function that converts the values inside a dictionary to a
    given dataclass type while retaining the same keys
    """

    return lambda dictionary: {
        key: ParserBaseObject.parse_from_dict(
            dataclass_type=dataclass_type, dictionary=value
        )
        for key, value in dictionary.items()
    }
