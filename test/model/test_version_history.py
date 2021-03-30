import pytest
from mock import patch, call, MagicMock, PropertyMock, Mock
from dateutil import parser
from dateutil.tz import tzutc
from datetime import datetime as dt

from dafni_cli.model import model, version_history
from test.fixtures.model_fixtures import (
    get_models_list_fixture,
    get_single_model_fixture,
    get_model_metadata_fixture,
)
from dafni_cli.consts import TAB_SPACE


class TestVersionHistory:
    """Test class for the VersionHistory class"""

    @patch.object(model.Model, "get_details_from_id")
    class TestInit:
        """Test class to test the VersionHistory.__init__() functionality"""

        def test_expected_attributes_found_on_class_and_dictionary_is_expected_value(
            self, mock_get_details, get_single_model_fixture,
        ):
            # SETUP
            expected_attributes = [
                "dictionary",
                "history",
            ]
            model_instance = model.Model()
            # Populate the dictionary and version_id of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_single_model_fixture
            model_instance.version_id = "version_id"
            jwt = "jwt"

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert isinstance(instance, version_history.ModelVersionHistory)
            assert all(getattr(instance, value) for value in expected_attributes)
            assert instance.dictionary == get_single_model_fixture["version_history"]

        def test_models_added_to_history_in_correct_order(
            self, mock_get_details, get_single_model_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary and version_id of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_single_model_fixture
            model_instance.version_id = "vid_1"
            jwt = "jwt"
            version_history_dict = get_single_model_fixture["version_history"]

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert len(instance.history) == 2
            assert instance.history[0].version_id == model_instance.version_id
            assert mock_get_details.call_args_list == [
                call(jwt, "vid_1"),
                call(jwt, version_history_dict[1]["id"]),
            ]
            assert isinstance(instance.history[1], model.Model)

        def test_latest_model_does_not_call_get_details_if_details_filled_in(
            self, mock_get_details, get_single_model_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary and version_id of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_single_model_fixture
            model_instance.version_id = "vid_1"
            model_instance.version_tags = ["latest", "new_param"]
            model_instance.display_name = "test model name"
            model_instance.publication_time = "time"
            model_instance.version_message = "version message"
            jwt = "jwt"
            previous_model_version_id = get_single_model_fixture["version_history"][1]["id"]

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert mock_get_details.call_count == 1
            assert mock_get_details.called_once_with(jwt, previous_model_version_id)

        def test_model_with_no_previous_versions_only_returns_one_entry_and_does_not_enter_loop(
            self, mock_get_details, get_single_model_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Use second model dictionary fixture as there is only 1 version
            model_instance.dictionary = get_single_model_fixture
            model_instance.dictionary["version_history"] = [model_instance.dictionary["version_history"][0]]
            model_instance.version_id = "vid_2"
            model_instance.version_tags = ["latest", "new_param"]
            model_instance.display_name = "test model name"
            model_instance.version_message = "version message"
            model_instance.publication_time = "time"
            jwt = "jwt"

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert all(
                len(version_property) == 1
                for version_property in [instance.dictionary, instance.history]
            )
            assert instance.history == [model_instance]
            mock_get_details.assert_not_called()

    @patch("dafni_cli.model.version_history.click")
    @patch.object(model.Model, "get_details_from_id")
    class TestOutputVersionHistory:
        """Test class to test the VersionHistory.output_version_history() functionality"""

        def test_single_version_displayed_correctly(
            self, mock_get_details, mock_click, get_single_model_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Remove first value of the version history
            get_single_model_fixture["version_history"] = [get_single_model_fixture["version_history"][0]]
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_single_model_fixture
            model_instance.version_id = "id"
            jwt = "jwt"
            instance = version_history.ModelVersionHistory(jwt, model_instance)
            instance.history = [model_instance]
            instance.history[0].display_name = "name"
            instance.history[0].publication_time = dt(2021, 5, 2, tzinfo=tzutc())
            instance.history[0].version_message = "version message"
            instance.history[0].version_tags = ["tag"]
            expected_string = (
                "Name: name" + TAB_SPACE + "ID: id" + TAB_SPACE + "Date: May 02 2021"
            )

            # CALL
            instance.output_version_history()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(expected_string),
                call("Version message: version message"),
                call("Version tags: tag"),
                call(""),
            ]

        def test_multiple_versions_displayed_correctly(
            self, mock_get_details, mock_click, get_single_model_fixture,
        ):
            # SETUP
            init_model_instance = model.Model()
            # Remove first value of the version history
            get_single_model_fixture["version_history"] = [get_single_model_fixture["version_history"][0]]
            # Populate the dictionary of the model so the version history dictionary can be accessed
            init_model_instance.dictionary = get_single_model_fixture
            jwt = "jwt"
            init_model_instance.version_id = "id"
            instance = version_history.ModelVersionHistory(jwt, init_model_instance)

            model_instance_1 = init_model_instance
            model_instance_1.display_name = "name"
            model_instance_1.publication_time = dt(2021, 5, 2, tzinfo=tzutc())
            model_instance_1.version_message = "version message"
            model_instance_1.version_tags = ["tag"]

            model_instance_2 = model.Model()
            model_instance_2.display_name = "name 2"
            model_instance_2.version_id = "id 2"
            model_instance_2.publication_time = dt(2021, 3, 2, tzinfo=tzutc())
            model_instance_2.version_message = "older version message"
            model_instance_2.version_tags = ["old", "tag2"]

            instance.history = [model_instance_1, model_instance_2]

            # CALL
            instance.output_version_history()

            # ASSERT
            expected_string1 = (
                "Name: name" + TAB_SPACE + "ID: id" + TAB_SPACE + "Date: May 02 2021"
            )
            expected_string2 = (
                "Name: name 2"
                + TAB_SPACE
                + "ID: id 2"
                + TAB_SPACE
                + "Date: March 02 2021"
            )
            assert mock_click.echo.call_args_list == [
                call(expected_string1),
                call("Version message: version message"),
                call("Version tags: tag"),
                call(""),
                call(expected_string2),
                call("Version message: older version message"),
                call("Version tags: old, tag2"),
                call(""),
            ]

        @patch("dafni_cli.model.version_history.print_json")
        def test_print_json_called_with_dictionary_when_json_flag_true(
                self, mock_print, mock_get_details, mock_click, get_single_model_fixture
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_single_model_fixture
            model_instance.version_id = "id"
            jwt = "jwt"
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # CALL
            instance.output_version_history(True)

            # ASSERT
            mock_print.assert_called_once_with(instance.dictionary)
            mock_click.echo.assert_not_called()
