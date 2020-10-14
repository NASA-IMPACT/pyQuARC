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

SCHEMAS = [
    ECHO10, DIF, UMM_JSON, "rule_mapping", "checks", "check_messages", "check_messages_override"
]

SCHEMA_PATHS = { schema: SCHEMAS_BASE_PATH / f"{schema}.json" for schema in SCHEMAS }
