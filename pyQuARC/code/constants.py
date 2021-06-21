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

SCHEMAS_BASE_PATH = ROOT_DIR / "schemas"

SCHEMAS = {
    "json": [
        "checks",
        "check_messages",
        "check_messages_override",
        "checks_override",
        "echo10_json",
        "rule_mapping",
        "rules_override",
        UMM_JSON
    ],
    "csv": [
        "granuledataformat",
        "instruments",
        "locations",
        "projects",
        "providers",
        "science_keywords"
    ],
    "xsd": [ f"{DIF}_xml", "echo10_xml" ],
    "xml": [ "catalog" ]
}

SCHEMA_PATHS = {
    schema: SCHEMAS_BASE_PATH / f"{schema}.{filetype}"
        for filetype, schemas in SCHEMAS.items()
            for schema in schemas
}

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
    "granuledataformat",
    "instruments",
    "locations",
    "platforms",
    "projects",
    "providers",
    "rucontenttype",
    "science_keywords"
]

GCMD_LINKS = {
    keyword: f"{GCMD_BASIC_URL}{keyword}?format=csv" for keyword in GCMD_KEYWORDS
}

CMR_URL = "https://cmr.earthdata.nasa.gov"
