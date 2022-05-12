import requests

from .base_validator import BaseValidator
from .gcmd_validator import GcmdValidator
from .utils import if_arg
from .constants import CMR_URL


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
        if type(value) == str:
            value = [value]

        validity = True
        for i in value:
            if i not in keywords_list:
                validity = False
                break

        return {
            "valid": validity,
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
    def organization_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_provider_short_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def organization_long_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_provider_long_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def organization_short_long_name_consistency_check(*args):
        received_keyword = [arg.upper().strip() for arg in args if arg]
        return {
            "valid": StringValidator.gcmdValidator.validate_provider_short_long_name_consistency(
                received_keyword
            ),
            "value": (args[0], args[1]),
        }

    @staticmethod
    @if_arg
    def instrument_short_long_name_consistency_check(*args):
        received_keyword = [arg.upper().strip() for arg in args if arg]
        return {
            "valid": StringValidator.gcmdValidator.validate_instrument_short_long_name_consistency(
                received_keyword
            ),
            "value": (args[0], args[1]),
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
    def platform_short_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_platform_short_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def platform_long_name_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_platform_long_name(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def platform_type_gcmd_check(value):
        return {
            "valid": StringValidator.gcmdValidator.validate_platform_type(
                value.upper()
            ),
            "value": value,
        }

    @staticmethod
    @if_arg
    def platform_short_long_name_consistency_check(*args):
        received_keyword = [arg.upper().strip() for arg in args if arg]
        return {
            "valid": StringValidator.gcmdValidator.validate_platform_short_long_name_consistency(
                received_keyword
            ),
            "value": (args[0], args[1]),
        }

    @staticmethod
    @if_arg
    def validate_granule_platform_against_collection(platform_shortname, collection_shortname):
        """
        Validates the platform shortname provided in the granule metadata
        against the platform shortname provided at the collection level.

        Args:
            platform_shortname (str): shortname of the platform
            collection_shortname (str): Shortname of the parent collection

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        collection  = requests.get(f'{CMR_URL}/search/collections.json?short_name={collection_shortname}&sort_key[]=platform').json()
        
        if len(collection['feed']['entry']) > 0:
            coll_data = collection['feed']['entry'][0]
            coll_platform_list = coll_data['platforms']
        return {
            "valid": platform_shortname in coll_platform_list,
            "value": platform_shortname
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
        received_keyword = [arg.upper().strip() for arg in args if arg]
        return {
            "valid": StringValidator.gcmdValidator.validate_campaign_short_long_name_consistency(
                received_keyword
            ),
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

    @staticmethod
    @if_arg
    def online_resource_type_gcmd_check(resource_type):
        return {
            "valid": StringValidator.gcmdValidator.validate_online_resource_type(
                resource_type.upper()
            ),
            "value": resource_type,
        }

    @staticmethod
    @if_arg
    def location_gcmd_check(*args):
        """
        Checks if the GCMD location keyword hierarchy is correct

        Args:
            args (list): List of the keyword in order of hierarchy
                example: ['CONTINENT', "AFRICA", "CENTRAL AFRICA", "ANGOLA", None]

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        value = None
        received_keyword = [arg.upper().strip() for arg in args if arg]
        validity, invalid_value = StringValidator.gcmdValidator.validate_location_hierarchy(
            received_keyword
        )
        if not validity:
            value = f"'{invalid_value}' in the hierarchy '{'/'.join(received_keyword)}'"
        return {"valid": validity, "value": value if value else received_keyword}

    @staticmethod
    @if_arg
    def chrono_gcmd_check(*args):
        """
        Checks if the Chrono Units keyword hierarchy is correct

        Args:
            args (list): List of the keyword in order of hierarchy
                example: ['PHANEROZOIC','CENOZOIC','QUATERNARY','PLEISTOCENE','CALABRIAN']

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        value = None
        received_keyword = [arg.upper().strip() for arg in args if arg]
        validity, invalid_value = StringValidator.gcmdValidator.validate_chrono_unit_hierarchy(
            received_keyword
        )
        if not validity:
            value = f"'{invalid_value}' in the hierarchy '{'/'.join(received_keyword)}'"
        return {"valid": validity, "value": value if value else received_keyword}

    @staticmethod
    @if_arg
    def horizontal_range_res_gcmd_check(resource_type):
        return {
            "valid": StringValidator.gcmdValidator.validate_horizontal_resolution_range(
                resource_type.upper()
            ),
            "value": resource_type,
        }

    @staticmethod
    @if_arg
    def vertical_range_res_gcmd_check(resource_type):
        return {
            "valid": StringValidator.gcmdValidator.validate_vertical_resolution_range(
                resource_type.upper()
            ),
            "value": resource_type,
        }

    @staticmethod
    @if_arg
    def temporal_range_res_gcmd_check(resource_type):
        return {
            "valid": StringValidator.gcmdValidator.validate_temporal_resolution_range(
                resource_type.upper()
            ),
            "value": resource_type,
        }

    @staticmethod
    @if_arg
    def mime_type_gcmd_check(resource_type):
        return {
            "valid": StringValidator.gcmdValidator.validate_mime_type(
                resource_type.upper()
            ),
            "value": resource_type,
        }

    @staticmethod
    @if_arg
    def idnnode_shortname_gcmd_check(resource_type):
        return {
            "valid": StringValidator.gcmdValidator.validate_idnnode_shortname(
                resource_type.upper()
            ),
            "value": resource_type,
        }
