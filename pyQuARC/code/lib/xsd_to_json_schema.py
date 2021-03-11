import json
import os

from pathlib import Path

from constants import type_based_keys
from utils import (
    EXTRACTION_KEYS,
    global_conversion_schema,
    key_extractor_fuctions
)

path = Path(__file__).resolve().parents[2]

# the following functions are used for setting optional=True and type=array


def type_based_keys_value(field_type, obj):
    """
        Handles restrictions etc
    """

    if "xs:simpleType" in obj:
        return type_based_keys_value(field_type, obj["xs:simpleType"])
    if "xs:restriction" in obj:
        return type_based_keys_value(field_type, obj["xs:restriction"])

    temp_dict = {}
    if field_type not in type_based_keys:
        # if there is no field key in the type_based_keys, return empty
        return temp_dict
    for type_key in type_based_keys[field_type]:
        schema = global_conversion_schema[type_key]
        in_value = obj[schema['in_key']]
        if isinstance(in_value, dict):
            in_value = in_value["@value"]
        try:
            # exceptions, if there are many if condtion here
            # think for a proper way to do this
            if (type_key == "maxItems" and in_value == "unbounded"):
                pass
            elif (type_key == "enum" and in_value == "Not Applicable"):
                pass
            else:
                val = schema['converter_function'](in_value)
                temp_dict[type_key] = val
        except KeyError:
            # if there is a key error, it means there is no in_key in the obj
            # it is normal to not have it so we let it pass
            pass

    return temp_dict


def process_object_type(obj, enum=False):
    """
        Handles "sequence", "choice", and the underlying "element"s
    """

    temp = {}
    if "xs:sequence" in obj:
        sequence = obj["xs:sequence"]
        if isinstance(sequence, dict):
            return process_object_type(sequence)
        elif isinstance(sequence, list):
            return {
                "oneOf": [
                    process_object_type(s) for s in sequence
                ]
            }
    elif "xs:choice" in obj:
        temp = process_object_type(obj["xs:choice"], True)

    obj_list = []
    if "xs:element" in obj:
        if isinstance(obj["xs:element"], list):
            obj_list = [
                get_single_obj_json(item) for item in obj["xs:element"]
            ]
        else:
            obj_list = [get_single_obj_json(obj["xs:element"])]
    if enum:
        return {"enum": obj_list}

    temp.update({
        "properties": {item["name"]: item for item in obj_list}
    })

    return temp


def get_single_obj_json(obj):
    """
        Takes a raw json object and return a json schema object
    """

    obj_json = {}
    for extraction_key in EXTRACTION_KEYS:
        val = key_extractor_fuctions[extraction_key](obj)
        obj_json.update(val)

    # post processing the "type" key
    if "type" not in obj_json:
        return obj_json
    elif obj_json["type"] == "N/A":
        obj_json.pop("type")
        return obj_json

    field_type = obj_json["type"]
    temp_obj = {}

    if (field_type == "object"):
        # complex object types
        temp_obj = process_object_type(obj)
    else:
        temp_obj = type_based_keys_value(field_type, obj)

    obj_json.update(temp_obj)

    return obj_json


def main():
    # set the paths for the input and output files
    file_name_list = ["metadata", "dif", "collection"]
    output_folder = path / "output"

    file_iterator = [
        {
            "input_file": output_folder / f"{file_name}.json",
            "output_file": output_folder / f"{file_name}_output.json"
        }
        for file_name in file_name_list
    ]

    # iterate through the files
    for file_dict in file_iterator:

        # open the input file and read the json data
        with open(file_dict["input_file"], "r") as input_file:
            myjson = json.loads(input_file.read())

        json_schemas = {}

        # handling type definitions in simpleType and complexType
        simple_types = myjson["xs:schema"]["xs:simpleType"]
        complex_types = myjson["xs:schema"]["xs:complexType"]

        # process the raw json data to create the json schema
        for obj in [*simple_types, *complex_types]:
            obj_json = get_single_obj_json(obj)
            json_schemas.update({obj_json["name"]: obj_json})

        final_schema = {
            "$schema": "http://json-schema.org/schema#",
            # definitions of simple types and complex types go together
            "definitions": json_schemas,
            # here we only have definitions of types. The actual schema would look like:
            # "type": "object",
            # "properties": {}
        }

        # write the output
        with open(file_dict["output_file"], "w") as output_file:
            output_file.write(json.dumps(final_schema))


if __name__ == "__main__":
    main()
