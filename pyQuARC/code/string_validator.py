from .base_validator import BaseValidator
from .gcmd_validator import GcmdValidator
from .utils import cmr_request, collection_in_cmr, if_arg, set_cmr_prms


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
    def instrument_long_name_presence_check(*args):
        if not args[1]:
            return {
                "valid": StringValidator.gcmdValidator.validate_instrument_long_name_presence(
                    args[0].upper()
                ),
                "value": args[0],
            }
        else:
            return {
                "valid": True,
                "value": args[0],
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
    def platform_long_name_presence_check(*args):
        if not args[1]:
            return {
                "valid": StringValidator.gcmdValidator.validate_platform_long_name_presence(
                    args[0].upper()
                ),
                "value": args[0],
            }
        else:
            return {
                "valid": True,
                "value": args[0],
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
    def _validate_against_collection(prm_value, entry_title, short_name, version, key):
        cmr_prms = set_cmr_prms({
            "entry_title": entry_title,
            "short_name": short_name,
            "version": version
        }, "umm_json")

        if not (collection_in_cmr(cmr_prms)):
            return True

        cmr_request_prms = f'{cmr_prms}&{key}={prm_value}'
        hits = cmr_request(cmr_request_prms).get('hits', 0)
        return hits > 0

    @staticmethod
    @if_arg
    def granule_project_short_name_check(project_shortname, entry_title=None, short_name=None, version=None):
        validity = StringValidator._validate_against_collection(project_shortname, entry_title, short_name, version, 'project')
        return {
            "valid": validity,
            "value": project_shortname
        }

    @staticmethod
    @if_arg
    def granule_sensor_short_name_check(sensor_shortname, entry_title=None, short_name=None, version=None):
        validity = StringValidator._validate_against_collection(sensor_shortname, entry_title, short_name, version, 'instrument')
        return {
            "valid": validity,
            "value": sensor_shortname
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
        validity = StringValidator._validate_against_collection(instrument_shortname, dataset_id, collection_shortname, version, "instrument")
        return {
            "valid": validity,
            "value": instrument_shortname
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
        validity = StringValidator._validate_against_collection(platform_shortname, dataset_id, collection_shortname, version, "platform")
        return {
            "valid": validity,
            "value": platform_shortname
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
            params = {
                "short_name": collection_shortname,
                "version": version,
            }
        else:
            params = {
                "DatasetId": dataset_id,
            }

        params["granule_data_format"] = granule_data_format

        query_string = set_cmr_prms(params, "json")
        collection = cmr_request(query_string)
            
        if collection["feed"]["entry"]:
            return {"valid": True, "value": granule_data_format}
        return {"valid": False, "value": granule_data_format}
