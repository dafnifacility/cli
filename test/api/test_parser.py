from dataclasses import dataclass
from typing import ClassVar, List, Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

from dafni_cli.api.parser import (
    ParserBaseObject,
    ParserParam,
    parse_datetime,
    parse_dict_retaining_keys,
)


@dataclass
class TestDataclassEmpty(ParserBaseObject):
    """Empty dataclass"""


@dataclass
class TestDataclass1(ParserBaseObject):
    """Dataclass for testing basic parsing with a type cast"""

    value1: str
    value2: str
    value3: list
    value4: dict

    _parser_params: ClassVar[List[ParserParam]] = [
        # Try casting value1 to a string
        ParserParam("value1", "value1", str),
        ParserParam("value2", "value2"),
        ParserParam("value3", "value3"),
        ParserParam("value4", "value4"),
    ]


@dataclass
class TestDataclass2(ParserBaseObject):
    """Dataclass for testing more complex parsing with a nested structure
    and a parsing function"""

    value1: int
    value2: str
    value3: list
    value4: dict

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("value1", "value1"),
        ParserParam("value2", "value2", lambda value: f"Date({value})"),
        ParserParam("value3", "value3"),
        ParserParam("value4", "value4", TestDataclass1),
    ]


@dataclass
class TestDataclassDefault(ParserBaseObject):
    """Dataclass for testing default values"""

    value1: str
    value2: Optional[str] = None

    _parser_params: ClassVar[List[ParserParam]] = [
        ParserParam("value1", "value1", str),
        ParserParam("value2", "value2", str),
    ]


TEST_DICT_DATA: dict = {
    "value1": 10,
    "value2": "24/04/2023",
    "value3": ["A", "list"],
    "value4": {
        "value1": "hello",
        "value2": "world",
        "value3": ["test1"],
        "value4": {"value": "test_value"},
    },
}

TEST_DICT_DATA2: dict = {
    "value1": 20,
    "value2": "24/01/2023",
    "value3": ["Another", "list"],
    "value4": [
        {
            "value1": "hello",
            "value2": "world",
            "value3": ["test1"],
            "value4": {"value": "test_value"},
        },
        {
            "value1": "something",
            "value2": "else",
            "value3": ["test2"],
            "value4": {"value": "test_value2"},
        },
    ],
}

TEST_DICT_DATA_LIST: List[dict] = [TEST_DICT_DATA, TEST_DICT_DATA2]


class TestParser(TestCase):
    """Tests the ParserBaseObject class and associated methods"""

    def test_parse_from_dict_ignores_unused_data(self):
        """Tests that parse_from_dict ignores any data not defined in the
        _parser_params"""
        parsed_obj = ParserBaseObject.parse_from_dict(
            TestDataclassEmpty, TEST_DICT_DATA
        )
        self.assertEqual(parsed_obj.__dict__, {"_dict": TEST_DICT_DATA})

    def test_parse_from_dict(self):
        """Tests that parse_from_dict parses basic data"""
        parsed_obj = ParserBaseObject.parse_from_dict(
            TestDataclass1,
            TEST_DICT_DATA,
        )
        self.assertEqual(parsed_obj.dictionary, TEST_DICT_DATA)
        self.assertEqual(
            parsed_obj,
            TestDataclass1(
                value1=str(TEST_DICT_DATA["value1"]),
                value2=TEST_DICT_DATA["value2"],
                value3=TEST_DICT_DATA["value3"],
                value4=TEST_DICT_DATA["value4"],
            ),
        )

    def test_parse_from_dict_nested_data(self):
        """Tests that parse_from_dict parses nested data (and applies parsing
        functions)"""
        parsed_obj = ParserBaseObject.parse_from_dict(
            TestDataclass2,
            TEST_DICT_DATA,
        )
        self.assertEqual(parsed_obj.dictionary, TEST_DICT_DATA)
        self.assertEqual(
            parsed_obj,
            TestDataclass2(
                value1=TEST_DICT_DATA["value1"],
                value2=f"Date({TEST_DICT_DATA['value2']})",
                value3=TEST_DICT_DATA["value3"],
                value4=TestDataclass1(
                    value1=str(TEST_DICT_DATA["value4"]["value1"]),
                    value2=TEST_DICT_DATA["value4"]["value2"],
                    value3=TEST_DICT_DATA["value4"]["value3"],
                    value4=TEST_DICT_DATA["value4"]["value4"],
                ),
            ),
        )

    def test_parse_from_dict_list(self):
        """Tests that parse_from_dict_list parses a list of dictionaries
        correctly"""
        parsed_obj_list = ParserBaseObject.parse_from_dict_list(
            TestDataclass1,
            TEST_DICT_DATA_LIST,
        )
        self.assertEqual(len(parsed_obj_list), 2)
        self.assertEqual(parsed_obj_list[0].dictionary, TEST_DICT_DATA_LIST[0])
        self.assertEqual(
            parsed_obj_list[0],
            TestDataclass1(
                value1=str(TEST_DICT_DATA["value1"]),
                value2=TEST_DICT_DATA["value2"],
                value3=TEST_DICT_DATA["value3"],
                value4=TEST_DICT_DATA["value4"],
            ),
        )
        self.assertEqual(parsed_obj_list[1].dictionary, TEST_DICT_DATA_LIST[1])
        self.assertEqual(
            parsed_obj_list[1],
            TestDataclass1(
                value1=str(TEST_DICT_DATA2["value1"]),
                value2=TEST_DICT_DATA2["value2"],
                value3=TEST_DICT_DATA2["value3"],
                value4=TEST_DICT_DATA2["value4"],
            ),
        )

    def test_parse_from_dict_list_nested(self):
        """Tests that parse_from_dict_list parses a list of dictionaries
        correctly when nested"""
        parsed_obj_list = ParserBaseObject.parse_from_dict_list(
            TestDataclass2,
            TEST_DICT_DATA_LIST,
        )
        self.assertEqual(len(parsed_obj_list), 2)
        self.assertEqual(parsed_obj_list[0].dictionary, TEST_DICT_DATA_LIST[0])
        self.assertEqual(
            parsed_obj_list[0],
            TestDataclass2(
                value1=TEST_DICT_DATA["value1"],
                value2=f"Date({TEST_DICT_DATA['value2']})",
                value3=TEST_DICT_DATA["value3"],
                value4=TestDataclass1(
                    value1=str(TEST_DICT_DATA["value4"]["value1"]),
                    value2=TEST_DICT_DATA["value4"]["value2"],
                    value3=TEST_DICT_DATA["value4"]["value3"],
                    value4=TEST_DICT_DATA["value4"]["value4"],
                ),
            ),
        )
        self.assertEqual(parsed_obj_list[1].dictionary, TEST_DICT_DATA_LIST[1])
        self.assertEqual(
            parsed_obj_list[1],
            TestDataclass2(
                value1=TEST_DICT_DATA2["value1"],
                value2=f"Date({TEST_DICT_DATA2['value2']})",
                value3=TEST_DICT_DATA2["value3"],
                value4=[
                    TestDataclass1(
                        value1=str(TEST_DICT_DATA2["value4"][0]["value1"]),
                        value2=TEST_DICT_DATA2["value4"][0]["value2"],
                        value3=TEST_DICT_DATA2["value4"][0]["value3"],
                        value4=TEST_DICT_DATA2["value4"][0]["value4"],
                    ),
                    TestDataclass1(
                        value1=str(TEST_DICT_DATA2["value4"][1]["value1"]),
                        value2=TEST_DICT_DATA2["value4"][1]["value2"],
                        value3=TEST_DICT_DATA2["value4"][1]["value3"],
                        value4=TEST_DICT_DATA2["value4"][1]["value4"],
                    ),
                ],
            ),
        )

    def test_parse_from_dict_error(self):
        """Tests the appropriate error is thrown when a value is missing
        from the dictionary but is required in the dataclass"""
        with self.assertRaises(TypeError) as err:
            ParserBaseObject.parse_from_dict(TestDataclassDefault, {})
        self.assertEqual(
            str(err.exception),
            (
                "At least one class attribute in 'TestDataclassDefault' was "
                "either missing from the dictionary or was parsed to be 'None' "
                "but doesn't have a default value."
            ),
        )

    def test_parse_from_dict_default_values(self):
        """Tests no error is thrown when a value with a default is missing
        from the dictionary"""
        parsed_obj = ParserBaseObject.parse_from_dict(
            TestDataclassDefault, {"value1": "test"}
        )
        self.assertEqual(parsed_obj, TestDataclassDefault(value1="test", value2=None))


class TestParseFunctions(TestCase):
    @patch("dafni_cli.api.parser.isoparse")
    def test_parse_datetime(self, mock_isoparse):
        """Tests parse_datetime functions correctly"""

        # SETUP
        date_string = MagicMock()

        # CALL
        result = parse_datetime(date_string)

        # ASSERT
        mock_isoparse.assert_called_once_with(date_string)
        self.assertEqual(result, mock_isoparse.return_value)

    @patch.object(ParserBaseObject, "parse_from_dict")
    def test_parse_dict_retaining_keys(self, mock_parse_from_dict):
        """Tests parse_dict_retaining_keys functions correctly"""

        # SETUP
        dictionary = {"id-1": TEST_DICT_DATA, "id-2": TEST_DICT_DATA}
        func = parse_dict_retaining_keys(TestDataclass1)
        instance_mocks = [MagicMock(), MagicMock()]
        mock_parse_from_dict.side_effect = instance_mocks

        # CALL
        result = func(dictionary)

        # ASSERT
        self.assertEqual(result, {"id-1": instance_mocks[0], "id-2": instance_mocks[1]})

    def test_parse_dict_retaining_keys_when_empty(self):
        """Tests parse_dict_retaining_keys functions correctly when there
        is nothing to parse"""

        # SETUP
        dictionary = {}
        func = parse_dict_retaining_keys(TestDataclass1)

        # CALL
        result = func(dictionary)

        # ASSERT
        self.assertEqual(result, {})
