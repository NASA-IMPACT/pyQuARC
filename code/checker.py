import json

from .custom_checker import CustomChecker
from .scheduler import Scheduler
from .schema_validator import SchemaValidator
from .tracker import Tracker
from .validator import StringValidator, UrlValidator, DatetimeValidator

from .constants import SCHEMA_PATHS, DIF, ECHO10, UMM_JSON


class Checker:
    """
    Handles both the structural and logical checks
    """

    def __init__(self, metadata_format=ECHO10, validation_paths=[]):
        """
        Args:
            metadata_format (str): The format of the metadata
            validation_paths ([str]): A list of paths for which
            the structure of the metadata needs to be checked
        """
        self.load_schemas()

        self.custom_checker = CustomChecker()
        self.scheduler = Scheduler(self.rule_mapping)
        self.schema_validator = SchemaValidator(metadata_format, validation_paths)
        self.tracker = Tracker(self.rule_mapping)

    @staticmethod
    def _json_load_schema(shema_name):
        return json.load(open(SCHEMA_PATHS[shema_name], "r"))

    def load_schemas(self):
        self.checks = Checker._json_load_schema("checks")
        self.rule_mapping = Checker._json_load_schema("rule_mapping")
        self.messages = Checker._json_load_schema("check_messages")
        self.messages_override = Checker._json_load_schema("check_messages_override")

    @staticmethod
    def map_to_function(data_type, function):
        """
        Maps the `data_type` and `function` to the corresponding function
        in the corresponding class

        Args:
            data_type (str): The data type
            function (str): The name of the function

        Returns:
            (func): The function reference
        """
        try:
            class_object = globals()[f"{data_type.title()}Validator"]
            function_object = getattr(class_object, function)
        except AttributeError as e:
            print("The function hasn't been implemented")
            return None
        return function_object

    def get_fields(self, rule_id):
        """
        Get the applicable fields for `rule_id`
        """
        for mapping in self.rule_mapping:
            if mapping["rule_id"] == rule_id:
                return mapping["fields_to_apply"]

    def get_message(self, rule_id):
        """
        Get the success, failure, warning messages for the `rule_id`
        """
        for message in self.messages_override:
            if message["check_id"] == rule_id:
                return message["message"]
        for message in self.messages:
            if message["check_id"] == rule_id:
                return message["message"]

    def build_message(self, result, rule_id):
        """
        Formats the message for `rule_id` based on the result
        """
        message = self.get_message(rule_id)
        if not result["valid"] and result.get("value") and message:
            value = result["value"]
            formatted_message = message
            if isinstance(value, tuple):
                formatted_message = message["failure"].format(*value)
            else:
                formatted_message = message["failure"].format(value)
            return formatted_message

    def perform_jsonschema_check(self, metadata_content):
        """
        Performs JSONSchema check
        """
        return self.schema_validator.run(metadata_content)

    def perform_custom_checks(self, metadata_content):
        """
        Performs custom checks
        """
        ordered_rule = self.scheduler.order_rules()
        result_dict = {}

        for rule_id in ordered_rule:
            result_dict.setdefault(rule_id, {})
            fields_to_apply = self.get_fields(rule_id)
            rule = self.checks[rule_id]
            func = Checker.map_to_function(rule["data_type"], rule["check_function"])
            dependencies = rule.get("dependencies") or []
            for field in fields_to_apply:
                main_field = field["fields"][0]
                dependency_check = True
                for dependency in dependencies:
                    if not self.tracker.read(dependency, main_field)["valid"]:
                        dependency_check = False
                if dependency_check:
                    result = self.custom_checker.run(metadata_content, field, func)
                    self.tracker.update(rule_id, main_field, result["valid"])
                if result["valid"] != None:
                    result_dict[rule_id][main_field] = result

                    message = self.build_message(result, rule_id)
                    if message:
                        result["message"] = message
        return result_dict

    def run(self, metadata_content):
        """
        Runs all checks on the `metadata_content`

        Args:
            metadata_content (dict): The downloaded metadata content

        Returns:
            (dict): The results of the jsonschema check and all custom checks
        """
        result = {}
        result["jsonschema"] = self.perform_jsonschema_check(metadata_content)
        result["custom"] = self.perform_custom_checks(metadata_content)
        return result
