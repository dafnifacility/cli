import pytest
from mock import patch, call
from dateutil import parser

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
