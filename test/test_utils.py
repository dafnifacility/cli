import pytest
from mock import patch, call
from dateutil import parser
from io import BytesIO
from zipfile import ZipFile
import os

from dafni_cli import utils
from dafni_cli.model.model import Model
from test.fixtures.model_fixtures import get_models_list_fixture


@patch("dafni_cli.utils.click")
class TestProsePrint:
    """Test class to test the prose_print() functionality"""

    def test_string_shorter_than_width_prints_as_one_string(self, mock_click):
        # SETUP
        string = "123456"

        # CALL
        utils.prose_print(string, 10)

        # ASSERT
        assert mock_click.echo.call_args_list == [call(string)]

    def test_string_without_line_breaks_or_spaces_is_split_correctly_and_printed_sequentially(
        self, mock_click
    ):
        # SETUP
        string = "123456"

        # CALL
        utils.prose_print(string, 2)

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("12"),
            call("34"),
            call("56"),
        ]

    def test_string_with_space_before_width_but_no_line_break_splits_at_space(
        self, mock_click
    ):
        # SETUP
        string = "12 3456"

        # CALL
        utils.prose_print(string, 4)

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("12"),
            call("3456"),
        ]

    def test_string_with_line_break_splits_at_line_break(self, mock_click):
        # SETUP
        string = "123456\n78"

        # CALL
        utils.prose_print(string, 4)

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("1234"),
            call("56"),
            call("78"),
        ]


class TestProcessResponseToClassList:
    """Test class to test the process_response_to_class_list() functionality"""

    @patch.object(Model, "set_details_from_dict")
    def test_model_created_and_details_from_dict_called_for_each_model(
        self, mock_set, get_models_list_fixture
    ):
        # SETUP
        models = get_models_list_fixture

        # CALL
        result = utils.process_response_to_class_list(models, Model)

        # ASSERT
        assert mock_set.call_args_list == [call(models[0]), call(models[1])]
        assert len(result) == 2
        assert all(isinstance(instance, Model) for instance in result)

    def test_a_models_dict_list_is_processed_correctly(self, get_models_list_fixture):
        # SETUP
        models = get_models_list_fixture

        # CALL
        result = utils.process_response_to_class_list(models, Model)

        # ASSERT
        for idx, instance in enumerate(result):
            assert instance.display_name == models[idx]["name"]
            assert instance.summary == models[idx]["summary"]
            assert instance.description == models[idx]["description"]
            assert instance.creation_time == parser.isoparse(
                models[idx]["creation_date"]
            )
            assert instance.publication_time == parser.isoparse(
                models[idx]["publication_date"]
            )
            assert instance.version_id == models[idx]["id"]
            assert instance.version_tags == models[idx]["version_tags"]
            assert instance.container == models[idx]["container"]


class TestOptionalColumn:
    """Test class to test the optional_column() functionality"""

    @pytest.mark.parametrize(
        "value, result",
        [
            ("value", "value     "),
            (1, "1         "),
            (1.0, "1.0       "),
            ({"sub_key": "value"}, "{'sub_key': 'value'}"),
            ({}, "{}        "),
            ([], "[]        "),
            ([1, 2], "[1, 2]    "),
            (True, "True      "),
        ],
    )
    def test_if_key_exists_value_is_returned_with_correct_width(self, value, result):
        # SETUP
        key = "key"
        dictionary = {key: value}
        column_width = 10

        # CALL
        entry = utils.optional_column(dictionary, key, column_width)

        # ASSERT
        assert entry == result

    @pytest.mark.parametrize(
        "value, result",
        [
            ("value", "     value"),
            (1, "         1"),
            (1.0, "       1.0"),
            ({"sub_key": "value"}, "{'sub_key': 'value'}"),
            ({}, "        {}"),
            ([], "        []"),
            ([1, 2], "    [1, 2]"),
            (True, "      True"),
        ],
    )
    def test_if_key_exists_value_is_returned_with_correct_width_and_alignment(
        self, value, result
    ):
        # SETUP
        key = "key"
        dictionary = {key: value}
        column_width = 10
        alignment = ">"

        # CALL
        entry = utils.optional_column(dictionary, key, column_width, alignment)

        # ASSERT
        assert entry == result

    @pytest.mark.parametrize(
        "value, result",
        [
            ("value", "value"),
            (1, "1"),
            (1.0, "1.0"),
            ({"sub_key": "value"}, "{'sub_key': 'value'}"),
            ({}, "{}"),
            ([], "[]"),
            ([1, 2], "[1, 2]"),
            (True, "True"),
        ],
    )
    def test_if_key_exists_and_no_column_width_specified_string_with_no_extra_spaces_is_returned(
        self, value, result
    ):
        # SETUP
        key = "key"
        dictionary = {key: value}

        # CALL
        entry = utils.optional_column(dictionary, key)

        # ASSERT
        assert entry == result

    def test_if_key_does_not_exist_but_column_width_specified_then_blank_space_of_specified_length_is_returned(
        self,
    ):
        # SETUP
        key = "key"
        dictionary = {"other_key": "value"}
        column_width = 8

        # CALL
        entry = utils.optional_column(dictionary, key, column_width)

        # ASSERT
        assert entry == " " * 8

    def test_if_key_does_not_exist_and_column_width_not_specified_then_empty_string_returned(
        self,
    ):
        # SETUP
        key = "key"
        dictionary = {"other_key": "value"}

        # CALL
        entry = utils.optional_column(dictionary, key)

        # ASSERT
        assert entry == ""

    def test_exception_raised_when_column_width_negative(self):
        # SETUP
        key = "key"
        value = "value"
        dictionary = {key: value}

        # CALL
        # ASSERT
        with pytest.raises(
            ValueError, match="Column width for optional column must be non-negative"
        ):
            utils.optional_column(dictionary, key, -1)


class TestProcessDateFilter:
    """Test class to test the process_date_filter functionality"""

    @pytest.mark.parametrize(
        "date_str, expected",
        [
            ("1/2/2003", "2003-02-01T00:00:00"),
            ("10/2/2003", "2003-02-10T00:00:00"),
            ("10/12/2003", "2003-12-10T00:00:00"),
        ],
    )
    def test_valid_date_strings_are_formatted_correctly(self, date_str, expected):
        # SETUP
        # CALL
        result = utils.process_date_filter(date_str)

        # ASSERT
        assert result == expected

    @pytest.mark.parametrize(
        "date_str",
        ["1/1/21", "1/13/2021", "32/2/2021"],
        ids=["Case 1 - 2 digit Year", "Case 2 - Month 13", "Case 3 - 32nd day"],
    )
    def test_value_error_raised_if_given_invalid_formatted_date(self, date_str):
        # SETUP # CALL # ASSERT
        with pytest.raises(ValueError):
            utils.process_date_filter(date_str)


class TestCheckKeyInDict:
    """Test class to test the check_key_in_dict functionality"""

    @pytest.mark.parametrize("input_dict", [[], "str", 12])
    def test_default_value_returned_if_input_dict_is_not_a_dict(self, input_dict):
        # SETUP
        keys = ["key"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == "N/A"

    @pytest.mark.parametrize("input_dict", [[], "str", 12])
    def test_defined_default_value_returned_if_input_dict_is_not_a_dict(
        self, input_dict
    ):
        # SETUP
        keys = ["key"]
        default = "default"

        # CALL
        result = utils.check_key_in_dict(input_dict, keys, default=default)

        # ASSERT
        assert result == default

    def test_default_value_returned_if_key_not_in_input_dict(self):
        # SETUP
        input_dict = {"key_1": "value_1"}
        keys = ["key_2"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == "N/A"

    @pytest.mark.parametrize("value", [["some", "items"], [], {}, "", "str", 12])
    def test_value_returned_if_key_in_input_dict(self, value):
        # SETUP
        input_dict = {"key_1": value}
        keys = ["key_1"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == value

    def test_default_value_returned_if_key_in_input_dict_and_value_is_none(self):
        # SETUP
        input_dict = {"key_1": None}
        keys = ["key_1"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == "N/A"

    def test_default_value_returned_if_nested_key_not_in_input_dict(self):
        # SETUP
        input_dict = {"key_1": {"nested_1": "value_1"}}
        keys = ["key_1", "nested_2"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == "N/A"

    @pytest.mark.parametrize("value", [[], "str", 12])
    def test_default_value_returned_if_nested_key_given_but_nested_item_not_a_dict(
        self, value
    ):
        # SETUP
        input_dict = {"key_1": value}
        keys = ["key_1", "nested_2"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == "N/A"

    @pytest.mark.parametrize("value", [["some", "items"], [], {}, "", "str", 12])
    def test_value_returned_if_nested_key_in_input_dict(self, value):
        # SETUP
        input_dict = {"key_1": {"nested_1": value}}
        keys = ["key_1", "nested_1"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == value

    def test_default_value_returned_if_nested_key_in_input_dict_and_value_is_none(self):
        # SETUP
        # SETUP
        input_dict = {"key_1": {"nested_1": None}}
        keys = ["key_1", "nested_1"]

        # CALL
        result = utils.check_key_in_dict(input_dict, keys)

        # ASSERT
        assert result == "N/A"


@patch("dafni_cli.utils.check_key_in_dict")
class TestProcessDictDatetime:
    """Test class to test the process_dict_datetime functionality"""

    @pytest.mark.parametrize("value", [[], (), {}, None])
    def test_default_value_returned_if_key_not_found(self, mock_check, value):
        # SETUP
        mock_check.return_value = value
        input_dict = {"key": "value"}
        keys = ["key_1"]

        # CALL
        result = utils.process_dict_datetime(input_dict, keys)

        # ASSERT
        assert result == "N/A"

    @pytest.mark.parametrize("value", [[], (), {}, None])
    def test_defined_default_value_returned_if_key_not_found(self, mock_check, value):
        # SETUP
        mock_check.return_value = value
        input_dict = {"key": "value"}
        keys = ["key_1"]
        default = "default"

        # CALL
        result = utils.process_dict_datetime(input_dict, keys, default=default)

        # ASSERT
        assert result == "default"

    @pytest.mark.parametrize(
        "value",
        [
            "2021/01/03",
            "March 21st 2021",
            "2021-3-16",
        ],
    )
    def test_value_returned_unprocessed_if_invalid_datetime_str(
        self, mock_check, value
    ):
        # SETUP
        mock_check.return_value = value
        input_dict = {"key": "value"}
        keys = ["key"]

        # CALL
        result = utils.process_dict_datetime(input_dict, keys)

        # ASSERT
        assert result == value

    @pytest.mark.parametrize(
        "value",
        [
            "2021-03-16T09:27:21+00:00",
            "2021-03-16T09:27:21Z",
            "2021-03-16",
        ],
    )
    def test_value_returned_processed_if_valid_datetime_str_found(
        self, mock_check, value
    ):
        # SETUP
        mock_check.return_value = value
        input_dict = {"key": "value"}
        keys = ["key"]

        # CALL
        result = utils.process_dict_datetime(input_dict, keys)

        # ASSERT
        assert result == "March 16 2021"


class TestOutputTableRow:
    """Test class to test the output_table_row functionality"""

    @pytest.mark.parametrize(
        "columns, widths, expected",
        [
            (["Column_1"], [10], "Column_1  \n-----------\n"),
            (
                ["Column_1", "Column_2", "Column_3"],
                [10, 11, 12],
                "Column_1   Column_2    Column_3    \n------------------------------------\n",
            ),
        ],
    )
    def test_table_header_string_processed_correctly_when_no_alignment_given(
        self, columns, widths, expected
    ):
        # SETUP
        # CALL
        result = utils.output_table_row(columns, widths, header=True)

        # ASSERT
        assert result == expected

    @pytest.mark.parametrize(
        "alignment, expected",
        [
            (
                "<",
                "Column_1   Column_2    Column_3    \n------------------------------------\n",
            ),
            (
                "^",
                " Column_1   Column_2     Column_3  \n------------------------------------\n",
            ),
            (
                ">",
                "  Column_1    Column_2     Column_3\n------------------------------------\n",
            ),
        ],
    )
    def test_table_header_string_processed_correctly_when_alignment_given_for_multiple_columns(
        self, alignment, expected
    ):
        # SETUP
        columns = ["Column_1", "Column_2", "Column_3"]
        widths = [10, 11, 12]

        # CALL
        result = utils.output_table_row(
            columns, widths, alignment=alignment, header=True
        )

        # ASSERT
        assert result == expected

    @pytest.mark.parametrize(
        "alignment, expected",
        [
            (
                "<",
                "Column_1  \n-----------\n",
            ),
            (
                "^",
                " Column_1 \n-----------\n",
            ),
            (
                ">",
                "  Column_1\n-----------\n",
            ),
        ],
    )
    def test_table_header_string_processed_correctly_when_alignment_given_for_single_column(
        self, alignment, expected
    ):
        # SETUP
        columns = ["Column_1"]
        widths = [10]

        # CALL
        result = utils.output_table_row(
            columns, widths, alignment=alignment, header=True
        )

        # ASSERT
        assert result == expected

    @pytest.mark.parametrize(
        "values, widths, expected",
        [
            (["Value_1"], [10], "Value_1   \n"),
            (
                ["Value_1", "Value_2", "Value_3"],
                [10, 11, 12],
                "Value_1    Value_2     Value_3     \n",
            ),
        ],
    )
    def test_table_row_string_processed_correctly_when_no_alignment_given(
        self, values, widths, expected
    ):
        # SETUP
        # CALL
        result = utils.output_table_row(values, widths)

        # ASSERT
        assert result == expected

    @pytest.mark.parametrize(
        "alignment, expected",
        [
            (
                "<",
                "Value_1    Value_2     Value_3     \n",
            ),
            (
                "^",
                " Value_1     Value_2     Value_3   \n",
            ),
            (
                ">",
                "   Value_1     Value_2      Value_3\n",
            ),
        ],
    )
    def test_table_row_string_processed_correctly_when_alignment_given_for_multiple_values(
        self, alignment, expected
    ):
        # SETUP
        values = ["Value_1", "Value_2", "Value_3"]
        widths = [10, 11, 12]

        # CALL
        result = utils.output_table_row(values, widths, alignment=alignment)

        # ASSERT
        assert result == expected

    @pytest.mark.parametrize(
        "alignment, expected",
        [
            (
                "<",
                "Value_1   \n",
            ),
            (
                "^",
                " Value_1  \n",
            ),
            (
                ">",
                "   Value_1\n",
            ),
        ],
    )
    def test_table_row_string_processed_correctly_when_alignment_given_for_single_value(
        self, alignment, expected
    ):
        # SETUP
        values = ["Value_1"]
        widths = [10]

        # CALL
        result = utils.output_table_row(values, widths, alignment=alignment)

        # ASSERT
        assert result == expected


@patch("dafni_cli.utils.output_table_row")
class TestOutputTable:
    """Test class to test the output_table functionality"""

    def test_correct_table_str_returned_for_single_column_table_with_default_alignment(
        self, mock_output
    ):
        # SETUP
        columns = ["Column_1"]
        rows = [["Value_1"]]
        widths = [10]
        # setup output_table_row to return the firs column/value passed in
        mock_output.side_effect = "Column_1  \n----------\n", "Value_1   \n"

        # CALL
        result = utils.output_table(columns, widths, rows)

        # ASSERT
        assert result == "Column_1  \n----------\nValue_1   \n"
        assert mock_output.call_args_list == [
            call(columns, widths, "<", header=True),
            call(rows[0], widths, "<"),
        ]

    def test_correct_table_str_returned_for_multiple_column_and_row_table_with_default_alignment(
        self, mock_output
    ):
        # SETUP
        columns = ["Column_1", "Column_2"]
        rows = [["Value_1", "Value_2"], ["Value_3", "Value_4"]]
        widths = [10]
        # setup output_table_row to return the firs column/value passed in
        mock_output.side_effect = (
            "Column_1  Column_2   \n----------\n",
            "Value_1   Value_2    \n",
            "Value_3   Value_4    \n",
        )

        # CALL
        result = utils.output_table(columns, widths, rows)

        # ASSERT
        assert (
            result
            == "Column_1  Column_2   \n----------\nValue_1   Value_2    \nValue_3   Value_4    \n"
        )
        assert mock_output.call_args_list == [
            call(columns, widths, "<", header=True),
            call(rows[0], widths, "<"),
            call(rows[1], widths, "<"),
        ]


class TestProcessFileSize:
    """Test class to test the process_file_size functionality"""

    @pytest.mark.parametrize("file_size", [[12], (12, 13)])
    def test_empty_string_returned_if_non_integer_or_float_value_given(self, file_size):
        # SETUP CALL
        result = utils.process_file_size(file_size)
        # ASSERT
        assert result == ""

    @pytest.mark.parametrize("data_type", [str, float, int])
    @pytest.mark.parametrize(
        "file_size, expected",
        [
            (1.0, "1.0 B"),
            (10.0, "10.0 B"),
            (100.0, "100.0 B"),
            (1e3, "1.0 KB"),
            (1e4, "10.0 KB"),
            (1e5, "100.0 KB"),
            (1e6, "1.0 MB"),
            (1e7, "10.0 MB"),
            (1e8, "100.0 MB"),
            (1e9, "1.0 GB"),
            (1e10, "10.0 GB"),
            (1e11, "100.0 GB"),
            (1e12, "1000.0 GB"),
            (1.5e3, "1.5 KB"),
            (2.7e6, "2.7 MB"),
            (3.8e9, "3.8 GB"),
            (2.743e6, "2.7 MB"),
            (3.854e9, "3.9 GB"),
        ],
    )
    def test_file_size_processed_correctly(self, file_size, expected, data_type):
        # SETUP
        input_size = data_type(file_size)

        # CALL
        result = utils.process_file_size(input_size)

        # ASSERT
        assert result == expected


@patch("dafni_cli.utils.click")
class TestArgumentConfirmation:
    """Test class to test the argument_confirmation functionality"""

    def test_arguments_are_printed_correctly_without_additional_messages(
        self, mock_click
    ):
        # SETUP
        argument_names = ["arg 1", "arg 2", "arg 3"]
        arguments = ["string option", "12", "{'key': 'value'}"]
        confirmation_message = "confirmation message"

        # CALL
        utils.argument_confirmation(argument_names, arguments, confirmation_message)

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("arg 1: string option"),
            call("arg 2: 12"),
            call("arg 3: {'key': 'value'}"),
        ]
        mock_click.confirm.assert_called_once_with(confirmation_message, abort=True)

    def test_arguments_are_printed_correctly_with_additional_messages(self, mock_click):
        # SETUP
        argument_names = ["arg 1", "arg 2", "arg 3"]
        arguments = ["string option", "12", "{'key': 'value'}"]
        confirmation_message = "confirmation message"
        additional_messages = ["additional message 1", "additional message 2"]

        # CALL
        utils.argument_confirmation(
            argument_names, arguments, confirmation_message, additional_messages
        )

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("arg 1: string option"),
            call("arg 2: 12"),
            call("arg 3: {'key': 'value'}"),
            call("additional message 1"),
            call("additional message 2"),
        ]
        mock_click.confirm.assert_called_once_with(confirmation_message, abort=True)

    def test_arguments_are_printed_correctly_with_none_additional_message_specified(
        self, mock_click
    ):
        # SETUP
        argument_names = ["arg 1", "arg 2", "arg 3"]
        arguments = ["string option", "12", "{'key': 'value'}"]
        confirmation_message = "confirmation message"
        additional_messages = None

        # CALL
        utils.argument_confirmation(
            argument_names, arguments, confirmation_message, additional_messages
        )

        # ASSERT
        assert mock_click.echo.call_args_list == [
            call("arg 1: string option"),
            call("arg 2: 12"),
            call("arg 3: {'key': 'value'}"),
        ]
        mock_click.confirm.assert_called_once_with(confirmation_message, abort=True)


class TestWriteFilesToZip:
    """Test class to test the write_files_to_zip functionality"""

    def test_given_files_written_as_zip_file_to_given_location_with_correct_contents(
        self, tmp_path
    ):
        # SETUP
        path = tmp_path
        zip_path = os.path.join(path, "test.zip")

        file_names = ["file_1.txt", "file_2.txt"]
        file_contents = [BytesIO(b"Test text 1"), BytesIO(b"Test text 2")]

        # CALL
        utils.write_files_to_zip(zip_path, file_names, file_contents)

        # ASSERT
        assert os.path.exists(zip_path)
        with ZipFile(zip_path, "r") as zipObj:
            assert zipObj.namelist() == file_names

            for idx, name in enumerate(file_names):
                with zipObj.open(name, "r") as zip_file:
                    assert zip_file.read() == file_contents[idx].getvalue()