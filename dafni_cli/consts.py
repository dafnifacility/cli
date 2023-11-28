# Timeout for requests (in seconds)
REQUESTS_TIMEOUT = 100

# Sender-Type for monitoring endpoint calls
SENDER_TYPE = "cli"

# Environment - Either 'production' or 'staging' for development purposes
ENVIRONMENT = "production"
ENVIRONMENT_DOMAIN = "secure" if ENVIRONMENT == "production" else "staging"

# URLs
DSS_API_URL = f"https://dafni-dss-dssauth.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
NIMS_API_URL = f"https://dafni-nims-api.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
NID_API_URL = f"https://dafni-nid-api.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
SEARCH_AND_DISCOVERY_API_URL = (
    f"https://dafni-search-and-discovery-api.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
)
MINIO_API_URL = f"https://minio.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"
MINIO_DOWNLOAD_REDIRECT_API_URL = (
    f"https://fwd.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk/nidminio"
)
KEYCLOAK_API_URL = f"https://keycloak.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk"

# URLs that require cookie based auth instead of header based
URLS_REQUIRING_COOKIE_AUTHENTICATION = [
    MINIO_API_URL,
    f"https://nid-minio.{ENVIRONMENT_DOMAIN}.dafni.rl.ac.uk",
]

# Keycloak realm
KEYCLOAK_API_REALM = ENVIRONMENT.capitalize()

# Specific endpoints
LOGIN_API_ENDPOINT = f"{KEYCLOAK_API_URL}/auth/realms/{KEYCLOAK_API_REALM}/protocol/openid-connect/token/"
LOGOUT_API_ENDPOINT = f"{KEYCLOAK_API_URL}/auth/realms/{KEYCLOAK_API_REALM}/protocol/openid-connect/logout"

# Authentication
SESSION_SAVE_FILE = ".dafni-cli"
SESSION_COOKIE = "__Secure-dafni"

# Time before a token expires that we should refresh the token regardless
# of any authentication errors (seconds) - 60 matches VueKeyCloak
TOKEN_EXPIRE_OFFSET = 60

# Content types
MINIO_UPLOAD_CT = "multipart/form-data"
VALIDATE_MODEL_CT = "application/yaml"

# Formatting

# ISO8601
DATE_TIME_OUTPUT_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_OUTPUT_FORMAT = "%Y-%m-%d"
DATE_INPUT_FORMAT = "%Y-%m-%d"
DATE_TIME_INPUT_FORMAT = "%Y-%m-%d %H:%M:%S"
# Same as above but for displaying to the user
DATE_INPUT_FORMAT_VERBOSE = "YYYY-MM-DD"
DATE_TIME_INPUT_FORMAT_VERBOSE = "YYYY-MM-DD HH:MM:SS"

# Tabulate arguments for table formatting
TABULATE_ARGS = {"tablefmt": "simple", "stralign": "left", "numalign": "left"}

# Table headers
TABLE_TITLE_HEADER = "Title"
TABLE_DESCRIPTION_HEADER = "Description"
TABLE_NAME_HEADER = "Name"
TABLE_TYPE_HEADER = "Type"
TABLE_MIN_HEADER = "Min"
TABLE_MAX_HEADER = "Max"
TABLE_DEFAULT_HEADER = "Default"
TABLE_REQUIRED_HEADER = "Required?"
TABLE_SLOT_NAME_HEADER = "Slot Name"
TABLE_PATH_IN_CONTAINER_HEADER = "Path in container"
TABLE_DEFAULT_DATASETS_HEADER = "Default datasets (Version IDs)"
TABLE_FORMAT_HEADER = "Format"
TABLE_SUMMARY_HEADER = "Summary"
TABLE_ID_HEADER = "ID"
TABLE_PUBLISHED_BY_HEADER = "Published by"
TABLE_PUBLISHED_DATE_HEADER = "Date published"
TABLE_WORKFLOW_VERSION_ID_HEADER = "Workflow version ID"
TABLE_PARAMETER_SET_HEADER = "Parameter set"
TABLE_STARTED_HEADER = "Started"
TABLE_FINISHED_HEADER = "Finished"
TABLE_STATUS_HEADER = "Status"
TABLE_VERSION_ID_HEADER = "Version ID"
TABLE_MODIFIED_HEADER = "Modified"
TABLE_VERSION_MESSAGE_HEADER = "Version message"
TABLE_ACCESS_HEADER = "Access"
TABLE_PUBLICATION_DATE_HEADER = "Publication date"
TABLE_VERSION_TAGS_HEADER = "Version tags"
TABLE_STEP_NAME_HEADER = "Step name"
TABLE_STEP_TYPE_HEADER = "Step type"
TABLE_ASSERT_VERSION_ID_HEADER = "Asset version ID"
TABLE_PARAMETER_HEADER = "Parameter"
TABLE_VALUE_HEADER = "Value"
TABLE_VALUES_HEADER = "Values"
TABLE_STEPS_THAT_CONTAIN_PARAMETER_HEADER = "Steps that contain parameter"
TABLE_GENERATE_VALUES_HEADER = "Generate values"
TABLE_PATH_TO_DATA_HEADER = "Path to data"
TABLE_DATASET_VERSION_IDS_HEADER = "Dataset version IDs"
TABLE_STEPS_THAT_CONTAIN_DATASLOT_HEADER = "Steps that contain dataslot"
TABLE_CONTACT_POINT_NAME = "Contact name"
TABLE_CONTACT_POINT_EMAIL = "Contact email"
TABLE_LICENCE = "Licence"
TABLE_RIGHTS = "Rights"

TABLE_DESCRIPTION_MAX_COLUMN_WIDTH = 80
TABLE_DISPLAY_NAME_MAX_COLUMN_WIDTH = 40
TABLE_SUMMARY_MAX_COLUMN_WIDTH = 60


CONSOLE_WIDTH = 120

# What to display if a data format is unknown
OUTPUT_UNKNOWN_FORMAT = "Unknown"

TAB_SPACE = "    "

# Chunk size for downloading (in bytes)
# Want it to be large enough to avoid unnecessary reading and writing but
# small enough to fit in memory and give a reasonable loading bar scale
DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB

# Maximum number of times to retry requests that have failed due to an error
REQUEST_ERROR_RETRY_ATTEMPTS = 3

# Time to wait between retry attempts when an error occurs during a
# request (seconds)
REQUEST_ERROR_RETRY_WAIT = 1

# Number of upload attempts to make when there is a problem during dataset upload
DATASET_UPLOAD_FILE_RETRY_ATTEMPTS = 3

# Data formats for datasets (See mimeTypes.js in front end)
DATA_FORMATS = {
    "audio/3gpp": "3GPP Audio",
    "video/3gpp": "3GPP Video",
    "audio/3gpp2": "3GPP2 Audio",
    "video/3gpp2": "3GPP2 Video",
    "application/x-7z-compressed": "7-zip",
    "audio/aac": "AAC",
    "application/x-abiword": "AbiWord",
    "application/x-freearc": "Archive",
    "video/x-msvideo": "AVI",
    "application/octet-stream": "Binary",
    "image/bmp": "Bitmap",
    "text/css": "CSS",
    "text/csv": "CSV",
    "application/vnd.ms-excel": "Excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "image/gif": "Gif",
    "application/gzip": "GZip",
    "text/html": "HTML",
    "image/vnd.microsoft.icon": "Icon",
    "application/java-archive": "JAR",
    "text/javascript": "JavaScript",
    "image/jpeg": "JPEG",
    "application/json": "JSON",
    "application/ld+json": "JSON-LD",
    "application/vnd.google-earth.kml+xml": "KML",
    "application/vnd.google-earth.kmz": "KMZ",
    "text/markdown": "MD",
    "audio/mpeg": "MP3",
    "video/mpeg": "MPEG",
    "application/ogg": "OGG",
    "audio/ogg": "OGG Audio",
    "video/ogg": "OGG Video",
    "audio/opus": "Opus Audio",
    "application/pdf": "PDF",
    "text/pdf": "PDF",
    "image/png": "PNG",
    "application/vnd.ms-powerpoint": "PowerPoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
    "application/vnd.oasis.opendocument.presentation": "Presentation",
    "application/postscript": "PS",
    "application/x-qgis": "QGIS",
    "application/vnd.rar": "RAR",
    "application/rtf": "RTF",
    "application/vnd.oasis.opendocument.spreadsheet": "Spreadsheet",
    "application/x-sql": "SQL",
    "image/svg+xml": "SVG",
    "application/x-tar": "TAR",
    "application/x-gzip": "TAR GZ",
    "application/vnd.oasis.opendocument.text": "Text",
    "text/plain": "Text",
    "image/tiff": "Tiff",
    "audio/wav": "WAV",
    "audio/webm": "WEBM Audio",
    "video/webm": "WEBM Video",
    "image/webp": "WEBP Image",
    "application/msword": "Word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word",
    "text/xlsx": "XLXS",
    "application/xml": "XML",
    "text/xml": "XML",
    "application/zip": "ZIP",
    "application/x-zip-compressed": "ZIP",
    "application/geo+json": "GeoJSON",
}
