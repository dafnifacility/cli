from typing import List

from dafni_cli.tests.fixtures.auth import TEST_AUTH_DATA_OBJECT, TEST_AUTH_DATA_OBJECTS
from dafni_cli.tests.fixtures.model_inputs import TEST_MODEL_INPUTS
from dafni_cli.tests.fixtures.model_outputs import TEST_MODEL_OUTPUTS

# Below follows example response data from the API for getting a models
# Values labelled with MODELS implies the responses are for the /models
# endpoint rather than the /model/<version_id> one and
# values labelled with _DEFAULT implies they do not define optional variables
# and are used to test the values still parse correctly
TEST_MODEL_METADATA: dict = {
    "description": "Test description",
    "display_name": "Some display name",
    "name": "test-name",
    "publisher": "Joel Davies",
    "summary": "For testing",
    "source_code": "https://github.com/dafnifacility/cli",
    "status": "F",
    "contact_point_name": "Lorem Ipsum",
    "contact_point_email": "lorem.ipsum@example.com",
    "licence": "https://creativecommons.org/licenses/by/4.0/",
    "rights": "Open",
}

# Data for a model from the /models endpoint
TEST_MODEL_DATA_MODELS_ENDPOINT: dict = {
    "auth": TEST_AUTH_DATA_OBJECTS,
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "kind": "M",
    "display_name": "Test Display Name",
    "name": "test-name",
    "summary": "Test summary",
    "creation_date": "2019-07-17T13:33:13.751682Z",
    "publication_date": "2020-04-02T09:12:25.989915Z",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_tags": ["latest"],
    "version_message": "",
    "status": "L",
    "type": "model",
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "version_history": [
        {
            "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
            "version_tags": ["latest"],
            "publication_date": "2020-04-02T09:12:25.989915Z",
            "version_message": "First version",
        }
    ],
    "contact_point_name": "Lorem Ipsum",
    "contact_point_email": "lorem.ipsum@example.com",
    "licence": "https://creativecommons.org/licenses/by/4.0/",
    "rights": "Open",
}

TEST_MODELS: List[dict] = [TEST_MODEL_DATA_MODELS_ENDPOINT]

TEST_MODEL_SPEC: dict = {
    "image": "some/image/url",
    "inputs": TEST_MODEL_INPUTS,
    "command": ["python", "some_script.py"],
    "outputs": TEST_MODEL_OUTPUTS,
}

TEST_MODEL_SPEC_DEFAULT: dict = {}

TEST_MODEL: dict = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "version_history": [
        {
            "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
            "version_tags": ["latest"],
            "publication_date": "2020-04-02T09:12:25.989915Z",
            "version_message": "First version",
        }
    ],
    "auth": TEST_AUTH_DATA_OBJECT,
    "metadata": TEST_MODEL_METADATA,
    "api_version": "v1beta2",
    "kind": "M",
    "creation_date": "2019-07-17T13:33:13.751682Z",
    "publication_date": "2020-04-02T09:12:25.989915Z",
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "version_tags": ["latest"],
    "version_message": "",
    "container": "some/url",
    "container_version": "nims",
    "ingest_completed_date": None,
    "spec": TEST_MODEL_SPEC,
    "type": "model",
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
}
