import json
import os

from pathlib import Path

path = Path(__file__).resolve().parents[2]


def process_type(elem_type):
    """
        Returns a dictionary with
        1) type and maybe a format
        2) elem_type as a $ref
    """

    elem_type = elem_type.replace("xs:", "")
    temp_dict = {"type": "string"}

    if (elem_type == "dateTime"):
        temp_dict["format"] = "date-time"
    elif (elem_type == "long" or elem_type == "int" or elem_type == "decimal"):
        temp_dict["type"] = "number"
    elif (elem_type == "anyURI"):
        temp_dict["format"] = "uri"
    elif (elem_type == "date"):
        temp_dict["format"] = "date"
    elif (elem_type == "anyURI"):
        temp_dict["format"] = "uri"
    else:
        temp_dict["type"] = elem_type

    if temp_dict["type"] in ["string", "number", "integer", "date"]:
        return temp_dict
    else:
        return {"$ref": f"#/definitions/{elem_type}"}


global_conversion_schema = {
    'minLength': {
        'in_key': 'xs:minLength',
        'converter_function': lambda x: int(x)
    },
    'maxLength': {
        'in_key': 'xs:maxLength',
        'converter_function': lambda x: int(x)
    },
    'inclusiveMinimum': {
        'in_key': 'xs:minInclusive',
        'converter_function': lambda x: float(x)
    },
    'inclusiveMaximum': {
        'in_key': 'xs:maxInclusive',
        'converter_function': lambda x: float(x)
    },
    'exclusiveMinimum': {
        'in_key': 'xs:minExclusive',
        'converter_function': lambda x: float(x)
    },
    'exclusiveMaximum': {
        'in_key': 'xs:maxExclusive',
        'converter_function': lambda x: float(x)
    },
    'multipleOf': {
        'in_key': 'xs:fractionDigits',
        'converter_function': lambda x: 1 / (10**int(x))
    },
    'maximum': {
        'in_key': 'xs:totalDigits',
        'converter_function': lambda x: 10**(int(x) - 1)
    },
    'pattern': {
        'in_key': 'xs:pattern',
        'converter_function': lambda x: x
    },
    'enum': {
        'in_key': 'xs:enumeration',
        'converter_function': lambda x:
            [i['@value'] for i in x] if isinstance(x, list) else x
    },
    'minItems': {
        'in_key': '@minOccurs',
        'converter_function': lambda x: int(x)
    },
    'maxItems': {
        'in_key': '@maxOccurs',
        'converter_function': lambda x: int(x)
    },
    'items': {
        'in_key': '@type',
        'converter_function': lambda x: process_type(x)
    }
}


int_num_type = [
    "maximum",
    "inclusiveMinimum",
    "inclusiveMaximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
]

type_based_keys = {
    "string": ["enum", "minLength", "maxLength", "pattern"],
    "array": ["items", "minItems", "maxItems"],
    "integer": int_num_type,
    "number": int_num_type,
    # type objects use the same thing
}

# the following functions are used for setting optional=True and type=array


def min_occurs(x):
    return "@minOccurs" in x


def max_occurs(x):
    return "@maxOccurs" in x


def min_0(x):
    return min_occurs(x) and x.get("@minOccurs") == "0"


def optional(x):
    return min_0(x) and not max_occurs(x)


def no_occurs(x):
    return not min_occurs(x) and not max_occurs(x)


def name_extractor(inp_obj):
    try:
        return {"name": inp_obj["@name"]}
    except KeyError:
        # this lets us know when some object doesn't have a name
        import ipdb
        ipdb.set_trace()


def description_extractor(inp_obj):
    """
        Extract the description string from xs:documentation and the xs:appinfo
    """

    intermediate_dict = {}
    if ("xs:annotation" in inp_obj):
        intermediate_dict["description"] = inp_obj["xs:annotation"]["xs:documentation"] or ""
        des = intermediate_dict["description"]
        if (isinstance(des, dict) and "p" in des):
            intermediate_dict["description"] = " ".join(des["p"])
        if ("xs:appinfo" in inp_obj["xs:annotation"]):
            intermediate_dict["appinfo"] = inp_obj["xs:annotation"]["xs:appinfo"]
    return intermediate_dict


def type_extractor(inp_obj):
    """
        Extract the type information from the input object
    """

    # the order of ifs matter, hence the mapping is not put in a dictionary
    field_type = "string"
    if "xs:simpleType" in inp_obj:
        return type_extractor(inp_obj["xs:simpleType"])

    if "xs:simpleContent" in inp_obj:
        temp = inp_obj["xs:simpleContent"]["xs:extension"]
        temp_dict = process_type(temp["@base"])
        temp_dict.update({"type_ref": temp["xs:attribute"]["@type"]})
        return temp_dict

    elif "xs:complexContent" in inp_obj:
        temp = inp_obj["xs:complexContent"]["xs:extension"]
        return process_type(temp["@base"])

    elif "xs:sequence" in inp_obj or "xs:choice" in inp_obj:
        field_type = "object"

    elif "xs:restriction" in inp_obj:
        field_type = process_type(inp_obj["xs:restriction"]["@base"])

    elif not (optional(inp_obj) or no_occurs(inp_obj)):
        field_type = "array"

    elif "@type" in inp_obj:
        field_type = process_type(inp_obj["@type"])

    else:
        field_type = "N/A"

    if isinstance(field_type, dict):
        return field_type
    return {"type": field_type}


def optional_extractor(inp_object):
    """
        Determine if an object is optional
    """

    if min_occurs(inp_object) and optional(inp_object):
        return {"optional": True}
    return {}


extraction_keys = ["name", "description", "type", "optional"]
key_extractor_fuctions = {
    "name": name_extractor,
    "description": description_extractor,
    "type": type_extractor,
    "optional": optional_extractor,
}


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
        try:
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
            except TypeError:
                import ipdb
                ipdb.set_trace()
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
    for extraction_key in extraction_keys:
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
