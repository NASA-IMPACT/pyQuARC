import json
import jsonschema
import re

from copy import deepcopy

from constants import DIF, ECHO10, UMM_JSON
from constants import SCHEMA_PATHS

from checks import dispatcher


def _get_path_value(input_json, path):
    """
    Gets the value of the field from the metadata (input_json)

    Args:
        input_json (str): The metadata content
        path (str): The path of the field. Example: 'Collection/RangeDateTime/StartDate'

    Returns:
        (str) The value of the field from the metadata (input_json)
    """

    splits = path.split("/")
    input_json = json.loads(input_json)

    try:
        for split in splits:
            input_json = input_json[split.strip()]
    except KeyError as e:
        return False
    except TypeError as e:
        # TODO: need another way to parse lists
        print(e, split.strip())
        print(f"_get_path_value failed for {path}")

    return input_json


def _get_rule(name_id, ruleset):
    """
    Extracts the rule from the ruleset based on its name_id

    Args:
        name_id (str): The name-id of the rule
        ruleset (list of dict): The ruleset that contains all the rules and their details

    Returns:
        (dict) The target rule and its details

    Raises:
        KeyError: When the name_id doesn't exist in the ruleset
    """
    for rule in ruleset:
        if rule["name-id"].strip() == name_id.strip():
            return rule
    raise KeyError(name_id)


class Validator:
    """
    Validates downloaded metadata for certain fields and returns the result.
    """

    PATH_SEPARATOR = "/"

    def __init__(
        self, metadata_format=ECHO10, validation_paths=[],
    ):
        """
        Args:
            metadata_format (str): The format of the metadata that needs to be validated. Can be either of { ECHO10, UMM-JSON, DIF }.
            validation_paths (str): The path of the fields in the metadata that need to be validated. In the form 'Collection/StartDate'.

        Returns:
            None

        """
        self.validation_paths = validation_paths
        self.metadata_format = metadata_format
        self.schema = self.read_schema()

        self.errors = []

    def _check_validation_paths_against_schema(self):
        """
        Check list of validation paths against schema

        Returns:
            (list) A list of fields from validation_path that don't exist in the metadata
        """
        # TODO: Add custom checks as well

        errors = []

        for validation_path in self.validation_paths:
            splits = [
                i.strip() for i in validation_path.split(Validator.PATH_SEPARATOR)
            ]

            try:
                check = self.schema["properties"]
                for split in splits[:-1]:
                    check = check[split]["properties"]
                check = check[splits[-1]]
            except KeyError:
                errors.append(validation_path)
        return errors

    def _filtered_schema(self):
        """
        Filters the schema based on validation paths passed

        Returns:
            (list) A subset of the JSONSchema schema file that only contains the fields in validation_paths
        """

        filtered_schema = deepcopy(self.schema)
        filtered_schema["properties"] = {}

        for validation_path in self.validation_paths:
            splits = [
                i.strip() for i in validation_path.split(Validator.PATH_SEPARATOR)
            ]

            base = filtered_schema["properties"]
            schema_path = self.schema["properties"]

            for split in splits[:-1]:
                if not split in base:
                    base[split] = {"properties": {}}
                base = base[split]["properties"]
                schema_path = schema_path[split]["properties"]

            base[splits[-1]] = schema_path[splits[-1]]

        return filtered_schema

    def validate_schema(self, content_to_validate):
        """
        Validate passed content based on fields/schema and return any errors

        Args:
            content_to_validate (str): The metadata content as a json string

        Returns:
            (dict) A dictionary that gives the validity of the schema and errors if they exist

        """
        # TODO: Make consistent return types

        errors = []

        validation_path_errors = self._check_validation_paths_against_schema()

        if validation_path_errors:
            errors.append(
                {
                    "message": "Validation path not found in schema",
                    "instance": str(validation_path_errors),
                    "validator": "validation_path",
                }
            )

            return errors

        content_to_validate = json.loads(content_to_validate)

        if self.validation_paths:
            filtered_schema = self._filtered_schema()
        else:
            filtered_schema = self.schema
        validator = jsonschema.Draft7Validator(
            filtered_schema, format_checker=jsonschema.draft7_format_checker
        )

        # this takes a json string
        for error in sorted(validator.iter_errors(content_to_validate), key=str):
            errors.append(
                {
                    "message": error.message,
                    "path": Validator.PATH_SEPARATOR.join(error.path),
                    "instance": error.instance,
                    "validator": error.validator,
                    "validator_value": error.validator_value,
                }
            )

        if len(errors) == 0:
            return {"valid": True}

        return {"valid": False, "errors": errors}

    def run_checks(self, content_to_validate):
        """
        Performs the custom checks based on the QA Rules

        Args:
            content_to_validate (str): The metadata content as a json string

        Returns:
            (dict) A dictionary that gives the result of the custom checks and errors if they exist
        """

        ruleset = json.load(open(SCHEMA_PATHS["ruleset"], "r"))
        rules_mapping = json.load(open(SCHEMA_PATHS["rules_mapping"], "r"))

        results = {}

        for mapping in rules_mapping:
            # do nothing for paths that have no custom checks
            if not mapping["rules"]:
                continue

            path = mapping["path"]
            results[path] = {}

            for rule_id in mapping["rules"]:
                # find this rule_id in ruleset
                # TODO: Maybe this can be done better by constructing a mapping between name-id and function name
                function_name = None
                for rule in ruleset:
                    if rule["name-id"] == rule_id:
                        function_name = rule.get("function", None)

                if not function_name:
                    continue

                results[path][rule_id] = {}
                rule = _get_rule(rule_id, ruleset)

                value = _get_path_value(content_to_validate, path)
                if not value:
                    del results[path][rule_id]
                    # results[path]["exists"] = False
                    continue

                results[path]["exists"] = True
                try:
                    if rule_id == "Data Update Time Logic Check":
                        value1 = _get_path_value(content_to_validate, "Collection/InsertTime")
                        value2 = _get_path_value(content_to_validate, "Collection/LastUpdate")

                        result = dispatcher[rule["function"]](value1, value2)
                    else:
                        result = dispatcher[rule["function"]](value)
                except KeyError as e:
                    # print(e)
                    continue
                if result["valid"] == False:
                    results[path][rule_id]["check_passes"] = False
                    results[path][rule_id]["severity"] = rule["severity"]

                    results[path][rule_id]["message"] = re.sub(
                        r"\{.*\}", str(result["instance"]), rule["message-fail"]
                    )
                    results[path][rule_id]["help_url"] = rule["help_url"]
                    # checks[path][rule_id]["error"] = result["result"]
                else:
                    results[path][rule_id]["check_passes"] = True

                results[path][rule_id]["instance"] = result["instance"]

            # if there is no output for any of the rules
            if not results[path]:
                del results[path]

        return results

    def validate(self, content_to_validate):
        """
        Performs schema check and custom checks and returns comprehensive report

        Args:
            content_to_validate (str): The metadata content as a json string

        Returns:
            (dict) A comprehensive report of errors from jsonschema check and custom checks

        """
        result = {}
        result["schema_check"] = self.validate_schema(content_to_validate)
        result["checks"] = self.run_checks(content_to_validate)

        return result

    def read_schema(self):
        """
        Reads the schema file based on the format and returns json schema

        Returns:
            (dict) The schema dictionary read from the schema file
        """

        schema = json.load(open(SCHEMA_PATHS[self.metadata_format], "r"))
        return schema


# Error dict

# {
#     "ShortName": {
#         "message": "2019 is not a date-time",
#         "path": "Collections > something > something > ShortName",
#         "instance": "2019",
#         "validator": "maxLength",
#         "validator_value": "80"
#     },
# }

# results = library.function(schema, data)
# function(schema, data)
# for all keys in data:
#     schema ko keys sanga match garna khojne
#     manum match bhayo
#     match bhako bhitra gayera tesko pani keys nikalnu paryo
#     bhitri each key ko lagi euta function huncha
#     jastai type ko lagi euta function
#     min length ko lagi euta function
#     kun key ko lagi kun function ho bhanne mapping pani chaincha
#     yo sabbai run garepachi tyo euta metadata key ko kaam siddiyo ani result ma haldine

# bhitri keys to function wala mapping

# {
#     "ShortName": {
#         "valid": True,
#         "errors": {}
#     }
#     OR
#     "ShortName": {
#         "valid": False,
#         "errors": {
#             "field_exists_in_downloaded_content": True
#             "invalid_criteria": ["min_length"]
#         }
#     }
# }


# what do we do when something is in fields but not in content_to_validate
# show error that field was not found

# what do we do when something is in content_to_validate but not in fields
# ignore
