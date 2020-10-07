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
    "rules_mapping": SCHEMAS_BASE_PATH / "rules_mapping.json",
    "rule_mapping": SCHEMAS_BASE_PATH / "rule_mapping.json",
    "checks": SCHEMAS_BASE_PATH / "checks.json",
    "check_messages": SCHEMAS_BASE_PATH / "check_messages.json",
    "check_messages_override": SCHEMAS_BASE_PATH / "check_messages_override.json",
    "science_keywords": SCHEMAS_BASE_PATH / "science_keywords.csv"
}
