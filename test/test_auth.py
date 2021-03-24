import pytest

from test.fixtures.auth_fixtures import (
    model_auth_fixture,
    dataset_auth_fixture
)
from dafni_cli.auth import Auth


class TestAuth:
    """Test class for the Auth class"""

    class TestInit:
        """Test class to test the Auth.__init__() functionality"""

        def test_expected_attributes_found_on_class_when_no_dict_given(self):
            # SETUP
            expected_attributes = [
                "asset_id",
                "destroy",
                "name",
                "read",
                "reason",
                "update",
                "view"
            ]
            # CALL
            instance = Auth()
            # ASSERT
            assert isinstance(instance, Auth)
            assert all(
                getattr(instance, value) is None for value in expected_attributes
            )

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