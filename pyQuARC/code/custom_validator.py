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

        if "USE SERVICE API" in url_type:
            if mime_type:
                result = StringValidator.controlled_keywords_check(
                    mime_type, controlled_list
                )

        return result

    @staticmethod
    def availability_check(
        field_value,
        parent_value
    ):
        validity = True
        if parent_value:
            if not field_value:
                validity = False
        return {
            "valid": validity,
            "value": field_value
        }

    @staticmethod
    def bounding_coordinate_logic_check(coordinates_dictionary):
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
        validity = False
        value = None

        for field_value in field_values:
            if value := field_value and field_value.strip():
                value = field_value
                validity = True

        return {
            "valid": validity,
            "value": value
        }
