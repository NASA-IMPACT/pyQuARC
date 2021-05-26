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

GCMD_LINKS = {
    "science_keywords": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/sciencekeywords?format=csv",
    "locations": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/locations?format=csv",
    "providers": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/providers?format=csv",
    "instruments": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/instruments?format=csv",
    "projects": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/projects?format=csv",
    "granuledataformat": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/granuledataformat?format=csv",
    "platforms": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/platforms?format=csv",
    "rucontenttype": "https://gcmdservices.gsfc.nasa.gov/kms/concepts/concept_scheme/rucontenttype?format=csv"
}

CRM_URL = "https://cmr.earthdata.nasa.gov"
