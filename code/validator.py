import json
import jsonschema
import re

from copy import deepcopy

from .checker import Checker
from .constants import DIF, ECHO10, UMM_JSON
from .constants import SCHEMA_PATHS


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

    def _construct_paths_recursively(self, content_to_validate, container, prefix=''):
        """
        Use recursion to construct all the paths exhaustively
        """
        for key, value in content_to_validate.items():
            pre = key if prefix == '' else f"{prefix}/{key}"

            if isinstance(value, dict):
                self._construct_paths_recursively(value, container, pre)
            elif isinstance(value, list):
                self._construct_paths_recursively(value[0], container, pre)
            else:
                container.add(pre)

    def generate_paths(self, content_to_validate):
        """
        Generate exhaustive list of paths from content_to_validate

        Args:
            content_to_validate (dict): The metadata file content

        Returns:
            (set) The set of all the paths
        """
        paths = set()
        self._construct_paths_recursively(content_to_validate, paths)
        return paths

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

        checker = Checker(content_to_validate)

        return checker.run()

    def validate(self, content_to_validate):
        """
        Performs schema check and custom checks and returns comprehensive report

        Args:
            content_to_validate (str): The metadata content as a json string

        Returns:
            (dict) A comprehensive report of errors from jsonschema check and custom checks

        """

        result = {}
        result["checks"] = self.run_checks(content_to_validate)
        result["schema_check"] = self.validate_schema(content_to_validate)

        return result

    def read_schema(self):
        """
        Reads the schema file based on the format and returns json schema

        Returns:
            (dict) The schema dictionary read from the schema file
        """

        schema = json.load(open(SCHEMA_PATHS[self.metadata_format], "r"))
        return schema
