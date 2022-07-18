import os

from colorama import Fore, Style
from pathlib import Path

DIF = "dif10"
ECHO10 = "echo10"
UMM_C = "umm-c"
UMM_G = "umm-g"

SUPPORTED_FORMATS = [DIF, ECHO10, UMM_C, UMM_G]

ROOT_DIR = (
    # go up one directory
    Path(__file__).resolve().parents[1]
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
        f"{UMM_G}-json-schema"
    ],
    "csv": GCMD_KEYWORDS,
    "xsd": [ f"{DIF}_schema", f"{ECHO10}_schema" ],
    "xml": [ "catalog" ]
}

SCHEMA_PATHS = {
    schema:  f"{SCHEMAS_BASE_PATH}/{schema}.{filetype}"
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
    "bright": Style.BRIGHT
}

GCMD_BASIC_URL = "https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/"

GCMD_LINKS = {
    keyword: f"{GCMD_BASIC_URL}{keyword}?format=csv" for keyword in GCMD_KEYWORDS
}

CMR_URL = "https://cmr.earthdata.nasa.gov"

def get_cmr_url():
    return os.environ.get("CMR_URL", CMR_URL)
