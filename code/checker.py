import json

from xmltodict import parse

from .custom_checker import CustomChecker
from .datetime_validator import DatetimeValidator
from .scheduler import Scheduler
from .schema_validator import SchemaValidator
from .string_validator import StringValidator
from .tracker import Tracker
from .url_validator import UrlValidator

from .constants import SCHEMA_PATHS, DIF, ECHO10, UMM_JSON


class Checker:
    """
    Handles both the structural and logical checks
    """

    def __init__(self, metadata_format=ECHO10):
        """
        Args:
            metadata_format (str): The format of the metadata
            validation_paths ([str]): A list of paths for which
            the structure of the metadata needs to be checked
        """
        self.load_schemas()

        self.custom_checker = CustomChecker()
        self.scheduler = Scheduler(self.rule_mapping)
        self.schema_validator = SchemaValidator(metadata_format)
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
        class_name = f"{data_type.title()}Validator"
        try:
            class_object = globals()[class_name]
            function_object = getattr(class_object, function)
        except AttributeError as e:
            print(f"The function {class_name}.{function} hasn't been implemented")
            return None
        return function_object

    def fields(self, rule_id):
        """
        Get the applicable fields for `rule_id`
        """
        for mapping in self.rule_mapping:
            if mapping["rule_id"] == rule_id:
                return mapping["fields_to_apply"]

    def message(self, rule_id):
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
        message = self.message(rule_id)
        if not result["valid"] and result.get("value") and message:
            value = result["value"]
            formatted_message = message
            if isinstance(value, tuple):
                formatted_message = message["failure"].format(*value)
            else:
                formatted_message = message["failure"].format(value)
            return formatted_message

    def perform_schema_check(self, xml_metadata, json_metadata):
        """
        Performs Schema check
        """
        return self.schema_validator.run(xml_metadata, json_metadata)

    def _check_dependencies_validity(self, dependencies, field_dict):
        for dependency in dependencies:
            for field in field_dict["fields"]:
                if not self.tracker.read_data(dependency, field)["valid"]:
                    return False
        return True

    def perform_custom_checks(self, metadata_content):
        """
        Performs custom checks
        """
        ordered_rule = self.scheduler.order_rules()
        result_dict = {}
        # metadata_content = json.loads(metadata_content)

        for rule_id in ordered_rule:
            result_dict.setdefault(rule_id, {})
            list_of_fields_to_apply = self.fields(rule_id)
            rule = self.checks[rule_id]
            func = Checker.map_to_function(rule["data_type"], rule["check_function"])
            dependencies = rule.get("dependencies", [])
            external_data = rule.get("data", [])
            for field_dict in list_of_fields_to_apply:
                main_field = field_dict["fields"][0]
                if self._check_dependencies_validity(dependencies, field_dict):
                    result = self.custom_checker.run(func, metadata_content, field_dict, external_data)
                    self.tracker.update_data(rule_id, main_field, result["valid"])
                    if result["valid"] != None: # this is to avoid "valid" = null in the result, for rules that are not applied
                        result_dict[rule_id][main_field] = result

                        message = self.build_message(result, rule_id)
                        if message:
                            result["message"] = message
        return result_dict

    def run(self, metadata_content):
        """
        Runs all checks on the `metadata_content`

        Args:
            metadata_content (str): The downloaded metadata content

        Returns:
            (dict): The results of the jsonschema check and all custom checks
        """
        json_metadata = parse(metadata_content)
        result = {}
        result["schema"] = self.perform_schema_check(
            metadata_content, json_metadata
        )
        result["custom"] = self.perform_custom_checks(json_metadata)
        return result
