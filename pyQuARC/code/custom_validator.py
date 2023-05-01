from .base_validator import BaseValidator
from .string_validator import StringValidator

from .utils import cmr_request, if_arg, set_cmr_prms



class CustomValidator(BaseValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
    def ends_at_present_flag_logic_check(
        ends_at_present_flag, ending_date_time, collection_state
    ):
        collection_state = collection_state.upper()
        valid = (
            ends_at_present_flag == True
            and not (ending_date_time) and collection_state == "ACTIVE"
        ) or (
            ends_at_present_flag == False
            and bool(ending_date_time) and collection_state == "COMPLETE"
        )

        return {"valid": valid, "value": ends_at_present_flag}

    @staticmethod
    def ends_at_present_flag_presence_check(
        ends_at_present_flag, ending_date_time, collection_state
    ):
        valid = True
        if ends_at_present_flag == None:
            valid = bool(ending_date_time) and collection_state == "COMPLETE"

        return {"valid": valid, "value": ends_at_present_flag}

    @staticmethod
    def mime_type_check(mime_type, url_type, controlled_list):
        """
            Checks that if the value for url_type is "USE SERVICE API",
            the mime_type should be one of the values from a controlled list
            For all other cases, the check should be valid
        """
        result = {"valid": True, "value": mime_type}
        if url_type:
            if "USE SERVICE API" in url_type:
                if mime_type:
                    result = StringValidator.controlled_keywords_check(
                        mime_type, controlled_list
                    )
                else:
                    result["valid"] = False
        return result

    @staticmethod
    def availability_check(field_value, parent_value):
        # If the parent is available, the child should be available too, else it is invalid
        return {"valid": bool(field_value) if parent_value else True, "value": parent_value}

    @staticmethod
    @if_arg
    def bounding_coordinate_logic_check(west, north, east, south):
        # Checks if the logic for coordinate values make sense
        result = {"valid": False, "value": [west, north, east, south]}
        west = float(west)
        east = float(east)
        south = float(south)
        north = float(north)

        result["valid"] = (
            (south >= -90 and south <= 90)
            and (north >= -90 and north <= 90)
            and (east >= -180 and east <= 180)
            and (west >= -180 and west <= 180)
            and (north > south)
            and (east > west)
        )
        return result

    @staticmethod
    def one_item_presence_check(*field_values):
        """
            Checks if one of the specified fields is populated
            At least one of the `field_values` should not be null
            It is basically a OneOf check
        """
        validity = False
        value = None

        for field_value in field_values:
            if field_value:
                value = field_value
                validity = True
                break

        return {"valid": validity, "value": value}
    
    @staticmethod
    def dif_standard_product_check(*field_values):
        """
        Checks if the Extended_Metadata field in the DIF schema is being 
        utilized to specify whether or not the collection is a Standard Product.
        This check is needed because DIF schema does not have a dedicated field
        for Standard Product, and the Extended_Metadata field is also utilized
        for other things.
        """
        validity = False
        value = None

        for field_value in field_values:
             if field_value:
                if 'StandardProduct' in field_value:
                    value = field_value
                    validity = True
                    break
        else:
            pass
        return {"valid": validity, "value": value}

    @staticmethod
    def granule_sensor_presence_check(sensor_values, collection_shortname=None, version=None, dataset_id=None):
        """
        Checks if sensor is provided at the granule level if provided at
        collection level
        """
        if dataset_id:
            params = {"DatasetId": dataset_id}
        else:
            params = {
                "collection_shortname": collection_shortname,
                "version": version,
            }
        prms = set_cmr_prms(params, format="umm_json")
        collections = cmr_request(prms)
        if collections := collections.get('items'):
            collection = collections[0]
            for platform in collection['umm'].get('Platforms', []):
                instruments = platform.get('Instruments', [])
                for instrument in instruments:
                    if 'ComposedOf' in instrument.keys():
                        return CustomValidator.presence_check(sensor_values)
                    
        return {
            "valid": True,
            "value": sensor_values,
        }

    @staticmethod
    @if_arg
    def user_services_check(first_name, middle_name, last_name):
        return {
            "valid": (
                first_name.lower() != 'user' or
                last_name.lower() != 'services' or 
                (middle_name and (middle_name.lower() != 'null'))
            ),
            "value": f"{first_name} {middle_name} {last_name}",
        }

    @staticmethod
    def doi_missing_reason_explanation(explanation, missing_reason, doi):
        validity = bool(doi or ((not doi) and missing_reason and explanation))
        return {
            "valid": validity,
            "value": explanation
        }

    @staticmethod
    @if_arg
    def boolean_check(field_value):
        # Checks if the value is a boolean, basically 'true' or 'false' or their case variants
        return {"valid": field_value.lower() in ["true", "false"], "value": field_value}

    @staticmethod
    @if_arg
    def collection_progress_consistency_check(
        collection_state, ends_at_present_flag, ending_date_time
    ):
        # Logic: https://github.com/NASA-IMPACT/pyQuARC/issues/61
        validity = False
        collection_state = collection_state.upper()
        ends_at_present_flag = str(ends_at_present_flag).lower() if ends_at_present_flag else None

        if collection_state in ["ACTIVE", "IN WORK"]:
            validity = (not ending_date_time) and (ends_at_present_flag == "true")
        elif collection_state == "COMPLETE":
            validity = ending_date_time and (
                not ends_at_present_flag or (
                    ends_at_present_flag == "false"
                )
            )
        
        return {
            "valid": validity,
            "value": collection_state
        }
    
    @staticmethod
    @if_arg
    def uniqueness_check(list_of_objects, key):
        seen, duplicates = set(), set()
        if isinstance(list_of_objects, list):
            for url_obj in list_of_objects:
                if (description := url_obj.get(key)) in seen:
                    duplicates.add(description)
                else:
                    seen.add(description)
        return {
            "valid": not bool(duplicates),
            "value": ', '.join(duplicates)
        }

    @staticmethod
    def get_data_url_check(related_urls, key):
        """Checks if the related_urls contains a "GET DATA" url

        Args:
            related_urls (dict): The related_urls field of the object
                Example: [
                    {
                        "Description": "The LP DAAC product page provides information on Science Data Set layers and links for user guides, ATBDs, data access, tools, customer support, etc.",
                        "URLContentType": "CollectionURL",
                        "Type": "DATA SET LANDING PAGE",
                        "URL": "https://doi.org/10.5067/MODIS/MOD13Q1.061"
                    }, ...
                ] or
                [
                    {
                        "Description": "The LP DAAC product page provides information on Science Data Set layers and links for user guides, ATBDs, data access, tools, customer support, etc.",
                        "URL_Content_Type": {
                            "Type": "GET DATA",
                            "Subtype>: "LAADS"  
                        },
                        "URL": "https://doi.org/10.5067/MODIS/MOD13Q1.061",
                        ...
                    }, ...
                ]
            key (list): The hierarchical list of keys
                Example: ["Type"]
                or
                ["URL_Content_Type", "Type"]
        """
        return_obj = { 'valid': False, 'value': 'N/A' }
        for url_obj in related_urls:
            type = url_obj.get(key[0])
            if len(key) == 2:
                type = (type or {}).get(key[1])
            if (validity := type == "GET DATA") and (url := url_obj.get("URL")):
                return_obj['valid'] = validity
                return_obj['value'] = url
                break
        return return_obj

    @staticmethod
    @if_arg
    def count_check(count, values, key):
        items = values.get(key, [])
        if not isinstance(items, list):
            items = [items]
        num_items = len(items)
        return {
            "valid": int(count) == num_items,
            "value": (count, num_items)
        }
