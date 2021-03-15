import pytest
from mock import patch, call, MagicMock, PropertyMock, Mock
from dateutil import parser
from dateutil.tz import tzutc
from datetime import datetime as dt

from dafni_cli.model import (
    model,
    version_history
)
from test.fixtures.model_fixtures import (
    get_models_list_fixture,
    get_model_metadata_fixture,
)
from dafni_cli.consts import TAB_SPACE


class TestVersionHistory:
    """Test class for the VersionHistory class"""

    @patch.object(model.Model, "get_details_from_id")
    class TestInit:
        """Test class to test the VersionHistory.__init__() functionality"""

        def test_expected_attributes_found_on_class_and_dictionary_is_expected_value(
                self,
                mock_get_details,
                get_models_list_fixture,
        ):
            # SETUP
            expected_attributes = [
                "dictionary",
                "history",
                "version_messages",
                "version_publication_dates",
                "version_tags"
            ]
            model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_models_list_fixture[0]
            jwt = "jwt"

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert isinstance(instance, version_history.ModelVersionHistory)
            assert all(
                getattr(instance, value) for value in expected_attributes
            )
            assert instance.dictionary == get_models_list_fixture[0]['version_history']

        def test_models_added_to_history_in_correct_order(
                self,
                mock_get_details,
                get_models_list_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_models_list_fixture[0]
            jwt = "jwt"
            previous_model_version_id = get_models_list_fixture[0]['version_history'][1]['id']

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert len(instance.history) == 2
            assert instance.history[0].version_id == model_instance.version_id
            assert mock_get_details.called_once_with(jwt, previous_model_version_id)
            assert isinstance(instance.history[1], model.Model)

        def test_ISO_dates_are_converted_to_datetime(
                self,
                mock_get_details,
                get_models_list_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_models_list_fixture[0]
            jwt = "jwt"

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert instance.version_publication_dates[0] == dt(2021, 2, 1, tzinfo=tzutc()).date()
            assert instance.version_publication_dates[1] == dt(2021, 5, 2, tzinfo=tzutc()).date()

        def test_version_attributes_added_in_correct_order(
                self,
                mock_get_details,
                get_models_list_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_models_list_fixture[0]
            jwt = "jwt"
            version_history_dict = get_models_list_fixture[0]['version_history']

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert all(
                len(version_property) == 2 for version_property in [instance.history,
                                                                    instance.version_messages,
                                                                    instance.version_publication_dates,
                                                                    instance.version_tags]
            )
            for i in range(2):
                assert instance.version_messages[i] == version_history_dict[i]['version_message']
                time_in_dt = parser.isoparse(version_history_dict[i]["published"])
                assert instance.version_publication_dates[i] == time_in_dt.date()
                assert instance.version_tags[i] == version_history_dict[i]['version_tags']

        def test_model_with_no_previous_versions_only_returns_one_entry_and_does_not_request_details_from_api(
                self,
                mock_get_details,
                get_models_list_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Use second model dictionary fixture as there is only 1 version
            model_instance.dictionary = get_models_list_fixture[1]
            jwt = "jwt"
            version_history_dict = get_models_list_fixture[1]['version_history']

            # CALL
            instance = version_history.ModelVersionHistory(jwt, model_instance)

            # ASSERT
            assert all(
                len(version_property) == 1 for version_property in [instance.dictionary,
                                                                    instance.history,
                                                                    instance.version_messages,
                                                                    instance.version_publication_dates,
                                                                    instance.version_tags]
            )
            assert instance.history == [model_instance]
            assert instance.version_messages[0] == version_history_dict[0]['version_message']
            time_in_dt = parser.isoparse(version_history_dict[0]["published"])
            assert instance.version_publication_dates[0] == time_in_dt.date()
            assert instance.version_tags[0] == version_history_dict[0]['version_tags']
            mock_get_details.assert_not_called()

    @patch("dafni_cli.model.version_history.click")
    class TestOutputVersionHistory:
        """Test class to test the VersionHistory.output_version_history() functionality"""

        def test_single_version_displayed_correctly(
                self,
                mock_click,
                get_models_list_fixture,
        ):
            # SETUP
            model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            model_instance.dictionary = get_models_list_fixture[1]
            jwt = "jwt"
            instance = version_history.ModelVersionHistory(jwt, model_instance)
            new_model_instance = model.Model()
            new_model_instance.display_name = "name"
            new_model_instance.version_id = "id"
            instance.history = [new_model_instance]
            instance.version_publication_dates = [dt(2021, 5, 2, tzinfo=tzutc())]
            instance.version_messages = ["version message"]
            instance.version_tags = [["tag"]]
            expected_string = "Name: name" + \
                              TAB_SPACE + \
                              "ID: id" + \
                              TAB_SPACE + \
                              "Date: May 02 2021"

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
                self,
                mock_click,
                get_models_list_fixture,
        ):
            # SETUP
            init_model_instance = model.Model()
            # Populate the dictionary of the model so the version history dictionary can be accessed
            init_model_instance.dictionary = get_models_list_fixture[1]
            jwt = "jwt"
            instance = version_history.ModelVersionHistory(jwt, init_model_instance)
            model_instance_1 = model.Model()
            model_instance_1.display_name = "name"
            model_instance_1.version_id = "id"
            model_instance_2 = model.Model()
            model_instance_2.display_name = "name 2"
            model_instance_2.version_id = "id 2"
            instance.history = [model_instance_1, model_instance_2]
            instance.version_publication_dates = [dt(2021, 5, 2, tzinfo=tzutc()), dt(2021, 3, 2, tzinfo=tzutc())]
            instance.version_messages = ["version message", "older version message"]
            instance.version_tags = [["tag"], ["old", "tag2"]]
            expected_string1 = "Name: name" + \
                               TAB_SPACE + \
                               "ID: id" + \
                               TAB_SPACE + \
                               "Date: May 02 2021"
            expected_string2 = "Name: name 2" + \
                               TAB_SPACE + \
                               "ID: id 2" + \
                               TAB_SPACE + \
                               "Date: March 02 2021"

            # CALL
            instance.output_version_history()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(expected_string1),
                call("Version message: version message"),
                call("Version tags: tag"),
                call(""),
                call(expected_string2),
                call("Version message: older version message"),
                call("Version tags: old, tag"),
                call(""),
            ]






