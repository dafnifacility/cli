from dafni_cli.tests.fixtures.auth import TEST_AUTH_DATA_OBJECT
from dafni_cli.tests.fixtures.workflow_metadata import TEST_WORKFLOW_METADATA
from dafni_cli.tests.fixtures.workflow_parameter_set import TEST_WORKFLOW_PARAMETER_SET
from dafni_cli.tests.fixtures.workflow_specification import TEST_WORKFLOW_SPECIFICATION

TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "display_name": "First parameter set",
}

TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION = {
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "version_message": "Initial Workflow version",
}

TEST_WORKFLOW_INSTANCE_LIST = {
    "instance_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "submission_time": "2023-04-06T12:46:38.031244Z",
    "overall_status": "Succeeded",
    "parameter_set": TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET,
    "workflow_version": TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION,
    "finished_time": "2023-04-06T12:58:35Z",
}

TEST_WORKFLOW_INSTANCE_LIST_DEFAULT = {
    "instance_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "submission_time": "2023-04-06T12:46:38.031244Z",
    "overall_status": "Succeeded",
    "parameter_set": TEST_WORKFLOW_INSTANCE_LIST_PARAMETER_SET,
    "workflow_version": TEST_WORKFLOW_INSTANCE_LIST_WORKFLOW_VERSION,
}

TEST_WORKFLOW_INSTANCE_STEP_STATUS = {
    "finished_at": "2023-06-15T11:41:43Z",
    "started_at": "2023-06-15T11:41:33Z",
    "status": "Succeeded",
}

TEST_WORKFLOW_INSTANCE_STEP_STATUS_DEFAULT = {
    "status": "Succeeded",
}

TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET = {
    "dataset_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000b",
    "kind": "publisher",
    "metadata_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000c",
    "version_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000d",
}

TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION = {
    "api_version": "v1.0.2",
    "creation_date": "2023-06-12T15:37:23.658116Z",
    "id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "kind": "W",
    "metadata": TEST_WORKFLOW_METADATA,
    "owner": "0a0a0a0a-0a00-0a00-a000-0a0a0000000e",
    "parent": "0a0a0a0a-0a00-0a00-a000-0a0a0000000f",
    "publication_date": "2023-06-12T15:37:23.658116Z",
    "spec": TEST_WORKFLOW_SPECIFICATION,
    "version_message": "Version message",
    "version_tags": ["latest"],
}

TEST_WORKFLOW_INSTANCE = {
    "auth": TEST_AUTH_DATA_OBJECT,
    "finished_time": "2023-06-15T11:41:53Z",
    "instance_id": "0a0a0a0a-0a00-0a00-a000-0a0a0000000a",
    "overall_status": "Succeeded",
    "parameter_set": TEST_WORKFLOW_PARAMETER_SET,
    "produced_assets": {
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000a": TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET,
        "0a0a0a0a-0a00-0a00-a000-0a0a0000001a": TEST_WORKFLOW_INSTANCE_PRODUCED_ASSET,
    },
    "step_status": {
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000a": {
            "finished_at": "2023-06-15T11:41:43Z",
            "started_at": "2023-06-15T11:41:33Z",
            "status": "Succeeded",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000b": {
            "finished_at": "2023-06-15T11:39:45Z",
            "started_at": "2023-06-15T11:38:28Z",
            "status": "Succeeded",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000c": {
            "finished_at": "2023-06-15T11:41:22Z",
            "started_at": "2023-06-15T11:40:21Z",
            "status": "Succeeded",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000d": {
            "finished_at": "2023-06-15T11:41:22Z",
            "started_at": "2023-06-15T11:40:21Z",
            "status": "Failed",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000000e": {
            "finished_at": "2023-06-15T11:41:22Z",
            "started_at": "2023-06-15T11:40:21Z",
            "status": "Succeeded",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000001a": {
            "finished_at": "2023-06-15T11:41:22Z",
            "started_at": "2023-06-15T11:40:21Z",
            "status": "Succeeded",
        },
        "0a0a0a0a-0a00-0a00-a000-0a0a0000001b": {
            "finished_at": "2023-06-15T11:41:22Z",
            "started_at": "2023-06-15T11:40:21Z",
            "status": "Succeeded",
        },
        "data-retrieval-step": {
            "finished_at": "2023-06-15T11:38:06Z",
            "started_at": "2023-06-15T11:37:46Z",
            "status": "Succeeded",
        },
        "data-transfer-step": {
            "finished_at": "2023-06-15T11:40:11Z",
            "started_at": "2023-06-15T11:39:57Z",
            "status": "Succeeded",
        },
        "directory-structure-creator": {
            "finished_at": "2023-06-15T11:37:44Z",
            "started_at": "2023-06-15T11:37:21Z",
            "status": "Succeeded",
        },
    },
    "submission_time": "2023-06-15T11:37:21.660040Z",
    "workflow_version": TEST_WORKFLOW_INSTANCE_WORKFLOW_VERSION,
}
