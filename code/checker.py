import json

from .custom_checker import CustomChecker
from .scheduler import Scheduler
from .schema_validator import SchemaValidator
from .tracker import Tracker
from .validator import StringValidator, UrlValidator, DatetimeValidator

from .constants import SCHEMA_PATHS


class Checker:
    def __init__(self, metadata_format, validation_paths):
        self.checks = json.load(
            open(SCHEMA_PATHS["checks"], "r")
            )
        self.rule_mapping = json.load(
            open(SCHEMA_PATHS["rule_mapping"], "r")
            )

        self.custom_checker = CustomChecker(self.rule_mapping, self.checks)
        self.scheduler = Scheduler(self.rule_mapping)
        self.schema_validator = SchemaValidator(metadata_format, validation_paths)
        self.tracker = Tracker(self.rule_mapping)
        self.messages = json.load(
            open(SCHEMA_PATHS["check_messages"], "r")
            )
        self.messages_override = json.load(
            open(SCHEMA_PATHS["check_messages_override"], "r")
            )

    @staticmethod
    def map_to_function(data_type, function):
        class_object = globals()[f"{data_type.title()}Validator"]
        function_object = getattr(class_object, function)
        return function_object

    def get_fields(self, rule_id):
        for mapping in self.rule_mapping:
            if mapping["rule_id"] == rule_id:
                return mapping["fields_to_apply"]

    def get_rule_ordering(self):
        return self.scheduler.order_rules()

    def get_message(self, rule_id):
        for message in self.messages_override:
            if message["check_id"] == rule_id:
                return message["message"]
        for message in self.messages:
            if message["check_id"] == rule_id:
                return message["message"]

    def build_message(self, result, rule_id):
        message = self.get_message(rule_id)
        if not result["valid"] and result.get("value") and message:
            value = result["value"]
            if isinstance(value, tuple):
                return message["failure"].format(*value)
            else:
                return message["failure"].format(value)

    def perform_jsonschema_check(self, metadata_content):
        return self.schema_validator.run(metadata_content)

    def perform_custom_checks(self, metadata_content):
        ordered_rule = self.get_rule_ordering()
        result_dict = {}

        for rule_id in ordered_rule:
            result_dict.setdefault(rule_id, {})
            fields_to_apply = self.get_fields(rule_id)
            rule = self.checks[rule_id]
            func = Checker.map_to_function(
                rule["data_type"],
                rule["check_function"]
            )
            dependencies = rule.get("dependencies") or []
            for field in fields_to_apply:
                main_field = field["fields"][0]
                dependency_check = True
                for dependency in dependencies:
                    if not self.tracker.read(dependency, main_field)["valid"]:
                        dependency_check = False
                if dependency_check:
                    result = self.custom_checker.run_v2(
                        metadata_content, field, func
                    )
                    self.tracker.update(rule_id, main_field, result["valid"])
                if result["valid"] != None:
                    result_dict[rule_id][main_field] = result

                    message = self.build_message(result, rule_id)
                    if message:
                        result["message"] = message
        return result_dict

    def run(self, metadata_content):
        result = {}
        result["jsonschema"] = self.perform_jsonschema_check(metadata_content)
        result["custom"] = self.perform_custom_checks(metadata_content)
        return result
