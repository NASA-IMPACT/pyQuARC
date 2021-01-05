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

SCHEMAS_BASE_PATH = ROOT_DIR / "schemas"

SCHEMAS = {
    "json": [ "check_messages", "check_messages_override", "checks", "echo10_json", "rule_mapping", UMM_JSON ],
    "csv": [ "granuledataformat", "instruments", "locations", "projects", "providers", "science_keywords" ],
    "xsd": [ DIF, "echo10_xml" ],
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
