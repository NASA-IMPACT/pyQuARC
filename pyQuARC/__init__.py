import os

from pyQuARC.main import ARC

from pyQuARC.code.constants import SUPPORTED_FORMATS

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

def supported_formats():
    """Returns a list of metadata formats supported by pyQuARC.
       One of the formats in the list can be passed to ARC.validate()
       Default is `echo-c`.

       "dif10": Dif10 collectioin metadata format
       "echo-c": Echo10 collection metadata format
       "umm-c": UMM json collection metadata format
       "umm-g": UMM json granule metadata format
       "echo-g": Echo10 granule metadata format

    Returns:
        list:   list of supported metadata formats
                eg: ["dif10", "echo-c", "umm-c", "umm-g", "echo-g"]
    """
    return SUPPORTED_FORMATS
