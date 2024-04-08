import pytz
import re

from datetime import datetime

from .base_validator import BaseValidator
from .utils import cmr_request, if_arg, set_cmr_prms


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
    def _iso_date(date_string):
        """
        Converts the input date string to iso datetime object

        Args:
            date_string (str): the datestring

        Returns:
            (datetime.datetime) If the string is valid iso string, False otherwise
        """

        try:
            value = datetime.strptime(date_string, "%Y-%m-%d")
            return value
        except:
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
    def date_or_datetime_format_check(datetime_string):
        """
        Performs the Date/DateTime Format Check
        Checks if the datetime_string is a valid ISO date or ISO datetime string

        Args:
            datetime_string (str): The date or datetime string

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": bool(DatetimeValidator._iso_datetime(datetime_string))
            or bool(DatetimeValidator._iso_date(datetime_string)),
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
        first = (
            DatetimeValidator._iso_datetime(first) or DatetimeValidator._iso_date(first)
        ).replace(tzinfo=pytz.utc)
        second = DatetimeValidator._iso_datetime(second) or DatetimeValidator._iso_date(
            second
        )
        if not (second):
            second = datetime.now()
        second = second.replace(
            tzinfo=pytz.UTC
        )  # Making it UTC for comparison with other UTC times
        result = BaseValidator.compare(first, second, relation)
        return {"valid": result, "value": (str(first), str(second))}

    @staticmethod
    def validate_datetime_against_granules(
        datetime_string, collection_shortname, version, sort_key, time_key
    ):
        """
        Validates the collection datetime against the datetime of the last granule in the collection

        Args:
            datetime_string (str): datetime string
            collection_shortname (str): ShortName of the parent collection
            sort_key (str): choice of start_date and end_date
            time_key (str): choice of time_end and time_start
        Returns:
            (dict) An object with the validity of the check and the instance
        """
        cmr_prms = set_cmr_prms(
            {
                "short_name": collection_shortname,
                "version": version,
                "sort_key[]": sort_key,
            },
            "json",
            "granules",
        )
        granules = cmr_request(cmr_prms)

        validity = True
        last_granule_datetime = None
        date_time = None

        # Define the formats in decreasing order of precision
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # Year to microsecond
            "%Y-%m-%dT%H:%M:%S",  # Year to second
            "%Y-%m-%dT%H:%M",  # Year to minute
            "%Y-%m-%dT%H",  # Year to hour
            "%Y-%m-%d",  # Year to day
            "%Y-%m",  # Year to month
            "%Y",  # Year
        ]

        # Function to determine the precision of a datetime string
        def get_precision(dt_str):
            for fmt in formats:
                try:
                    date_time = datetime.strptime(dt_str, fmt)
                    return date_time, fmt
                except ValueError:
                    continue
            return None, False

        # Compare the precision of the two datetime strings
        # return get_precision(datetime_str1) == get_precision(datetime_str2)
        if len(granules["feed"]["entry"]) > 0:
            last_granule = granules["feed"]["entry"][0]
            last_granule_datetime = last_granule.get(time_key)
            date_time, date_time_format = get_precision(datetime_string)
            last_granule_datetime, lgd_format = get_precision(last_granule_datetime)
            validity = date_time == last_granule_datetime

        return {"valid": validity, "value": (date_time, last_granule_datetime)}

    @staticmethod
    @if_arg
    def validate_ending_datetime_against_granules(
        ending_datetime, collection_shortname, version
    ):
        """
        Validates the collection EndingDatetime against the datetime of the last granule in the collection

        Args:
            ending_datetime (str): EndingDatetime string
            collection_shortname (str): ShortName of the parent collection

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return DatetimeValidator.validate_datetime_against_granules(
            ending_datetime, collection_shortname, version, "-end_date", "time_end"
        )

    @staticmethod
    @if_arg
    def validate_beginning_datetime_against_granules(
        beginning_datetime, collection_shortname, version
    ):
        """
        Validates the collection BeginningDateTime against the datetime of the last granule in the collection

        Args:
            beginning_datetime (str): BeginningDateTime string
            collection_shortname (str): ShortName of the parent collection

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return DatetimeValidator.validate_datetime_against_granules(
            beginning_datetime,
            collection_shortname,
            version,
            "start_date",
            "time_start",
        )
