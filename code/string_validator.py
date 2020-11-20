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
            "value": length
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
            "valid": BaseValidator.compare(first, second, relation),
            "value": (first, second)
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
            "valid": str(value).upper() in [keyword.upper() for keyword in keywords_list],
            "value": value
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
        validity, invalid_value = StringValidator.gcmdValidator.validate_science_keyword(received_keyword)
        if not validity:
            value = f"'{invalid_value}', '{'/'.join(received_keyword)}'"
        return {
            "valid": validity,
            "value": value if value else received_keyword
        }

    @staticmethod
    @if_arg
    def data_center_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_provider_short_name(value),
            "value": value
        }

    @staticmethod
    @if_arg
    def instrument_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_instrument_short_name(value),
            "value": value
        }

    @staticmethod
    @if_arg
    def instrument_long_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_instrument_long_name(value),
            "value": value
        }

    @staticmethod
    def ends_at_present_flag_logic_check(
        ends_at_present_flag,
        ending_date_time,
        collection_state
        ):
        valid = True
        if ends_at_present_flag == "true":
            if ending_date_time or collection_state == "COMPLETE":
                valid = False
        elif ends_at_present_flag == "false":
            if not ending_date_time or collection_state == "ACTIVE":
                valid = False

        return {
            "valid": valid,
            "value": ends_at_present_flag
        }

    @staticmethod
    def ends_at_present_flag_presence_check(
        ends_at_present_flag,
        ending_date_time,
        collection_state
        ):
        valid = True
        if not ends_at_present_flag:
            if ending_date_time or collection_state == "ACTIVE":
                valid = False

        return {
            "valid": valid,
            "value": ends_at_present_flag
        }

    @staticmethod
    def mime_type_check(mime_type, url_type, controlled_list):
        result = {
            "valid": True,
            "value": mime_type
        }

        if "USE SERVICE API" in url_type:
            if mime_type:
                result = StringValidator.controlled_keywords_check(mime_type, controlled_list)
        
        return result

    @staticmethod
    def data_center_name_presence_check(archive_center, processing_center, organization_name):
        if value := archive_center or processing_center or organization_name:
            result = {
                "valid": True,
                "value": value
            }
        else:
            result = {
                "valid": False,
            }

        return result
