import os

from pyQuARC.main import ARC

from pyQuARC.code.constants import SUPPORTED_FORMATS as FORMATS

from pyQuARC.code.checker import Checker
from pyQuARC.code.downloader import Downloader

from pyQuARC.code.base_validator import BaseValidator
from pyQuARC.code.datetime_validator import DatetimeValidator
from pyQuARC.code.schema_validator import SchemaValidator
from pyQuARC.code.string_validator import StringValidator
from pyQuARC.code.url_validator import UrlValidator

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
with open(f"{ABS_PATH}/version.txt") as version_file:
    __version__ = version_file.read().strip()

def version():
    """Returns the current version of pyQuARC.
    """
    return __version__
