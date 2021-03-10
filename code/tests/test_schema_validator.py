import os

from xmltodict import parse

from ..schema_validator import SchemaValidator

KEYS = [
    "no_error_metadata", "bad_syntax_metadata", "test_cmr_metadata"
]

class TestSchemaValidator:
    def setup_method(self):
        self.data = self.read_data()
        self.schema_validator = SchemaValidator({
            "oneOf": {
                "failure": "One of `{}` should be populated.",
                "help": {
                    "message": "",
                    "url": ""
                },
                "remediation": "Make sure one of the fields is populated."
            }
        })

    def read_data(self):
        result = {}
        for data_key in KEYS:
            # os.path.join(os.getcwd(), DUMMY_METADATA_FILE_PATH)
            with open(
                os.path.join(
                os.getcwd(),
                f"code/tests/fixtures/{data_key}.echo10"
            ), "r"
            ) as myfile:
                result[data_key] = myfile.read().encode()
            result[f"{data_key}_json"] = parse(result[data_key])
        return result

    def test_json_validator(self):
        for data_key in KEYS:
            assert self.schema_validator.run_json_validator(
                self.data[f"{data_key}_json"]
            )

    def test_xml_validator(self):
        for data_key in KEYS:
            assert self.schema_validator.run_json_validator(
                self.data[data_key]
            )
