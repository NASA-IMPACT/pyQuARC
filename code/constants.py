import os
import environ

DIF = "dif"
ECHO10 = "echo10"
UMM_JSON = "umm-json"

ROOT_DIR = (
    environ.Path(__file__) - 2
)

SCHEMAS_BASE_PATH = ROOT_DIR.path("schemas")
SCHEMA_EXTENSION = "json"

SCHEMA_PATHS = {
    ECHO10: SCHEMAS_BASE_PATH.path(f"{ECHO10}.{SCHEMA_EXTENSION}"),
    DIF: SCHEMAS_BASE_PATH.path(f"{DIF}.{SCHEMA_EXTENSION}"),
    UMM_JSON: SCHEMAS_BASE_PATH.path(f"{UMM_JSON}.{SCHEMA_EXTENSION}")
}
