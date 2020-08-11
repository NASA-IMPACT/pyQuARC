import json
import jsonschema

from copy import deepcopy

from constants import DIF, ECHO10, UMM_JSON
from constants import SCHEMA_PATHS

from checks import dispatcher


def _get_path_value(input_json, path):
    splits = path.split("/")
    input_json = json.loads(input_json)

    try:
        for split in splits:
            input_json = input_json[split.strip()]
    except KeyError as e:
        return False
    except TypeError as e:
        print(path)

    return input_json


def _get_rule(name_id, ruleset):
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
        self.validation_paths = validation_paths
        self.metadata_format = metadata_format
        self.schema = self.read_schema()

        self.errors = []

    def _check_validation_paths_against_schema(self):
        """
            Check list of validation paths against schema
        """

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
        """

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
            return {
                "valid": True
            }

        return {
            "valid": False,
            "errors": errors
        }

    def run_checks(self, content_to_validate):
        """
            Performs the custom checks based on the QA Rules
        """
        ruleset = json.load(open(SCHEMA_PATHS["ruleset"], 'r'))
        rules_mapping = json.load(open(SCHEMA_PATHS["rules_mapping"], 'r'))

        checks = {}

        for mapping in rules_mapping:
            path = mapping["path"]
            checks[path] = {}
            for rule_id in mapping["rules"]:
                checks[path][rule_id] = {}
                rule = _get_rule(rule_id, ruleset)

                if rule_id == 'data_updatetime_logic_check':
                    continue
                else:
                    value = _get_path_value(content_to_validate, path)
                    if not value:
                        checks[path]["exists"] = False
                        continue

                    checks[path]["exists"] = True
                    try:
                        result = dispatcher[rule["function"]](value)
                    except KeyError as e:
                        # print(e)
                        continue
                    if result["valid"] == False:
                        checks[path][rule_id]["check_passes"] = False
                        checks[path][rule_id]["severity"] = rule["severity"]
                        checks[path][rule_id]["message"] = rule["message-fail"]
                        checks[path][rule_id]["help_url"] = rule["help_url"]
                        # checks[path][rule_id]["error"] = result["result"]
        
        return checks


    def validate(self, content_to_validate):
        """
            Performs schema check and custom checks and returns comprehensive report
        """
        result = {}
        result["schema_check"] = self.validate_schema(content_to_validate)
        result["checks"] = self.run_checks(content_to_validate)

        return result


    def read_schema(self):
        """
            Reads the schema file based on the format and returns json schema
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
