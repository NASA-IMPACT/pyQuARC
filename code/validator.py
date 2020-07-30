import json
import jsonschema

from constants import DIF, ECHO10, UMM_JSON
from constants import SCHEMA_PATHS


class Validator:
    """
        Validates downloaded metadata for certain fields and returns the result.
    """

    def __init__(
        self,
        metadata_format=ECHO10,
        validation_fields=["ShortName"],  # TODO: path instead in a list
    ):
        self.validation_fields = validation_fields
        self.metadata_format = metadata_format
        self.validator = jsonschema.Draft7Validator(self.read_schema())
        self.errors = []

    def validate(self, content_to_validate):
        """
            Validate passed content based on fields/schema and return any errors
        """
        errors = []

        content_to_validate = json.loads(content_to_validate)

        # this takes a json string
        for error in sorted(self.validator.iter_errors(content_to_validate), key=str):
            errors.append(
                {
                    "message": error.message,
                    "path": " > ".join(error.path),
                    "instance": error.instance,
                    "validator": error.validator,
                    "validator_value": error.validator_value,
                }
            )

        return errors

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
