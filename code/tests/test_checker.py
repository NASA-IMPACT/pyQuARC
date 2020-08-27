import json
import os
import pytest

from datetime import datetime

from ..checker import Checker

from .fixtures.checker import INPUT_OUTPUT, DUMMY_METADATA_CONTENT
from .fixtures.common import DUMMY_METADATA_FILE_PATH


class TestChecker:
    """
    Test cases for the Checker script in checker.py
    """

    def setup_method(self):
        self.checker = Checker(TestChecker._read_test_metadata())

    @staticmethod
    def _read_test_metadata():
        with open(os.path.join(os.getcwd(), DUMMY_METADATA_FILE_PATH), "r") as content_file:
            return content_file.read()

    def test_date_datetime_iso_format_check(self):
        for input_output in INPUT_OUTPUT["date_datetime_iso_format_check"]:
            assert (
                self.checker.date_datetime_iso_format_check(
                    input_output["input"], {})["valid"]
            ) == input_output["output"]

    def test_run(self):
        self.checker.run()

    def test_get_path_value(self):
        input_data = DUMMY_METADATA_CONTENT

        checker = Checker(json.dumps(input_data))

        for input_output in INPUT_OUTPUT["get_path_value"]:
            assert checker._get_path_value(
                input_output["input"]) == input_output["output"]
