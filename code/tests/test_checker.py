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
        self.checker = Checker()

    @staticmethod
    def _read_test_metadata():
        with open(os.path.join(os.getcwd(), DUMMY_METADATA_FILE_PATH), "r") as content_file:
            return content_file.read()

    def test_run(self):
        self.checker.run(DUMMY_METADATA_CONTENT)
