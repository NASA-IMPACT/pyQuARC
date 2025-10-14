import json

from xmltodict import parse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .custom_checker import CustomChecker
from .schema_validator import SchemaValidator

from .scheduler import Scheduler
from .tracker import Tracker

from .custom_validator import CustomValidator
from .datetime_validator import DatetimeValidator
from .string_validator import StringValidator
from .url_validator import UrlValidator

from .schema_validator import SchemaValidator
from .constants import UMM_C  # or however you define metadata format

from .constants import ECHO10_C, SCHEMA_PATHS


class Checker:
    """
    Handles both the structural and logical checks
    """

    def __init__(
        self,
        metadata_format=ECHO10_C,
        messages_override=None,
        checks_override=None,
        rules_override=None,
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
        self.metadata_format = metadata_format

        self.msgs_override_file = messages_override or "check_messages_override"
        self.rules_override_file = rules_override or "rules_override"
        self.checks_override_file = checks_override or "checks_override"

        self.load_schemas()

        self.custom_checker = CustomChecker()
        self.scheduler = Scheduler(
            self.rule_mapping,
            self.rules_override,
            self.checks,
            self.checks_override,
            metadata_format=metadata_format,
        )
        self.schema_validator = SchemaValidator(
            self.messages_override or self.messages, metadata_format
        )
        self.tracker = Tracker(
            self.rule_mapping, self.rules_override, metadata_format=metadata_format
        )

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
        self.messages_override = Checker._json_load_schema(self.msgs_override_file)
        self.rules_override = Checker._json_load_schema(self.rules_override_file)
        self.checks_override = Checker._json_load_schema(self.checks_override_file)

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
        return messages[msg_type] if messages else ""

    def build_message(self, result, rule_id):
        """
        Formats the message for `rule_id` based on the result
        """
        failure_message = self.message(rule_id, "failure")
        rule_mapping = self.rules_override.get(rule_id) or self.rule_mapping.get(
            rule_id
        )
        severity = rule_mapping.get("severity", "error")
        messages = []
        if not (result["valid"]) and result.get("value"):
            for value in result["value"]:
                formatted_message = failure_message
                value = value if isinstance(value, tuple) else (value,)
                formatted_message = failure_message.format(*value)
                formatted_message = f"{severity.title()}: {formatted_message}"
                messages.append(formatted_message)
        return messages

    def perform_schema_check(self, xml_metadata):
        """
        Performs Schema check
        """
        return self.schema_validator.run(xml_metadata)

    def _check_dependency_validity(self, dependency, field_dict):
        """
        Checks if the dependent check called `dependency` is valid
        """
        dependency_fields = (
            field_dict["fields"] if len(dependency) == 1 else [dependency[1]]
        )
        for field in dependency_fields:
            if not self.tracker.read_data(dependency[0], field).get("valid"):
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

    def _process_field(
        self,
        func,
        check,
        rule_id,
        metadata_content,
        field_dict,
        result_dict,
        rule_mapping,
    ):
        """
        Process a single field according to the given rule and update result_dict
        """
        external_data = rule_mapping.get("data", [])
        relation = rule_mapping.get("relation")
        dependencies = self.scheduler.get_all_dependencies(
            rule_mapping, check, field_dict
        )
        main_field = field_dict["fields"][0]
        external_data = field_dict.get("data", external_data)
        result_dict.setdefault(main_field, {})

        if not self._check_dependencies_validity(dependencies, field_dict):
            return

        result = self.custom_checker.run(
            func, metadata_content, field_dict, external_data, relation
        )

        self.tracker.update_data(rule_id, main_field, result["valid"])

        # Avoid adding null valid results for rules that are not applied
        if result["valid"] is None:
            return

        result_dict[main_field][rule_id] = result

        message = self.build_message(result, rule_id)
        if message:
            result["message"] = message
            result["remediation"] = self.message(rule_id, "remediation")

    def _run_func(self, func, check, rule_id, metadata_content, result_dict):
        """
        Run the check function for `rule_id` and update `result_dict`
        """
        rule_mapping = self.rules_override.get(rule_id) or self.rule_mapping.get(
            rule_id
        )
        list_of_fields_to_apply = rule_mapping.get("fields_to_apply").get(
            self.metadata_format, {}
        )
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for field_dict in list_of_fields_to_apply:
                future = executor.submit(
                    self._process_field,
                    func,
                    check,
                    rule_id,
                    metadata_content,
                    field_dict,
                    result_dict,
                    rule_mapping,
                )
                futures.append(future)

            # Wait for all futures to complete
            for future in as_completed(futures):
                # Retrieve the result or raise an exception if an error occurred
                try:
                    future.result()
                except Exception as e:
                    # Handle the exception from the thread
                    raise e

    def perform_custom_checks(self, metadata_content):
        """
        Performs custom checks
        """
        ordered_rule = self.scheduler.order_rules()
        result_dict = {}
        pyquarc_errors = []
        for rule_id in ordered_rule:
            try:
                rule_mapping = self.rules_override.get(
                    rule_id
                ) or self.rule_mapping.get(rule_id)
                check_id = rule_mapping.get("check_id", rule_id)
                check = self.checks_override.get(check_id) or self.checks.get(check_id)
                func = Checker.map_to_function(
                    check["data_type"], check["check_function"]
                )
                if func:
                    self._run_func(func, check, rule_id, metadata_content, result_dict)
            except Exception as e:
                pyquarc_errors.append(
                    {
                        "message": f"Running check for the rule: '{rule_id}' failed.",
                        "details": str(e),
                    }
                )
        return result_dict, pyquarc_errors

    def run(self, metadata_content):
        """
        Runs all checks on the `metadata_content`

        Args:
            metadata_content (str): The downloaded metadata content

        Returns:
            (dict): The results of the jsonschema check and all custom checks
        """

        def _xml_postprocessor(_, key, value):
            """
            Sometimes the XML values contain attributes.
            In such a case, the returned value for a field looks something like:

            >> doc["DIF"]["ISO_Topic_Category"]
                OrderedDict([('@uuid', '26ebb539-cae2-4961-9252-7f367642fa57'), ('#text', 'IMAGERY/BASE MAPS/EARTH COVER')]) #noqa

            instead of the regular:
            >> doc["DIF"]["ISO_Topic_Category"]
                IMAGERY/BASE MAPS/EARTH COVER

            this postprocessor is used to get the regular value even in cases
            where attrs are present
            """
            try:
                return key, value["#text"]
            except (KeyError, TypeError):
                return key, value

        kwargs = {}
        parser = json.loads
        if not self.metadata_format.startswith("umm-"):
            parser = parse
            kwargs = {"postprocessor": _xml_postprocessor}
        json_metadata = parser(metadata_content, **kwargs)
        result_schema = self.perform_schema_check(metadata_content)
        result_custom, pyquarc_errors = self.perform_custom_checks(json_metadata)
        result = {**result_schema, **result_custom}
        return result, pyquarc_errors
