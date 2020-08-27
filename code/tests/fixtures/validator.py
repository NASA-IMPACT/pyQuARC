import json
import os

WORKING_DIR = os.getcwd()
FIXTURE_PATH = os.path.join(WORKING_DIR, "code/tests/fixtures/")
PATH = os.path.join(
    FIXTURE_PATH, 'real_collection_validator_result.json'
)

REAL_COLLECTION_VALIDATOR_RESULT = json.load(
    open(PATH)
)
