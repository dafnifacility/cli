# Timeout for requests (in seconds)
REQUESTS_TIMEOUT = 100

# URLs
WORKFLOWS_API_URL = "https://dafni-nims-api.secure.dafni.rl.ac.uk"
MODELS_API_URL = "https://dafni-nims-api.secure.dafni.rl.ac.uk"
LOGIN_API_URL = "https://keycloak.secure.dafni.rl.ac.uk"
LOGIN_API_ENDPOINT = (
    f"{LOGIN_API_URL}/auth/realms/Production/protocol/openid-connect/token/"
)
LOGOUT_API_ENDPOINT = (
    f"{LOGIN_API_URL}/auth/realms/Production/protocol/openid-connect/logout"
)
DATA_UPLOAD_API_URL = "https://dafni-nid-api.secure.dafni.rl.ac.uk"
DISCOVERY_API_URL = "https://dafni-search-and-discovery-api.secure.dafni.rl.ac.uk"
DSS_API_URL = "https://dafni-dss-dssauth.secure.dafni.rl.ac.uk"
MINIO_API_URL = "https://minio.secure.dafni.rl.ac.uk"
DATA_DOWNLOAD_API_URL = MINIO_API_URL
DATA_DOWNLOAD_REDIRECT_API_URL = "https://fwd.secure.dafni.rl.ac.uk/nidminio"

# Authentication
SESSION_SAVE_FILE = ".dafni-cli"
SESSION_COOKIE = "__Secure-dafni"

# Content types
MINIO_UPLOAD_CT = "multipart/form-data"
VALIDATE_MODEL_CT = "application/yaml"

# Formatting

# ISO8601
DATE_TIME_OUTPUT_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_OUTPUT_FORMAT = "%Y-%m-%d"

# Tabulate arguments for table formatting
TABULATE_ARGS = {"tablefmt": "simple", "stralign": "left", "numalign": "left"}

# Model Input/Output Table Formatting
INPUT_TITLE_HEADER = "Title"
INPUT_DESCRIPTION_HEADER = "Description"
INPUT_NAME_HEADER = "Name"
INPUT_TYPE_HEADER = "Type"
INPUT_MIN_HEADER = "Min"
INPUT_MAX_HEADER = "Max"
INPUT_DEFAULT_HEADER = "Default"
INPUT_REQUIRED_HEADER = "Required?"
INPUT_SLOT_NAME_HEADER = "Slot Name"
INPUT_PATH_IN_CONTAINER_HEADER = "Path in container"
INPUT_DEFAULT_DATASETS_HEADER = "Default datasets (Version IDs)"

INPUT_DESCRIPTION_MAX_COLUMN_WIDTH = 80

OUTPUT_NAME_HEADER = "Name"
OUTPUT_FORMAT_HEADER = "Format"
OUTPUT_SUMMARY_HEADER = "Summary"

OUTPUT_SUMMARY_MAX_COLUMN_WIDTH = 80

CONSOLE_WIDTH = 120

TAB_SPACE = "    "

# Datasets
DATA_FORMATS = {
    "application/octet-stream": "Binary",
    "application/pdf": "PDF",
    "application/vnd.ms-excel": "Excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "application/zip": "ZIP",
    "text/csv": "CSV",
    "text/plain": "Text",
}
