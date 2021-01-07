import csv

from .constants import SCHEMA_PATHS

from .base_validator import BaseValidator
from .gcmd_validator import GcmdValidator
from .utils import if_arg


class StringValidator(BaseValidator):
    """
    Validator class for string values
    """

    gcmdValidator = GcmdValidator()

    def __init__(self):
        super().__init__()

    @staticmethod
    @if_arg
    def length_check(string, extent, relation):
        """
        Checks if the length of the string is valid based on the extent
        and relation provided in the args

        Args:
            string (str): The input string
            args (list): [extent (int), relation (str)] The extent and the relation

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        length = len(string)
        return {
            "valid": BaseValidator.compare(length, extent, relation),
            "value": length,
        }

    @staticmethod
    @if_arg
    def compare(first, second, relation):
        """
        Compares two strings based on the relationship

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": BaseValidator.compare(first.upper(), second.upper(), relation),
            "value": (first, second),
        }

    @staticmethod
    @if_arg
    def controlled_keywords_check(value, keywords_list):
        """
        Checks if `value` is in `keywords_list`

        Args:
            value (str/int): The value of the field
            keyword_list (list): The controlled keywords list

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": str(value).upper()
            in [keyword.upper() for keyword in keywords_list],
            "value": value,
        }

    @staticmethod
    @if_arg
    def science_keywords_gcmd_check(*args):
        """
        Checks if the GCMD keyword hierarchy is correct

        Args:
            args (list): List of the keyword in order of hierarchy
                example: ['EARTH SCIENCE', "ATMOSPHERE", "ATMOSPHERIC PRESSURE", None]

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        value = None
        received_keyword = [arg.upper().strip() for arg in args if arg]
        validity, invalid_value = StringValidator.gcmdValidator.validate_science_keyword(
            received_keyword
        )
        if not validity:
            value = f"'{invalid_value}' in the hierarchy '{'/'.join(received_keyword)}'"
        return {"valid": validity, "value": value if value else received_keyword}

    @staticmethod
    @if_arg
    def data_center_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_provider_short_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def instrument_short_long_name_consistency_check(*args):
        value = None
        received_keyword = [arg.upper().strip() for arg in args if arg]
        return {
            "valid": StringValidator.gcmdValidator.validate_instrument_short_long_name_consistency(
                received_keyword
            ),
            "value": [args[0], args[1]],
        }

    @staticmethod
    @if_arg
    def instrument_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_instrument_short_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def instrument_long_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_instrument_long_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def spatial_keyword_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_spatial_keyword(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def campaign_short_long_name_consistency_check(*args):
        value = None
        received_keyword = [arg.upper().strip() for arg in args if arg]
        return {
            "valid": StringValidator.gcmdValidator.validate_campaign_short_long_name_consistency(
                received_keyword
            )[0],
            "value": (args[0], args[1]),
        }

    @staticmethod
    @if_arg
    def campaign_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_campaign_short_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def campaign_long_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_campaign_long_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def data_format_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_data_format(
                value.upper()
            ),
            "value": value,
        }
