import csv

from .constants import SCHEMA_PATHS

from .base_validator import BaseValidator
from .gcmd_validator import GcmdValidator


class StringValidator(BaseValidator):
    """
    Validator class for string values
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def length_check(string, args):
        """
        Checks if the length of the string is valid based on the extent 
        and relation provided in the args

        Args:
            string (str): The input string
            args (list): [extent (int), relation (str)] The extent and the relation

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        extent, relation = args
        length = len(string)
        return {
            "valid": BaseValidator.compare(length, extent, relation),
            "value": length
        }

    @staticmethod
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
            "valid": str(value) in keywords_list,
            "value": value
        }
    
    @staticmethod
    def gcmd_keywords_check(*args):
        """
        Checks if the GCMD keyword hierarchy is correct

        Args:
            args (list of lists): List of lists of the keywords in order of hierarchy
                If there are multiple GCMD keywords, it'll be in the form:
                [
                    [Category_1, Category_2, ...],
                    [Topic_1, Topic_2, ...],
                    [Term_1, Term_2, ...],
                    [VariableLevel1_1, VariableLevel1_2, ...],
                    [VariableLevel2_1, VariableLevel2_2, ...],
                    [VariableLevel3_1, VariableLevel3_2, ...],
                    [DetailedVariable_1, DetailedVariable_2, ...]
                ]

        Returns:
            (dict) An object with the validity of the check and the instance
        """

        gcmdValidator = GcmdValidator()

        received_keywords = gcmdValidator.prepare_received_gcmd_keywords_list(*args)

        valid = True
        value = []

        for keyword in received_keywords:
            validity, invalid_value = gcmdValidator.validate(keyword)
            if not validity:
                valid = False
                value.append((invalid_value, '/'.join(keyword)))
        
        return {
            "valid": valid,
            "value": value if value else received_keywords
        }

    @staticmethod
    def ends_at_present_flag_logic_check(
        ends_at_present_flag,
        ending_date_time,
        collection_state
        ):
        valid = True
        if ends_at_present_flag == "true":
            if ending_date_time.strip() or collection_state == "COMPLETE":
                valid = False
        elif ends_at_present_flag == "false":
            if not ending_date_time.strip() or collection_state == "ACTIVE":
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
            if mime_type.strip():
                result = StringValidator.controlled_keywords_check(mime_type, controlled_list)
        
        return result
