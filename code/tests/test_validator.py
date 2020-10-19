import json

import jsonschema
import pytest
import xmltodict

from ..downloader import Downloader
from ..validator import DatetimeValidator

from .fixtures.validator import INPUT_OUTPUT


class TestValidator:
    """
        Test cases for the validator script in validator.py
    """

    def setup_method(self):
        pass

    def test_datetime_iso_format_check(self):
        for input_output in INPUT_OUTPUT["date_datetime_iso_format_check"]:
            assert (
                DatetimeValidator.iso_format_check(
                    input_output["input"])["valid"]
            ) == input_output["output"]

    def test_datetime_compare(self):
        pass

    def test_string_length_check(self):
        pass

    def test_string_compare(self):
        pass

    def test_processing_level_id_check(self):
        pass

    def test_url_health_check(self):
        pass

    def test_doi_check(self):
        pass
