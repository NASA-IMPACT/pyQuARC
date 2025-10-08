import json
import os
import re

from io import BytesIO
from jsonschema import Draft7Validator, RefResolver
from lxml import etree
from urllib.request import pathname2url
from .utils import read_json_schema_from_url
from .constants import ECHO10_C, SCHEMA_PATHS, UMM_C, UMM_G


SUPPORTED_UMM_C_VERSIONS = ["v1.18.4", "v1.18.3", "v1.18.2"]
DEFAULT_UMM_C_VERSION = "v1.18.4" # Or any other version you prefer as default

# Define UMM-G versions if you want to make it flexible as well
SUPPORTED_UMM_G_VERSIONS = ["v1.6.6"]
DEFAULT_UMM_G_VERSION = "v1.6.6"

SCHEMA_CDN_BASE = "https://cdn.earthdata.nasa.gov/umm"

REMOTE_XML_SCHEMAS = {
    "echo10_collection": "https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/browse/schemas/10.0/Collection.xsd",
    "echo10_granule": "https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/browse/schemas/10.0/Granule.xsd"
}

class SchemaValidator:
    """
    Validates downloaded metadata for its schema and returns the result.
    """

    PATH_SEPARATOR = "/"

    def __init__(
        self,
        check_messages,
        metadata_format=ECHO10_C,
           # Add a new parameter for UMM-C version
        umm_c_version=DEFAULT_UMM_C_VERSION,
        # Add a new parameter for UMM-G version (if you want to make it flexible too)
        umm_g_version=DEFAULT_UMM_G_VERSION
    ):
        """
        Args:
            metadata_format (str): The format of the metadata that needs
                to be validated. Can be any of { DIF, ECHO10_C, UMM_C, UMM_G }.
            validation_paths (list of str): The path of the fields in the
                metadata that need to be validated. In the form
                ['Collection/StartDate', ...].
            umm_c_version (str): The specific UMM-C version to use for validation (e.g., "v1.18.4").
            umm_g_version (str): The specific UMM-G version to use for validation (e.g., "v1.6.6").
            check_messages (dict): A dictionary of check messages for errors.
        """
        self.metadata_format = metadata_format
        # Validate and store the UMM-C version
        if umm_c_version not in SUPPORTED_UMM_C_VERSIONS:
            raise ValueError(
                f"Unsupported UMM-C version: {umm_c_version}. "
                f"Supported versions are: {', '.join(SUPPORTED_UMM_C_VERSIONS)}"
            )
        self.umm_c_version = umm_c_version

        # Validate and store the UMM-G version
        if umm_g_version not in SUPPORTED_UMM_G_VERSIONS:
            raise ValueError(
                f"Unsupported UMM-G version: {umm_g_version}. "
                f"Supported versions are: {', '.join(SUPPORTED_UMM_G_VERSIONS)}"
            )
        self.umm_g_version = umm_g_version

        if metadata_format.startswith("umm-"):
            self.validator_func = self.run_json_validator
        else:
            self.validator_func = self.run_xml_validator
        self.check_messages = check_messages



    def read_xml_schema(self):
        """
        Reads the XML schema file (either from a remote URL or local path).
        """
        from urllib.request import urlopen

        # Maintain XML catalog handling
        catalog_path = f"file:{pathname2url(str(SCHEMA_PATHS['catalog']))}"
        os.environ["XML_CATALOG_FILES"] = os.environ.get(
            "XML_CATALOG_FILES", catalog_path
        )

        def get_raw_schema_url(browse_url: str) -> str:
            """Convert /browse/ URL into /raw/ for direct XML download."""
            if "/browse/" in browse_url:
                return browse_url.replace("/browse/", "/raw/") + "?at=refs%2Fheads%2Fmaster"
            return browse_url

            # Select remote schema if metadata_format matches
        schema_url = REMOTE_XML_SCHEMAS.get(self.metadata_format)
        try:
            if schema_url:
                raw_url = get_raw_schema_url(schema_url)
                print(f"Fetching schema remotely from: {raw_url}")
                import ssl
                ssl_context = ssl._create_unverified_context()  # Disable certificate check safely for this fetch
                with urlopen(raw_url, context=ssl_context) as response:
                    file_content = response.read()
            else:
                # Fallback to local schema file
                with open(SCHEMA_PATHS[f"{self.metadata_format}_schema"]) as schema_file:
                    file_content = schema_file.read().encode()

            xmlschema_doc = etree.parse(BytesIO(file_content))
            schema = etree.XMLSchema(xmlschema_doc)
            return schema

        except Exception as e:
            print(f"⚠️ Remote fetch failed or unavailable for {self.metadata_format}: {e}")
            print("Falling back to local schema file...")
            with open(SCHEMA_PATHS[f"{self.metadata_format}_schema"]) as schema_file:
                file_content = schema_file.read().encode()
            xmlschema_doc = etree.parse(BytesIO(file_content))
            schema = etree.XMLSchema(xmlschema_doc)
            return schema
    
    def read_json_schema(self):
        """
        Reads the json schema file
        """
        if self.metadata_format == UMM_C:
            schema_url = (f"{SCHEMA_CDN_BASE}/collection/{self.umm_c_version}/umm-c-json-schema.json")
            return read_json_schema_from_url(schema_url)

        if self.metadata_format == UMM_G:
            schema_url = (f"{SCHEMA_CDN_BASE}/granule/{self.umm_g_version}/umm-g-json-schema.json")
            return read_json_schema_from_url(schema_url)
        
        with open(SCHEMA_PATHS[f"{self.metadata_format}-json-schema"]) as schema_file:
            return json.load(schema_file)

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


            #umm_cmn_schema_url = f"{SCHEMA_CDN_BASE}/collection/{self.umm_c_version}/umm-c-json-schema.json"
            # If it's *not* versioned and always the latest or a specific fixed version, adjust this URL
            # e.g., f"{SCHEMA_CDN_BASE}/common/umm-cmn-json-schema.json" or from SCHEMA_PATHS

            try:
                with open(SCHEMA_PATHS["umm-cmn-json-schema"]) as common_schema_file:
                    schema_base = json.load(common_schema_file)
                 # 1. Add the schema using its $id (most common canonical reference)
                if "$id" in schema_base:
                    schema_store[schema_base["$id"]] = schema_base
                
                # 2. Add the schema using the full URL you fetched it from (if different from $id or for robustness)
                schema_store["/umm-cmn-json-schema.json"] = schema_base
                schema_store["umm-cmn-json-schema.json"] = schema_base
            except Exception as e:
                print(f"Error loading UMM Common schema from {SCHEMA_PATHS['umm-cmn-json-schema']}: {e}")
                print("Schema validation for UMM-C might proceed without common schema, leading to incomplete validation.")

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
