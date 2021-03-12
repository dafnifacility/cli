class Permissions:
    def __init__(self, permissions: dict):
        self.name = permissions["name"]
        self.view = permissions["view"]
        self.read = permissions["read"]
        self.update = permissions["update"]
        self.destroy = permissions["destroy"]
        self.reason = permissions["reason"]


class Dataset:
    def __init__(self):
        self.id = None
        self.version_id = None
        self.metadata_id = None
        self.asset_id = None
        self.title = None
        self.description = None
        self.subject = None
        self.source = None
        self.date_range_start = None
        self.date_range_end = None
        self.modified = None
        self.formats = None

    def set_from_dict(self, dataset: dict):
        self.id = dataset["id"]["dataset_uuid"]
        self.version_id = dataset["id"]["version_uuid"]
        self.metadata_id = dataset["id"]["metadata_uuid"]
        self.asset_id = dataset["id"]["asset_id"]
        self.title = dataset["title"]
        self.description = dataset["description"]
        self.subject = dataset["subject"]
        self.source = dataset["source"]
        self.date_range_start = dataset["date_range"]["begin"]
        self.date_range_end = dataset["date_range"]["end"]
        self.modified = dataset["modified_date"]
        self.formats = dataset["formats"]
        self.permissions = Permissions(dataset["auth"])
