import os
from colorama import Fore, Style

DIF = "dif10"
ECHO10_C = "echo-c"
UMM_C = "umm-c"
UMM_G = "umm-g"
ECHO10_G = "echo-g"

SUPPORTED_FORMATS = [DIF, ECHO10_C, UMM_C, UMM_G, ECHO10_G]

# Changed to os instead of pathlib
# https://github.com/aio-libs/aiohttp/issues/3977

ROOT_DIR = (
    # go up one directory
    os.path.abspath(os.path.join(__file__, "../.."))
)

SCHEMAS_BASE_PATH = f"{ROOT_DIR}/schemas"

GCMD_KEYWORDS = [
    "chronounits",
    "granuledataformat",
    "horizontalresolutionrange",
    "idnnode",
    "instruments",
    "locations",
    "MimeType",
    "platforms",
    "projects",
    "providers",
    "rucontenttype",
    "sciencekeywords",
    "temporalresolutionrange",
    "verticalresolutionrange",
]

SCHEMAS = {
    "json": [
        "checks",
        "check_messages",
        "check_messages_override",
        "checks_override",
        "rule_mapping",
        "rules_override",
        f"{UMM_C}-json-schema",
        "umm-cmn-json-schema",
        f"{UMM_G}-json-schema",
    ],
    "csv": GCMD_KEYWORDS,
    "xsd": [f"{DIF}_schema", f"{ECHO10_C}_schema", f"{ECHO10_G}_schema"],
    "xml": ["catalog"],
}

SCHEMA_PATHS = {
    schema: f"{SCHEMAS_BASE_PATH}/{schema}.{filetype}"
    for filetype, schemas in SCHEMAS.items()
    for schema in schemas
}

VERSION_FILE = f"{SCHEMAS_BASE_PATH}/version.txt"

COLOR = {
    "title": Fore.GREEN,
    "info": Fore.BLUE,
    "error": Fore.RED,
    "warning": Fore.YELLOW,
    "reset": Style.RESET_ALL,
    "bright": Style.BRIGHT,
}

GCMD_BASIC_URL = "https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/"

GCMD_LINKS = {
    keyword: f"{GCMD_BASIC_URL}{keyword}?format=csv"
    for keyword in GCMD_KEYWORDS
}

CMR_URL = "https://cmr.earthdata.nasa.gov"

DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%fZ",  # Year to microsecond
    "%Y-%m-%dT%H:%M:%SZ",  # Year to second
    "%Y-%m-%dT%H:%MZ",  # Year to minute
    "%Y-%m-%dT%HZ",  # Year to hour
    "%Y-%m-%d",  # Year to day
    "%Y-%m",  # Year to month
    "%Y",  # Year
]

CONTENT_TYPE_MAP = {
    UMM_C: "vnd.nasa.cmr.umm+json",
    UMM_G: "vnd.nasa.cmr.umm+json",
    ECHO10_C: "echo10+xml",
    ECHO10_G: "echo10+xml",
    DIF: "dif10+xml"
}
