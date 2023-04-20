from dafni_cli.api.datasets_api import get_all_datasets, get_latest_dataset_metadata
from dafni_cli.api.parser import ParserBaseObject
from dafni_cli.api.session import DAFNISession
from dafni_cli.datasets.dataset import Dataset
from dafni_cli.datasets.dataset_metadata import DatasetMetadata

session = DAFNISession()
data = get_latest_dataset_metadata(
    session,
    "f7fd0d12-f6c2-401a-ae7e-21fce0b3bec4",
    "0bd05eea-886a-47f3-983d-6fe47b7fd1a0",
)

print(ParserBaseObject.parse_from_dict(DatasetMetadata, data))

# data = get_all_datasets(session, {})
# print(ParserBaseObject.parse_from_dict_list(Dataset, data["metadata"])[0])
