import json
import os
import pytest

from datetime import datetime

from ..checker import Checker

from .fixtures.checker import FUNCTION_MAPPING, DUMMY_METADATA_CONTENT
from .fixtures.common import DUMMY_METADATA_FILE_PATH


class TestChecker:
    """
    Test cases for the Checker script in checker.py
    """

    def setup_method(self):
        self.checker = Checker()

    @staticmethod
    def _read_test_metadata():
        with open(os.path.join(os.getcwd(), DUMMY_METADATA_FILE_PATH), "r") as content_file:
            return content_file.read()

    def test_run(self):
        result = self.checker.run(DUMMY_METADATA_CONTENT)
        assert result['jsonschema'] and result['custom']

    def test_map_to_function(self):
        for in_, out_ in zip(
            FUNCTION_MAPPING["input"],
            FUNCTION_MAPPING["output"]
        ):
            result = self.checker.map_to_function(
                in_["datatype"], in_["function"]
            )
            assert bool(callable(result)) == out_
