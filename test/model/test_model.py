import pytest
from mock import patch, call, MagicMock, PropertyMock, Mock
from datetime import datetime as dt
from dateutil.tz import tzutc

from test.fixtures.jwt_fixtures import JWT
from test.fixtures.model_fixtures import (
    get_models_list_fixture,
    get_single_model_fixture,
    get_model_metadata_fixture,
)
from dafni_cli.model import model
from dafni_cli.consts import DATE_TIME_FORMAT, CONSOLE_WIDTH, TAB_SPACE


class TestModel:
    """Test class for the Model class"""

    class TestInit:
        """Test class to test the Model.__init__() functionality"""

        def test_expected_attributes_found_on_class(self):
            # SETUP
            expected_attributes = [
                "container",
                "creation_time",
                "description",
                "dictionary",
                "display_name",
                "metadata",
                "publication_time",
                "summary",
                "version_id",
                "version_message",
                "version_tags",
            ]
            # CALL
            instance = model.Model()
            # ASSERT
            assert isinstance(instance, model.Model)
            assert all(
                getattr(instance, value) is None for value in expected_attributes
            )

        def test_version_id_set_if_identifier_given(self):
            # SETUP
            version_id = "model_1"
            # CALL
            instance = model.Model(identifier=version_id)
            # ASSERT
            assert instance.version_id == version_id

    class TestSetDetailsFromDict:
        """Test class to test the Model.get_details_from_dict() functionality"""

        def test_non_date_fields_set_correctly(self, get_models_list_fixture):
            # SETUP
            instance = model.Model()
            model_dict = get_models_list_fixture[0]

            # CALL
            instance.set_details_from_dict(model_dict)

            # ASSERT
            assert instance.dictionary == model_dict
            assert instance.display_name == model_dict["name"]
            assert instance.summary == model_dict["summary"]
            assert instance.description == model_dict["description"]
            assert instance.version_id == model_dict["id"]
            assert instance.version_tags == model_dict["version_tags"]
            assert instance.container == model_dict["container"]

        def test_ISO_dates_are_converted_to_datetime(self, get_models_list_fixture):
            # SETUP
            instance = model.Model()
            model_dict = get_models_list_fixture[0]

            # CALL
            instance.set_details_from_dict(model_dict)

            # ASSERT
            assert instance.creation_time == dt(2021, 1, 1, tzinfo=tzutc())
            assert instance.publication_time == dt(2021, 1, 2, tzinfo=tzutc())

    @patch("dafni_cli.model.model.get_single_model_dict")
    @patch.object(model.Model, "set_details_from_dict")
    class TestGetDetailsFromId:
        """Test class to test the Model.get_details_from_id() functionality"""

        def test_single_api_call_made_and_processed(
            self, mock_details, mock_get, get_single_model_fixture
        ):
            # SETUP
            model_dict = get_single_model_fixture
            mock_get.return_value = model_dict

            instance = model.Model()
            jwt_string = JWT
            version_id = "version_0.1"

            # CALL
            instance.get_details_from_id(jwt_string, version_id)

            # ASSERT
            mock_get.assert_called_once_with(jwt_string, version_id)
            mock_details.assert_called_once_with(model_dict)

    @patch("dafni_cli.model.model.get_model_metadata_dict")
    class TestGetMetadata:
        """Test class to test the Model.get_metadata() functionality"""

        def test_single_api_call_made_and_metadata_processed(
            self, mock_get, get_model_metadata_fixture
        ):
            # SETUP
            mock_get.return_value = get_model_metadata_fixture

            jwt_string = JWT
            instance = model.Model()
            instance.version_id = "version_1"

            # CALL
            instance.get_metadata(jwt_string)

            # ASSERT
            mock_get.assert_called_once_with(jwt_string, instance.version_id)
            assert isinstance(instance.metadata, model.ModelMetadata)

    class TestFilterByDate:
        """Test class to test the Model.filter_by_date() functionality"""

        @pytest.mark.parametrize(
            "date, expected",
            [
                ("3/3/2021", True),
                ("2/3/2021", True),
                ("4/3/2021", False),
                ("03/03/2021", True),
                ("02/03/2021", True),
                ("04/03/2021", False),
            ],
        )
        @pytest.mark.parametrize(
            "key",
            [
                "creation",
                "publication",
                "CREATION",
                "PUBLICATION",
                "CrEaTiOn",
                "PuBlIcAtIoN",
            ],
        )
        def test_models_filtered_correctly_for_given_date(self, key, date, expected):
            #  SETUP
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.publication_time = date_time
            # CALL
            result = instance.filter_by_date(key, date)
            # ASSERT
            assert result is expected

        @pytest.mark.parametrize("key", ["CREATE", "PUBLICATE", "key"])
        def test_key_error_raised_for_invalid_key(self, key):
            # SETUP
            date = "04/03/2021"
            instance = model.Model()

            # CALL
            # ASSERT
            with pytest.raises(KeyError, match="Key should be CREATION or PUBLICATION"):
                instance.filter_by_date(key, date)

        @pytest.mark.parametrize("date", ["2021/4/3", "4/13/2021", "29/2/2021"])
        def test_exception_raised_for_invalid_date(self, date):
            # SETUP
            key = "creation"
            instance = model.Model()

            # CALL
            # ASSERT
            with pytest.raises(ValueError):
                instance.filter_by_date(key, date)

    @patch("dafni_cli.model.model.click")
    class TestOutputModelDetails:
        """Test class to test the Model.output_details() functionality"""

        def test_model_details_outputted_correctly(self, mock_click):
            # SETUP
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.version_id = "version id"
            instance.summary = "summary"

            # CALL
            instance.output_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(
                    "Name: display name"
                    + TAB_SPACE
                    + "ID: version id"
                    + TAB_SPACE
                    + "Date: March 03 2021"
                ),
                call("Summary: summary"),
                call(""),
            ]

        @patch("dafni_cli.model.model.prose_print")
        def test_model_details_outputted_correctly_with_description_when_long_option_used(
            self, mock_prose, mock_click
        ):
            # SETUP
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.version_id = "version id"
            instance.summary = "summary"
            instance.description = "description"

            # CALL
            instance.output_details(long=True)

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(
                    "Name: display name"
                    + TAB_SPACE
                    + "ID: version id"
                    + TAB_SPACE
                    + "Date: March 03 2021"
                ),
                call("Summary: summary"),
                call("Description: "),
                call(""),
            ]
            assert mock_prose.called_once_with("description", CONSOLE_WIDTH)

    @patch("dafni_cli.model.model.click")
    @patch("dafni_cli.model.model.prose_print")
    class TestOutputModelMetadataDetails:
        """Test class to test the Model.output_metadata() functionality"""

        def test_output_correct_when_all_keys_present(self, mock_prose, mock_click):
            # SETUP
            # mock outputs from metadata
            metadata = MagicMock()
            mock_inputs = PropertyMock(return_value=True)
            mock_outputs = PropertyMock(return_value=True)
            mock_param_table = Mock(return_value="params")
            mock_dataslots = Mock(return_value="dataslots")
            mock_output_table = Mock(return_value="outputs")
            type(metadata).inputs = mock_inputs
            type(metadata).outputs = mock_outputs
            type(metadata).format_parameters = mock_param_table
            type(metadata).format_dataslots = mock_dataslots
            type(metadata).format_outputs = mock_output_table
            # mock model
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.summary = "summary"
            instance.description = "description"
            instance.metadata = metadata

            # CALL
            instance.output_metadata()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("Name: display name"),
                call("Date: March 03 2021"),
                call("Summary: "),
                call("summary"),
                call("Description: "),
                call(""),
                call("Input Parameters: "),
                call("params"),
                call("Input Data Slots: "),
                call("dataslots"),
                call("Outputs: "),
                call("outputs"),
            ]
            assert mock_prose.called_once_with("description", CONSOLE_WIDTH)

        def test_output_correct_when_inputs_present_but_not_outputs(
            self, mock_prose, mock_click
        ):
            # SETUP
            # mock outputs from metadata
            metadata = MagicMock()
            mock_inputs = PropertyMock(return_value=True)
            mock_outputs = PropertyMock(return_value=False)
            mock_param_table = Mock(return_value="params")
            mock_dataslots = Mock(return_value="dataslots")
            mock_output_table = Mock(return_value="outputs")
            type(metadata).inputs = mock_inputs
            type(metadata).outputs = mock_outputs
            type(metadata).format_parameters = mock_param_table
            type(metadata).format_dataslots = mock_dataslots
            type(metadata).format_outputs = mock_output_table
            # mock model
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.summary = "summary"
            instance.description = "description"
            instance.metadata = metadata

            # CALL
            instance.output_metadata()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("Name: display name"),
                call("Date: March 03 2021"),
                call("Summary: "),
                call("summary"),
                call("Description: "),
                call(""),
                call("Input Parameters: "),
                call("params"),
                call("Input Data Slots: "),
                call("dataslots"),
            ]
            assert mock_prose.called_once_with("description", CONSOLE_WIDTH)

        def test_output_correct_when_outputs_present_but_not_inputs(
            self, mock_prose, mock_click
        ):
            # SETUP
            # mock outputs from metadata
            metadata = MagicMock()
            mock_inputs = PropertyMock(return_value=False)
            mock_outputs = PropertyMock(return_value=True)
            mock_param_table = Mock(return_value="params")
            mock_dataslots = Mock(return_value="dataslots")
            mock_output_table = Mock(return_value="outputs")
            type(metadata).inputs = mock_inputs
            type(metadata).outputs = mock_outputs
            type(metadata).format_parameters = mock_param_table
            type(metadata).format_dataslots = mock_dataslots
            type(metadata).format_outputs = mock_output_table
            # mock model
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.summary = "summary"
            instance.description = "description"
            instance.metadata = metadata

            # CALL
            instance.output_metadata()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("Name: display name"),
                call("Date: March 03 2021"),
                call("Summary: "),
                call("summary"),
                call("Description: "),
                call(""),
                call("Outputs: "),
                call("outputs"),
            ]
            assert mock_prose.called_once_with("description", CONSOLE_WIDTH)

        def test_output_correct_when_neither_inputs_nor_outputs_are_present(
            self, mock_prose, mock_click
        ):
            # SETUP
            # mock outputs from metadata
            metadata = MagicMock()
            mock_inputs = PropertyMock(return_value=False)
            mock_outputs = PropertyMock(return_value=False)
            mock_param_table = Mock(return_value="params")
            mock_dataslots = Mock(return_value="dataslots")
            mock_output_table = Mock(return_value="outputs")
            type(metadata).inputs = mock_inputs
            type(metadata).outputs = mock_outputs
            type(metadata).format_parameters = mock_param_table
            type(metadata).format_dataslots = mock_dataslots
            type(metadata).format_outputs = mock_output_table
            # mock model
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.summary = "summary"
            instance.description = "description"
            instance.metadata = metadata

            # CALL
            instance.output_metadata()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call("Name: display name"),
                call("Date: March 03 2021"),
                call("Summary: "),
                call("summary"),
                call("Description: "),
                call(""),
            ]
            assert mock_prose.called_once_with("description", CONSOLE_WIDTH)
