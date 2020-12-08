from .base_validator import BaseValidator
from .string_validator import StringValidator


class CustomValidator(BaseValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
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
    def data_center_name_presence_check(
        archive_center, processing_center, organization_name
    ):
        result = {
            "valid": False,
        }
        if value := archive_center or processing_center or organization_name:
            result["valid"] = True
            result["value"] = value

        return result
