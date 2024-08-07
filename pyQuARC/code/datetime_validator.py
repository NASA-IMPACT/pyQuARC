import pytz
import re

from datetime import datetime

from .base_validator import BaseValidator
from .utils import if_arg


class DatetimeValidator(BaseValidator):
    """
    Validator class for datetime datatype
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def _iso_datetime(datetime_string):
        """
        Converts the input datetime string to iso datetime object

        Args:
            datetime_string (str): the datetime string

        Returns:
            (datetime.datetime) If the string is valid iso string, False otherwise
        """
        REGEX = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
        match_iso8601 = re.compile(REGEX).match
        try:
            if match_iso8601(datetime_string):
                if datetime_string.endswith("Z"):
                    datetime_string = datetime_string.replace("Z", "+00:00")
                value = datetime.fromisoformat(datetime_string)
                return value
        except:
            pass
        return False

    @staticmethod
    @if_arg
    def iso_format_check(datetime_string):
        """
        Performs the Date/DateTime ISO Format Check - checks if the datetime
        is valid ISO formatted datetime string

        Args:
            datetime_string (str): The datetime string

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": bool(DatetimeValidator._iso_datetime(datetime_string)),
            "value": datetime_string,
        }

    @staticmethod
    @if_arg
    def compare(first, second, relation):
        """
        Compares two datetime values based on the argument relation
        Returns:
            (dict) An object with the validity of the check and the instance
        """
        first = DatetimeValidator._iso_datetime(first)
        second = DatetimeValidator._iso_datetime(second)
        if not(second):
            second = datetime.now().replace(tzinfo=pytz.UTC) # Making it UTC for comparison with other UTC times
        result = BaseValidator.compare(first, second, relation)
        return {
            "valid": result,
            "value": (str(first), str(second))
        }
