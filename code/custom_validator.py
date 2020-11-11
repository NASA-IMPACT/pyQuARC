from .base_validator import BaseValidator
from .string_validator import StringValidator


class CustomValidator(BaseValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
    def ends_at_present_flag_logic_check(
        ends_at_present_flag,
        ending_date_time,
        collection_state
    ):
        value = ends_at_present_flag.strip().lower()
        ending_date_time = ending_date_time.strip()
        collection_state = collection_state.upper().strip()

        valid = (
            (
                value == "true"
                and bool(not(ending_date_time) or collection_state == "ACTIVE"))
            or  
            (
                value == "false"
                and bool(ending_date_time or collection_state == "COMPLETE")
            )
        )

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
        if not ends_at_present_flag.strip():
            valid = ending_date_time.strip() or collection_state == "COMPLETE"

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