import json
import os
import pytest

from xmltodict import parse

from vacqm.custom_checker import CustomChecker

from .fixtures.custom_checker import INPUT_OUTPUT
from .common import read_test_metadata

class TestCustomChecker:
    """
    Test cases for the CustomChecker script in custom_checker.py
    """

    def setup_method(self):
        self.custom_checker = CustomChecker()
        self.dummy_metadata = parse(read_test_metadata())

    def test_get_path_value(self):
        in_out = INPUT_OUTPUT["get_path_value"]
        for _in, _out in zip(in_out["input"], in_out["output"]):
            assert CustomChecker._get_path_value(
                self.dummy_metadata,
                _in
            ) == _out
