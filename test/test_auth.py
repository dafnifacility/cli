import pytest
from mock import patch, call

from dafni_cli.auth import Auth

from test.fixtures.auth_fixtures import model_auth_fixture, dataset_auth_fixture


class TestAuth:
    """Test class for the Auth class"""

    class TestInit:
        """Test class to test the Auth.__init__() functionality"""

        def test_expected_attributes_found_on_class_when_no_dict_given(self):
            # SETUP
            string_attributes = ["asset_id", "name", "reason"]
            bool_attributes = ["destroy", "read", "update", "view"]

            # CALL
            instance = Auth()
            # ASSERT
            assert isinstance(instance, Auth)
            assert all(getattr(instance, value) is None for value in string_attributes)
            assert all(getattr(instance, value) is False for value in bool_attributes)

        def test_attributes_have_expected_values_when_model_auth_dict_used(
            self, model_auth_fixture
        ):
            # SETUP
            auth_dict = model_auth_fixture
            # CALL
            instance = Auth(auth_dict)
            # ASSERT
            assert isinstance(instance, Auth)
            assert instance.asset_id == auth_dict["asset_id"]
            assert instance.destroy == auth_dict["destroy"]
            assert instance.name is None
            assert instance.read == auth_dict["read"]
            assert instance.reason == auth_dict["reason"]
            assert instance.update == auth_dict["update"]
            assert instance.view == auth_dict["view"]

        def test_attributes_have_expected_values_when_dataset_auth_dict_used(
            self, dataset_auth_fixture
        ):
            # SETUP
            auth_dict = dataset_auth_fixture
            # CALL
            instance = Auth(auth_dict)
            # ASSERT
            assert isinstance(instance, Auth)
            assert instance.asset_id is None
            assert instance.destroy == auth_dict["destroy"]
            assert instance.name == auth_dict["name"]
            assert instance.read == auth_dict["read"]
            assert instance.reason == auth_dict["reason"]
            assert instance.update == auth_dict["update"]
            assert instance.view == auth_dict["view"]

    @patch("dafni_cli.auth.check_key_in_dict")
    class TestSetDetailsFromDict:
        """Test class for auth.set_attributes_from_dict() functionality"""

        def test_check_key_in_dict_called_with_correct_arguments(self, mock_check):
            # SETUP
            instance = Auth()
            dictionary = {}

            # CALL
            instance.set_attributes_from_dict(dictionary)

            # ASSERT
            assert mock_check.call_args_list == [
                call(dictionary, ["asset_id"], default=None),
                call(dictionary, ["destroy"], default=False),
                call(dictionary, ["name"], default=None),
                call(dictionary, ["read"], default=False),
                call(dictionary, ["reason"], default=None),
                call(dictionary, ["update"], default=False),
                call(dictionary, ["view"], default=False),
            ]
