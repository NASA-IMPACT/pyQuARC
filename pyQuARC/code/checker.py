import json

from xmltodict import parse

from .custom_checker import CustomChecker
from .schema_validator import SchemaValidator

from .scheduler import Scheduler
from .tracker import Tracker

from .custom_validator import CustomValidator
from .datetime_validator import DatetimeValidator
from .string_validator import StringValidator
from .url_validator import UrlValidator

from .constants import COLOR, DIF, ECHO10, SCHEMA_PATHS, UMM_JSON


class Checker:
    """
    Handles both the structural and logical checks
    """

    def __init__(
        self,
        metadata_format=ECHO10,
        messages_override=None,
        checks_override=None,
        rules_override=None
    ):
        """
        Args:
            metadata_format (str): The format of the metadata
            validation_paths ([str]): A list of paths for which
            the structure of the metadata needs to be checked

            messages_override ([str]): path to json with override message
            checks_override ([str]): path to json with override checks
            rules_override ([str]): path to json with override rules
            or add missing checks
        """
        self.msgs_override_file = messages_override or "check_messages_override"
        self.rules_override_file = rules_override or "rules_override"
        self.checks_override_file = checks_override or "checks_override"

        self.load_schemas()

        self.custom_checker = CustomChecker()
        self.scheduler = Scheduler(
            self.rule_mapping,
            self.rules_override,
            self.checks,
            self.checks_override
        )
        self.schema_validator = SchemaValidator(self.messages, metadata_format)
        self.tracker = Tracker(self.rule_mapping, self.rules_override)

    @staticmethod
    def _json_load_schema(schema_name):
        """
        Loads json schema file
        """
        return json.load(open(SCHEMA_PATHS.get(schema_name, schema_name), "r"))

    def load_schemas(self):
        """
        Loads all the schema files to object variables
        """
        self.checks = Checker._json_load_schema("checks")
        self.rule_mapping = Checker._json_load_schema("rule_mapping")
        self.messages = Checker._json_load_schema("check_messages")
        self.messages_override = Checker._json_load_schema(
            self.msgs_override_file
        )
        self.rules_override = Checker._json_load_schema(
            self.rules_override_file
        )
        self.checks_override = Checker._json_load_schema(
            self.checks_override_file
        )

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
        class_object = globals().get(class_name)
        if not class_object or not hasattr(class_object, function):
            print(f"The function {class_name}.{function} hasn't been implemented")
            return None
        return getattr(class_object, function)

    def message(self, rule_id, msg_type):
        """
        Gets the success, failure, warning messages for the `rule_id`
        msg_type can be any one of 'failure', 'remediation'
        """
        messages = self.messages_override.get(rule_id) or self.messages.get(rule_id)
        return messages[msg_type]

    def build_message(self, result, rule_id):
        """
        Formats the message for `rule_id` based on the result
        """
        failure_message = self.message(rule_id, "failure")
        rule_mapping = self.rules_override.get(
            rule_id
        ) or self.rule_mapping.get(rule_id)
        severity = rule_mapping.get("severity", "error")
        messages = []
        if not(result["valid"]) and result.get("value"):
            for value in result["value"]:
                formatted_message = failure_message
                value = value if isinstance(value, tuple) else (value,)
                formatted_message = failure_message.format(*value)
                formatted_message = f"{severity.title()}: {formatted_message}"
                messages.append(formatted_message)
        return messages

    def perform_schema_check(self, xml_metadata, json_metadata):
        """
        Performs Schema check
        """
        return self.schema_validator.run(xml_metadata, json_metadata)

    def _check_dependency_validity(self, dependency, field_dict):
        """
        Checks if the dependent check called `dependency` is valid
        """
        dependency_fields = field_dict["fields"] if len(dependency) == 1 else [dependency[1]]
        for field in dependency_fields:
            if not self.tracker.read_data(dependency[0], field)["valid"]:
                return False
        return True

    def _check_dependencies_validity(self, dependencies, field_dict):
        """
        Checks if the dependent checks are valid
        """
        for dependency in dependencies:
            if not self._check_dependency_validity(dependency, field_dict):
                return False
        return True

    def _run_func(self, func, rule, rule_id, metadata_content, result_dict):
        """
        Run the check function for `rule_id` and update `result_dict`
        """
        dependencies = rule.get("dependencies", [])
        external_data = rule.get("data", [])
        rule_mapping = self.rules_override.get(
            rule_id
        ) or self.rule_mapping.get(rule_id)
        list_of_fields_to_apply = rule_mapping.get("fields_to_apply")
        for field_dict in list_of_fields_to_apply:
            main_field = field_dict["fields"][0]
            result_dict.setdefault(main_field, {})
            if not self._check_dependencies_validity(dependencies, field_dict):
                continue
            result = self.custom_checker.run(
                func,
                metadata_content,
                field_dict,
                external_data
            )
            self.tracker.update_data(rule_id, main_field, result["valid"])

            # this is to avoid "valid" = null in the result, for rules that are not applied
            if result["valid"] is None:
                continue
            result_dict[main_field][rule_id] = result

            message = self.build_message(result, rule_id)
            if message:
                result["message"] = message
                result["remediation"] = self.message(rule_id, "remediation")

    def perform_custom_checks(self, metadata_content):
        """
        Performs custom checks
        """
        ordered_rule = self.scheduler.order_rules()
        result_dict = {}
        for rule_id in ordered_rule:
            rule_mapping = self.rules_override.get(
                rule_id
            ) or self.rule_mapping.get(rule_id)
            check_id = rule_mapping.get("check_id", rule_id)
            rule = self.checks_override.get(check_id) or self.checks.get(check_id)
            func = Checker.map_to_function(rule["data_type"], rule["check_function"])
            if func:
                self._run_func(func, rule, rule_id, metadata_content, result_dict)
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
        result_schema = self.perform_schema_check(
            metadata_content, json_metadata
        )
        result_custom = self.perform_custom_checks(json_metadata)
        result = {
            **result_schema, **result_custom
        }
        return result
