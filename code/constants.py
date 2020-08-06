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
SCHEMA_EXTENSION = "json"

SCHEMA_PATHS = {
    ECHO10: SCHEMAS_BASE_PATH / f"{ECHO10}.{SCHEMA_EXTENSION}",
    DIF: SCHEMAS_BASE_PATH / f"{DIF}.{SCHEMA_EXTENSION}",
    UMM_JSON: SCHEMAS_BASE_PATH / f"{UMM_JSON}.{SCHEMA_EXTENSION}",
    "ruleset": SCHEMAS_BASE_PATH / "ruleset.json",
    "rules_mapping": SCHEMAS_BASE_PATH / "rules_mapping.json",
}
