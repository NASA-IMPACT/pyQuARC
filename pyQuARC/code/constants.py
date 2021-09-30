import os

from colorama import Fore, Style
from pathlib import Path

DIF = "dif10"
ECHO10 = "echo10"
UMM_JSON = "umm-json"

ROOT_DIR = (
    # go up one directory
    Path(__file__).resolve().parents[1]
)

SCHEMAS_BASE_PATH = f"{ROOT_DIR}/schemas"

SCHEMAS = {
    "json": [
        "checks",
        "check_messages",
        "check_messages_override",
        "checks_override",
        "rule_mapping",
        "rules_override",
        UMM_JSON
    ],
    "csv": [
        "chronounits",
        "granuledataformat",
        "horizontalresolutionrange",
        "instruments",
        "locations",
        "MimeType",
        "platforms",
        "projects",
        "providers",
        "rucontenttype",
        "sciencekeywords",
        "temporalresolutionrange",
        "verticalresolutionrange"
    ],
    "xsd": [ f"{DIF}_xml", f"{ECHO10}_xml" ],
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

GCMD_BASIC_URL = "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/"

GCMD_KEYWORDS = [
    "chronounits",
    "granuledataformat",
    "horizontalresolutionrange",
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

GCMD_LINKS = {
    keyword: f"{GCMD_BASIC_URL}{keyword}?format=csv" for keyword in GCMD_KEYWORDS
}

CMR_URL = "https://cmr.earthdata.nasa.gov"
