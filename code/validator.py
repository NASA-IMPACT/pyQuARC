import json
import jsonschema

from .constants import SCHEMA_PATHS

class Validator:
    """
        Validates downloaded metadata for certain fields and returns the result.
    """

    def __init__(
        self,
        metadata_format="echo10",
        validation_fields=["ShortName"], # TODO: path instead in a list
    ):
        self.validation_fields = validation_fields
        self.metadata_format = metadata_format
        self.validator = jsonschema.Draft7Validator(self.read_schema())
        self.errors = []

    def validate(self):
        """
            Validate passed content based on fields and log any errors
        """

        schema = self.read_schema()
        for field in validation_fields:
            # run all checks for this field
            # where do we get a list of checks to run
            # how are the checks stored (utils.py?)
            # how do we add more checks
            self.results[field] = {
                "errors": {"invalid_criteria": []},
                "valid": False,
                "field_exists_in_downloaded_content": False,
            }

            if field in content_to_validate:
                self.results[field]["field_exists_in_downloaded_content"] = True

                for key, val in schema[field].items():
                    # not valid
                    if not MAPPING[key](
                        schema_val=val,
                        content_val=content_to_validate[field]
                    ):
                        self.results[field]["errors"]["invalid_criteria"].append(
                            key)

                if len(self.results[field]["errors"]["invalid_criteria"]) == 0:
                    self.results[field]["valid"] = True

        return self.results

    def validate_new(self, content_to_validate):
        """
            Validate passed content based on fields/schema and return any errors
        """
        errors = []

        for error in sorted(self.validator.iter_errors(content_to_validate), key=str):
            errors.append({
                'message': error.message,
                'path' : ' > '.join(error.path),
                'instance': error.instance,
                'validator': error.validator,
                'validator_value': error.validator_value
            })

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
