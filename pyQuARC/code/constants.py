import os

from colorama import Fore, Style
from pathlib import Path

DIF = "dif"
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
        "platforms",
        "science_keywords"
    ],
    "xsd": [ DIF, "echo10_xml" ],
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

GCMD_LINKS = {
    "science_keywords": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/sciencekeywords?format=csv",
    "locations": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/locations?format=csv",
    "providers": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/providers?format=csv",
    "instruments": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/instruments?format=csv",
    "projects": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/projects?format=csv",
    "granuledataformat": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/granuledataformat?format=csv",
    "platforms": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/platforms?format=csv"
}
