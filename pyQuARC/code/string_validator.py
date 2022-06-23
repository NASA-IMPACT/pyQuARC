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
        for keyword in value:
            if keyword not in keywords_list:
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
        (
            validity,
            invalid_value,
        ) = StringValidator.gcmdValidator.validate_science_keyword(received_keyword)
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
            "valid": StringValidator.gcmdValidator.validate_data_format(value.upper()),
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
        (
            validity,
            invalid_value,
        ) = StringValidator.gcmdValidator.validate_location_hierarchy(received_keyword)
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
        (
            validity,
            invalid_value,
        ) = StringValidator.gcmdValidator.validate_chrono_unit_hierarchy(
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
    def set_cmr_prms(collection_entry_title, collection_shortname, collection_version):
        if collection_entry_title == None:
            cmr_prms = f'collections.umm_json?shortName={collection_shortname}&version={collection_version}'
        else:
            cmr_prms = f'collections.umm_json?entry_title={collection_entry_title}'
        return cmr_prms

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
        cmr_prms = StringValidator.set_cmr_prms(collection_entry_title, collection_shortname, collection_version)
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
        cmr_prms = StringValidator.set_cmr_prms(collection_entry_title, collection_shortname, collection_version)
        validity = StringValidator.granule_sensor_validate_against_collection(cmr_prms, sensor_shortname)
        return {
            "valid": validity,
            "value": sensor_shortname
        }
        
    @if_arg
    def validate_granule_data_format_against_collection(
        granule_data_format, collection_shortname=None, version=None, dataset_id=None
    ):
        """
        Validates the data format provided in the granule metadata
        against the data format provided at the collection level.

        Args:
            granule_data_format (str): data format in the collection
            collection_shortname (str): Shortname of the parent collection
            version (str):              version of the collection
            dataset_id (str):           Entry title of the parent collection

        Returns:
            (dict) An object with the validity of the check and the instance
        """

        if collection_shortname and version:
            collection = requests.get(
                f"{CMR_URL}/search/collections.json?short_name={collection_shortname}&version={version}&granule_data_format={granule_data_format}"
            ).json()
        else:
            collection = requests.get(
                f"{CMR_URL}/search/collections.json?DatasetId={dataset_id}&granule_data_format={granule_data_format}"
            ).json()

        if collection["feed"]["entry"]:
            return {"valid": True, "value": granule_data_format}
        return {"valid": False, "value": granule_data_format}
