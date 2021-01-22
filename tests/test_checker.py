import json
import os
import pytest

from datetime import datetime

from vacqm.code.checker import Checker

from .fixtures.checker import FUNCTION_MAPPING, DUMMY_METADATA_CONTENT
from .common import read_test_metadata


class TestChecker:
    """
    Test cases for the Checker script in checker.py
    """

    def setup_method(self):
        self.checker = Checker()
        self.test_metadata = read_test_metadata()

    def test_run(self):
        result = self.checker.run(self.test_metadata)
        assert result

    def test_map_to_function(self):
        for in_, out_ in zip(FUNCTION_MAPPING["input"], FUNCTION_MAPPING["output"]):
            result = self.checker.map_to_function(in_["datatype"], in_["function"])
            assert bool(callable(result)) == out_
