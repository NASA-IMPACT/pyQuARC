import json
import os
import re

from io import BytesIO
from jsonschema import Draft7Validator, RefResolver 
from lxml import etree
from urllib.request import pathname2url

from .constants import ECHO10_C, SCHEMA_PATHS, UMM_C


class SchemaValidator:
    """
    Validates downloaded metadata for its schema and returns the result.
    """

    PATH_SEPARATOR = "/"

    def __init__(
        self,
        check_messages,
        metadata_format=ECHO10_C,
    ):
        """
        Args:
            metadata_format (str): The format of the metadata that needs
                to be validated. Can be any of { DIF, ECHO10_C, UMM_C, UMM_G }.
            validation_paths (list of str): The path of the fields in the
                metadata that need to be validated. In the form
                ['Collection/StartDate', ...].
        """
        self.metadata_format = metadata_format
        if metadata_format.startswith("umm-"):
            self.validator_func = self.run_json_validator
        else:
            self.validator_func = self.run_xml_validator
        self.check_messages = check_messages

    def read_xml_schema(self):
        """
        Reads the xml schema file
        """
        # The XML schema file (echo10_xml.xsd) imports another schema file (MetadataCommon.xsd)
        # Python cannot figure out the import if they are in a different location than the calling script
        # Thus we need to set an environment variable to let it know where the files are located
        # Path to catalog must be a url
        catalog_path = f"file:{pathname2url(str(SCHEMA_PATHS['catalog']))}"
        # Temporarily set the environment variable
        os.environ["XML_CATALOG_FILES"] = os.environ.get(
            "XML_CATALOG_FILES", catalog_path
        )

        with open(SCHEMA_PATHS[f"{self.metadata_format}_schema"]) as schema_file:
            file_content = schema_file.read().encode()
        xmlschema_doc = etree.parse(BytesIO(file_content))
        schema = etree.XMLSchema(xmlschema_doc)
        return schema

    def read_json_schema(self):
        """
        Reads the json schema file
        """
        with open(SCHEMA_PATHS[f"{self.metadata_format}-json-schema"]) as schema_file:
            schema = json.load(schema_file)
        return schema

    def run_json_validator(self, content_to_validate):
        """
        Validate passed content based on the schema and return any errors
        Args:
            content_to_validate (str): The metadata content as a json string
        Returns:
            (dict) A dictionary that gives the validity of the schema and errors if they exist
        """
        schema = self.read_json_schema()
        schema_store = {}

        if self.metadata_format == UMM_C:
            with open(SCHEMA_PATHS["umm-cmn-json-schema"]) as schema_file:
                schema_base = json.load(schema_file)

            # workaround to read local referenced schema file (only supports uri)
            schema_store = {
                schema_base.get("$id", "/umm-cmn-json-schema.json"): schema_base,
                schema_base.get("$id", "umm-cmn-json-schema.json"): schema_base,
            }

        errors = {}

        resolver = RefResolver.from_schema(schema, store=schema_store)

        validator = Draft7Validator(
            schema, format_checker=Draft7Validator.FORMAT_CHECKER, resolver=resolver
        )

        for error in sorted(
            validator.iter_errors(json.loads(content_to_validate)), key=str
        ):
            field = SchemaValidator.PATH_SEPARATOR.join(
                [str(x) for x in list(error.path)]
            )
            message = error.message
            remediation = None
            if error.validator == "oneOf" and (
                check_message := self.check_messages.get(error.validator)
            ):
                fields = [
                    f'{field}/{obj["required"][0]}' for obj in error.validator_value
                ]
                message = check_message["failure"].format(fields)
                remediation = check_message["remediation"]
            errors.setdefault(field, {})["schema"] = {
                "message": [f"Error: {message}"],
                "remediation": remediation,
                "valid": False,
            }
        return errors

    @staticmethod
    def _build_errors(error_log, paths):
        """
        Cleans up the error log given by the XML Validator and builds an error object in
        the format accepted by our program

        Args:
            error_log (str): The error log as output by the xml validator
            paths (list): All available paths in the document file

        Returns:
            (dict): The formatted error dictionary
        """
        errors = {}
        lines = error_log.splitlines()
        for line in lines:
            # For DIF, because the namespace is specified in the metadata file, lxml library
            # provides field name concatenated with the namespace,
            # the following 3 lines of code removes the namespace
            namespaces = re.findall(r"(\{http[^}]*\})", line)
            for namespace in namespaces:
                line = line.replace(namespace, "")
            field_name = re.search(r"Element\s'(.*)':", line)[1]
            field_paths = [abs_path for abs_path in paths if field_name in abs_path]
            field_name = field_paths[0] if len(field_paths) == 1 else field_name
            message = re.search(r"Element\s'.+':\s(\[.*\])?(.*)", line)[2].strip()
            errors.setdefault(field_name, {})["schema"] = {
                "message": [f"Error: {message}"],
                "valid": False,
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
        schema = self.read_xml_schema()

        xml_content = content_to_validate
        doc = etree.parse(BytesIO(xml_content))

        # Getting a list of available paths in the document
        # The validator only gives the field name, not full path
        # Getting this to map it to the full path later
        paths = []
        for node in doc.xpath("//*"):
            if not node.getchildren() and node.text:
                paths.append(doc.getpath(node)[1:])

        errors = {}

        try:
            schema.assertValid(doc)
        except etree.DocumentInvalid as err:
            errors = SchemaValidator._build_errors(str(err.error_log), paths)
        return errors

    def run(self, metadata):
        """
        Runs schema validation on the metadata

        Args:
            metadata (str): The original metadata (either xml or json string)

        Returns:
            (dict): Result of the validation from xml and json schema validators
        """
        return self.validator_func(metadata)
