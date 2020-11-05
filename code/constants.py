import os
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
    "json": [ "echo10_json", UMM_JSON, "rule_mapping", "checks", "check_messages", "check_messages_override" ],
    "csv": [ "science_keywords", "providers", "instruments"],
    "xsd": [ "echo10_xml", DIF ],
    "xml": [ "catalog" ]
}

SCHEMA_PATHS = {
    schema: SCHEMAS_BASE_PATH / f"{schema}.{filetype}" 
        for filetype, schemas in SCHEMAS.items()
            for schema in schemas
}
