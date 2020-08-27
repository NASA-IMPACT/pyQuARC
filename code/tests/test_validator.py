import json

import jsonschema
import pytest
import xmltodict

from ..downloader import Downloader
from ..validator import Validator

from .fixtures.validator import REAL_COLLECTION_VALIDATOR_RESULT


class TestValidator:
    """
        Test cases for the validator script in validator.py
    """

    def setup_method(self):
        self.concept_ids = {
            "collection": {
                "real": "C1339230297-GES_DISC",
                "dummy": "C123456-LPDAAC_ECS",
            },
            "granule": {
                "real": "G1370895082-GES_DISC",
                "dummy": "G1000000002-CMR_PROV1",
            },
            "invalid": "asdfasdf",
        }

    def test_read_schema(self):
        downloader = Downloader(self.concept_ids["collection"]["real"])
        content_to_validate = downloader.download()
        validator = Validator()
        schema = validator.read_schema()

        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["definitions"]["RangeDateTime"]["type"] == "object"

    def test_validate(self):
        downloader = Downloader(self.concept_ids["collection"]["real"])
        content_to_validate = downloader.download()

        validator = Validator()
        results_dict = validator.validate(content_to_validate)

        assert results_dict == REAL_COLLECTION_VALIDATOR_RESULT

    def test_validate_field_not_in_schema(self):
        pass

    def test_validate_field_in_schema_all_keys_valid(self):
        pass

    def test_validate_field_in_schema_some_keys_invalid(self):
        pass
