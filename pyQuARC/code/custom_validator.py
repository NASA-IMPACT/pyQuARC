from .base_validator import BaseValidator
from .string_validator import StringValidator

from .utils import if_arg


class CustomValidator(BaseValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
    @if_arg
    def ends_at_present_flag_logic_check(
        ends_at_present_flag, ending_date_time, collection_state
    ):
        value = ends_at_present_flag.lower()
        collection_state = collection_state.upper()

        valid = (
            value == "true"
            and not (ending_date_time) or collection_state == "ACTIVE"
        ) or (
            value == "false"
            and ending_date_time or collection_state == "COMPLETE"
        )

        return {"valid": valid, "value": ends_at_present_flag}

    @staticmethod
    def ends_at_present_flag_presence_check(
        ends_at_present_flag, ending_date_time, collection_state
    ):
        valid = True
        if not ends_at_present_flag:
            valid = ending_date_time or collection_state == "COMPLETE"

        return {"valid": valid, "value": ends_at_present_flag}

    @staticmethod
    def mime_type_check(mime_type, url_type, controlled_list):
        result = {"valid": True, "value": mime_type}
        # The check checks that if the value for url_type is "USE SERVICE API",
        # the mime_type should be one of the values from a controlled list
        # For all other cases, the check should be valid
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
    def availability_check(
        field_value,
        parent_value
    ):
        # If the parent is available, the child should be available too, else it is invalid
        validity = True
        if parent_value:
            if not field_value:
                validity = False
        return {
            "valid": validity,
            "value": parent_value
        }

    @staticmethod
    def bounding_coordinate_logic_check(coordinates_dictionary):
        # Checks if the logic for coordinate values make sense
        coordinates_dictionary = coordinates_dictionary or {}
        coordinates = [
                "WestBoundingCoordinate",
                "EastBoundingCoordinate",
                "NorthBoundingCoordinate",
                "SouthBoundingCoordinate"
            ]

        result = {
            "valid": False,
            "value": ""
        }

        values = {
            coordinate: int(coordinates_dictionary.get(coordinate, 0))
            for coordinate in coordinates
        }

        result["valid"] = (
            (values["NorthBoundingCoordinate"] > values["SouthBoundingCoordinate"])
            and
            (values["EastBoundingCoordinate"] > values["WestBoundingCoordinate"])
        )

        return result

    @staticmethod
    def presence_check(*field_values):
        """
            Checks if one of the field has a value
        """
        # At least one of all the fields should have a value
        # It is basically a OneOf check
        validity = False
        value = None

        for field_value in field_values:
            if field_value:
                value = field_value
                validity = True

        return {
            "valid": validity,
            "value": value
        }

    @staticmethod
    @if_arg
    def opendap_url_location_check(field_value):
        # The field shouldn't have a opendap url
        return {
            "valid": 'opendap' not in field_value.lower(),
            "value": field_value
        }

    @staticmethod
    @if_arg
    def user_services_check(first_name, middle_name, last_name):
        return {
            "valid": not (first_name.lower() == 'user' and last_name.lower() == 'services' and (not middle_name)),
            "value": f'{first_name} {last_name}'
        }

    @staticmethod
    def doi_missing_reason_explanation(explanation, missing_reason, doi):
        return {
            "valid": not((not doi) and (missing_reason) and (not explanation)),
            "value": explanation
        }

    @staticmethod
    @if_arg
    def boolean_check(field_value):
        # Checks if the value is a boolean, basically one of 'true' or 'false'
        return {
            "valid": field_value.lower() in ["true", "false"],
            "value": field_value
        }

    @staticmethod
    @if_arg
    def collection_progress_consistency_check(collection_state, ends_at_present_flag, ending_date_time):
        # Logic: https://github.com/NASA-IMPACT/pyQuARC/issues/61
        validity = True
        if collection_state.upper() in ["ACTIVE", "IN WORK"]:
            validity = (not bool(ending_date_time)) and ends_at_present_flag.lower() == "true"
        elif collection_state.upper() == "COMPLETE":
            validity = bool(ending_date_time) and (not bool(ends_at_present_flag) or ends_at_present_flag.lower() == "false")
        else:
            validity = False
        return {
            "valid": validity,
            "value": collection_state
        }

    @staticmethod
    @if_arg
    def characteristic_name_uniqueness_check(characteristics):
        seen, duplicates = set(), set()
        for characteristic in characteristics['Characteristic']:
            name = characteristic['Name']
            if name in seen:
                duplicates.add(name)
            else:
                seen.add(name)

        return {
            "valid": not bool(duplicates),
            "value": ', '.join(duplicates)
        }

    @staticmethod
    def get_data_url_check(metadata_json):
        required_type = 'GET DATA'
        related_urls = metadata_json.get('Related_URL', [])
        validity = False
        value = None
        for url in related_urls:
            if (url_type := url.get('URL_Content_Type', {}).get('Type')) and \
                url_type.upper() == required_type:
                validity = True
                value = url_type
                break

        return {
            "valid": validity,
            "value": value
        }
