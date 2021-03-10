import pytest
from mock import patch, call
from datetime import datetime as dt
from dateutil import parser
from dateutil.tz import tzutc

from test.fixtures.jwt_fixtures import JWT
from test.fixtures.model_fixtures import (
    get_models_list_fixture,
    get_model_metadata_fixture,
)
from dafni_cli import model
from dafni_cli.consts import DATE_TIME_FORMAT


class TestModel:
    """Test class for the Model class"""

    class TestInit:
        """Test class to test the Model.__init__() functionality"""

        def test_expected_attributes_found_on_class(self):
            # SETUP
            expected_attributes = [
                "version_id",
                "display_name",
                "summary",
                "description",
                "creation_time",
                "publication_time",
                "version_tags",
                "container",
                "name",
                "inputs",
                "outputs",
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

    @patch("dafni_cli.model.get_single_model_dict")
    @patch.object(model.Model, "set_details_from_dict")
    class TestGetDetailsFromId:
        """Test class to test the Model.get_details_from_id() functionality"""

        def test_single_api_call_made_and_processed(
            self, mock_details, mock_get, get_models_list_fixture
        ):
            # SETUP
            model_dict = get_models_list_fixture[0]
            mock_get.return_value = model_dict

            instance = model.Model()
            jwt_string = JWT
            version_id = "version_0.1"

            # CALL
            instance.get_details_from_id(jwt_string, version_id)

            # ASSERT
            mock_get.assert_called_once_with(jwt_string, version_id)
            mock_details.assert_called_once_with(model_dict)

    @patch("dafni_cli.model.get_model_metadata_dicts")
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

            assert instance.name == get_model_metadata_fixture["metadata"]["name"]
            assert instance.inputs == get_model_metadata_fixture["spec"]["inputs"]
            assert instance.outputs == get_model_metadata_fixture["spec"]["outputs"]

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

    @patch("dafni_cli.model.click")
    class TestOutputModelDetails:
        """Test class to test the Model.output_model_details() functionality"""

        def test_model_details_outputted_correctly(self, mock_click):
            # SETUP
            instance = model.Model()
            date_time = dt(2021, 3, 3, 0, 0, 0, tzinfo=tzutc())
            instance.creation_time = date_time
            instance.display_name = "display name"
            instance.version_id = "version id"
            instance.summary = "summary"

            # CALL
            instance.output_model_details()

            # ASSERT
            assert mock_click.echo.call_args_list == [
                call(
                    "Name: display name     ID: version id     Date: 03/03/2021 00:00:00"
                ),
                call("Summary: summary"),
            ]


class TestCreateModelList:
    """Test class to test the create_model_list() functionality"""

    @patch.object(model.Model, "set_details_from_dict")
    def test_model_created_and_details_from_dict_called_for_each_model(
        self, mock_get, get_models_list_fixture
    ):
        # SETUP
        models = get_models_list_fixture

        # CALL
        result = model.create_model_list(models)

        # ASSERT
        assert mock_get.call_args_list == [call(models[0]), call(models[1])]
        assert len(result) == 2
        assert all(isinstance(instance, model.Model) for instance in result)

    def test_a_models_dict_list_is_processed_correctly(self, get_models_list_fixture):
        # SETUP
        models = get_models_list_fixture

        # CALL
        result = model.create_model_list(models)

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