import json

import jsonschema
import pytest
import xmltodict

from ..code.validator import Validator
from ..code.downloader import Downloader


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
        validator = Validator(content_to_validate=content_to_validate)
        schema = validator.read_schema()

        schema_dict = {
            "ShortName": {"type": "string", "min_length": 1, "max_length": 40}
        }

        assert schema == schema_dict

    def test_validate(self):
        downloader = Downloader(self.concept_ids["collection"]["real"])
        content_to_validate = downloader.download()

        validator = Validator(content_to_validate=content_to_validate)
        results_dict = validator.validate()

        expected_results_dict = {
            "ShortName": {
                "field_exists_in_downloaded_content": True,
                "valid": True,
                "errors": [],
            }
        }

        assert results_dict == expected_results_dict

    def test_validate_field_not_in_schema(self):
        pass

    def test_validate_field_in_schema_all_keys_valid(self):
        pass

    def test_validate_field_in_schema_some_keys_invalid(self):
        pass

    def test_dami_schema(self):
        content = json.load(open("code/data/damidata.json", "r"))
        schema = json.load(open("code/data/damischema.json", "r"))

        result = jsonschema.validate(
            content, schema, format_checker=jsonschema.draft7_format_checker,
        )
        assert result == None

    def test_dami_schema_xml(self):
        with open("code/data/echo10.xml", "r") as file:
            content = file.read()
        content = xmltodict.parse(content)

        validator = Validator()
        errors = validator.validate_new(content)

        # maybe we can use faker for tests
        assert errors == [
            {
                "instance": "2009-04-20",
                "message": "'2009-04-20' is not a 'date-time'",
                "path": "Collection/Temporal/RangeDateTime/BeginningDateTime",
                "validator": "format",
                "validator_value": "date-time",
            },
            {
                "instance": "21234132984132874132471241234124312423212341329841328741324712412341243124232123413298413287413247124123412431242321234132984132874132471241234124312423",
                "message": "'21234132984132874132471241234124312423212341329841328741324712412341243124232123413298413287413247124123412431242321234132984132874132471241234124312423' "
                "is too long",
                "path": "Collection > ProcessingLevelId",
                "validator": "maxLength",
                "validator_value": 80,
            },
        ]

# not in schema
# in schema
# all keys are valid
# some keys are invalid

