import json
import os
import pytest

from ..custom_checker import CustomChecker

from .fixtures.custom_checker import INPUT_OUTPUT
from .fixtures.common import DUMMY_METADATA_FILE_PATH


class TestCustomChecker:
    """
    Test cases for the CustomChecker script in custom_checker.py
    """

    def setup_method(self):
        self.custom_checker = CustomChecker()
        self.dummy_metadata = json.loads(
            TestCustomChecker._read_test_metadata()
        )

    @staticmethod
    def _read_test_metadata():
        with open(
            os.path.join(os.getcwd(), DUMMY_METADATA_FILE_PATH), "r"
        ) as content_file:
            return content_file.read()

    def test_get_path_value(self):
        # Uncomment after the gcmd_keyword_check branch has been merged
        # in_out = INPUT_OUTPUT["get_path_value"]
        # for _in, _out in zip(in_out["input"], in_out["output"]):
        #     assert CustomChecker._get_path_value(
        #         self.dummy_metadata,
        #         _in
        #     ) == _out
        pass
