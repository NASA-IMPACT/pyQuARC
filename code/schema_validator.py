import json
import jsonschema
import os
import re

from io import BytesIO
from lxml import etree
from urllib.request import pathname2url

from .constants import DIF, ECHO10, UMM_JSON, SCHEMA_PATHS


class SchemaValidator:
    """
    Validates downloaded metadata for its schema and returns the result.
    """

    PATH_SEPARATOR = "/"

    def __init__(
        self, metadata_format=ECHO10
    ):
        """
        Args:
            metadata_format (str): The format of the metadata that needs to be validated. Can be either of { ECHO10, UMM-JSON, DIF }.
            validation_paths (list of str): The path of the fields in the metadata that need to be validated. 
                                            In the form ['Collection/StartDate', ...].
        """
        # The XML schema file (echo10_xml.xsd) imports another schema file (MetadataCommon.xsd)
        # Python cannot figure out the import if they are in a different location than the calling script
        # Thus we need to set an environment variable to let it know when the files are located
        if "XML_CATALOG_FILES" not in os.environ:
            # Path to catalog must be a url.
            catalog_path = f"file:{pathname2url(str(SCHEMA_PATHS['catalog']))}"
            # Temporarily set the environment variable.
            os.environ['XML_CATALOG_FILES'] = catalog_path

        self.metadata_format = metadata_format
        self.xml_schema = self.read_xml_schema()
        self.json_schema = self.read_json_schema()

    def read_json_schema(self):
        """
        Reads the json schema file
        """
        schema = json.load(open(SCHEMA_PATHS["echo10_json"], "r"))
        return schema

    def read_xml_schema(self):
        """
        Reads the xml schema file
        """
        with open(SCHEMA_PATHS["echo10_xml"], 'r') as schema_file:
            file_content = schema_file.read().encode()
        xmlschema_doc = etree.parse(BytesIO(file_content))
        schema = etree.XMLSchema(xmlschema_doc)
        return schema

    def run_json_validator(self, content_to_validate):
        """
        Validate passed content based on the schema and return any errors

        Args:
            content_to_validate (str): The metadata content as a json string

        Returns:
            (dict) A dictionary that gives the validity of the schema and errors if they exist

        """
        errors = {}
        error_dict = {
            "valid": False,
            "errors": errors
        }

        validator = jsonschema.Draft7Validator(
            self.json_schema, format_checker=jsonschema.draft7_format_checker
        )

        for error in sorted(validator.iter_errors(content_to_validate), key=str):
            field = SchemaValidator.PATH_SEPARATOR.join(error.path)
            message = error.message
            if error.validator == "oneOf":
                message = "One of `{}` or `{}` is required".format(*[f'{field}/{obj["required"][0]}' for obj in error.validator_value])
            errors.setdefault(field, {})["json_schema"] = {
                    "message": [f"Error: {message}"],
                    "valid": False
                }
        return error_dict

    @staticmethod
    def _build_errors(error_log):
        """
        Cleans up the error log given by the XML Validator and builds an error object in
        the format accepted by our program

        Args:
            error_log (str): The error log as output by the xml validator

        Returns:
            (dict): The formatted error dictionary
        """
        errors = {}
        lines = error_log.splitlines()
        for line in lines:
            field = re.search("Element\s\'(\w+)\'", line)[1]
            message = re.search("Element\s\'\w+\':\s(\[.*\])?(.*)", line)[2].strip()
            errors.setdefault(field, {})["xml_schema"] = {
                "message": [f"Error: {message}"],
                "valid": False
            }
        return errors

    def run_xml_validator(self, content_to_validate):
        """
        Validate passed content based on the schema and return any errors

        Args:
            content_to_validate (bytes): The metadata content as a xml string

        Returns:
            (dict) A dictionary that gives the validity of the schema and errors if they exist

        """
        xml_content = content_to_validate
        doc = etree.parse(BytesIO(xml_content))
        errors = {}

        try:
            self.xml_schema.assertValid(doc)
        except etree.DocumentInvalid as err:
            errors = SchemaValidator._build_errors(str(err.error_log))

        result = {
            "errors": errors
        }
        return result

    def run(self, xml_metadata, json_metadata):
        """
        Runs both XML and JSON schema validation on the metadata

        Args:
            xml_metadata (str): The original metadata (in xml format)
            json_metadata (str): The metadata converted to json

        Returns:
            (dict): Result of the validation from xml and json schema validators
        """
        return {
            ** self.run_json_validator(json_metadata)["errors"],
            ** self.run_xml_validator(xml_metadata)["errors"]
        }
