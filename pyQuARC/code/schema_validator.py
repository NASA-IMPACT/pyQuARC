import json
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
        self, metadata_format=ECHO10,
    ):
        """
        Args:
            metadata_format (str): The format of the metadata that needs
                to be validated. Can be either of { ECHO10, UMM-JSON, DIF }.
            validation_paths (list of str): The path of the fields in the
                metadata that need to be validated. In the form
                ['Collection/StartDate', ...].
        """
        # The XML schema file (echo10_xml.xsd) imports another schema file (MetadataCommon.xsd)
        # Python cannot figure out the import if they are in a different location than the calling script
        # Thus we need to set an environment variable to let it know where the files are located
        # Path to catalog must be a url
        catalog_path = f"file:{pathname2url(str(SCHEMA_PATHS['catalog']))}"
        # Temporarily set the environment variable
        os.environ['XML_CATALOG_FILES'] = os.environ.get('XML_CATALOG_FILES', catalog_path)

        self.metadata_format = metadata_format
        self.xml_schema = self.read_xml_schema()

    def read_xml_schema(self):
        """
        Reads the xml schema file
        """
        with open(SCHEMA_PATHS[f"{self.metadata_format}_xml"], "r") as schema_file:
            file_content = schema_file.read().encode()
        xmlschema_doc = etree.parse(BytesIO(file_content))
        schema = etree.XMLSchema(xmlschema_doc)
        return schema

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
            namespaces = re.findall("(\{http[^}]*\})", line)
            for namespace in namespaces:
                line = line.replace(namespace, '')
            field_name = re.search("Element\s\'(.*)\':", line)[1]
            field_paths = [
                abs_path for abs_path in paths if field_name in abs_path
            ]
            field_name = field_paths[0] if len(field_paths) == 1 else field_name
            message = re.search("Element\s\'.+\':\s(\[.*\])?(.*)", line)[2].strip()
            errors.setdefault(field_name, {})["xml_schema"] = {
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

        # Getting a list of available paths in the document
        # The validator only gives the field name, not full path
        # Getting this to map it to the full path later
        paths = []
        for node in doc.xpath('//*'):
            if not node.getchildren() and node.text:
                paths.append(doc.getpath(node)[1:])

        errors = {}

        try:
            self.xml_schema.assertValid(doc)
        except etree.DocumentInvalid as err:
            errors = SchemaValidator._build_errors(str(err.error_log), paths)

        return errors

    def run(self, xml_metadata):
        """
        Runs schema validation on the metadata

        Args:
            xml_metadata (str): The original metadata (in xml format)

        Returns:
            (dict): Result of the validation from xml and json schema validators
        """
        return self.run_xml_validator(xml_metadata)
