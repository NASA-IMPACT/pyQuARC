from platform import platform
import requests
import urllib

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
    def validate_granule_instrument_against_collection(instrument_shortname, collection_shortname=None, version=None, dataset_id=None):
        """
        Validates the instrument shortname provided in the granule metadata
        against the instrument shortname provided at the collection level.

        Args:
            instrument_shortname (str): shortname of the instrument
            collection_shortname (str): Shortname of the parent collection
            version (str):              version of the collection
            dataset_id (str):           Entry title of the parent collection

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        cmr_prms = StringValidator.set_cmr_prms({"entry_title": dataset_id, "shortName": collection_shortname, 
        "version": version})
        validity = StringValidator.granule_sensor_validate_against_collection(cmr_prms, "instrument", instrument_shortname)
        return {
            "valid": validity,
            "value": instrument_shortname
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
    def validate_granule_platform_against_collection(platform_shortname, collection_shortname=None, version=None, dataset_id=None):
        """
        Validates the platform shortname provided in the granule metadata
        against the platform shortname provided at the collection level.

        Args:
            platform_shortname (str): shortname of the platform
            collection_shortname (str): Shortname of the parent collection
            version (str):              version of the collection
            dataset_id (str):           Entry title of the parent collection

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        cmr_prms = StringValidator.set_cmr_prms({"entry_title": dataset_id, "shortName": collection_shortname, 
        "version": version})
        validity = StringValidator.validate_against_collection(cmr_prms, "platform", platform_shortname)
        return {
            "valid": validity,
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

    @staticmethod
    def set_cmr_prms(params):
        base_url = "collections.umm_json?"
        params = {key:value for key, value in params.items() if value}
        return f"{base_url}{urllib.parse.urlencode(params)}"

    @staticmethod
    def granule_project_validate_against_collection(cmr_prms, project_shortname):
        if not(StringValidator.collection_in_cmr(cmr_prms)):
            validity = True
        else:
            validity = StringValidator.validate_against_collection(cmr_prms, 'project', project_shortname)
        return validity

    @staticmethod
    def collection_in_cmr(cmr_prms):
        return BaseValidator.cmr_request(cmr_prms).json()['hits'] > 0

    @staticmethod
    def validate_against_collection(cmr_prms, prm, prm_value):
        cmr_request_prms = f'{cmr_prms}&{prm}={prm_value}'
        request = BaseValidator.cmr_request(cmr_request_prms).json()['hits']
        validity = request > 0
        return validity

    @staticmethod
    @if_arg
    def granule_project_short_name_check(project_shortname, collection_entry_title=None, collection_shortname=None, collection_version=None):
        cmr_prms = StringValidator.set_cmr_prms({"entry_title": collection_entry_title, "shortName": collection_shortname, 
        "version": collection_version})
        validity = StringValidator.granule_project_validate_against_collection(cmr_prms, project_shortname)
        return {
            "valid": validity,
            "value": project_shortname
        }

    @staticmethod
    def granule_sensor_validate_against_collection(cmr_prms, sensor_shortname):
        if not(StringValidator.collection_in_cmr(cmr_prms)):
            validity = True
        else:
            validity = StringValidator.validate_against_collection(cmr_prms, 'sensor', sensor_shortname)
        return validity

    @staticmethod
    @if_arg
    def granule_sensor_short_name_check(sensor_shortname, collection_entry_title=None, collection_shortname=None, collection_version=None):
        cmr_prms = StringValidator.set_cmr_prms({"entry_title": collection_entry_title, "shortName": collection_shortname, 
        "version": collection_version})
        validity = StringValidator.granule_sensor_validate_against_collection(cmr_prms, sensor_shortname)
        return {
            "valid": validity,
            "value": sensor_shortname
        }
