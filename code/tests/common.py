import os

from .fixtures.common import DUMMY_METADATA_FILE_PATH


def read_test_metadata():
    with open(
        os.path.join(os.getcwd(), DUMMY_METADATA_FILE_PATH), "r"
    ) as content_file:
        return content_file.read().encode()