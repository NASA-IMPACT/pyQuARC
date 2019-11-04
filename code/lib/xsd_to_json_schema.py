import json
import os

from pathlib import Path
from pprint import pprint

path = Path(__file__).resolve().parents[2]

INPUT_FILE = path / 'output' / 'dif.json'
OUTPUT_FILE = path / 'output' / 'dif_json_schema.json'

with open(INPUT_FILE, 'r') as metadata:
    myjson = json.loads(metadata.read())

result_dict = {
    'simpleType': [],
    'complexType': []
}

# this is supposed to help us remove
# some of the if statements in the following code
# but we haven't used it that way yet
conversion_key_set = {
    "@base",
    "xs:enumeration",
    "xs:minLength",
    "xs:maxLength",
    "xs:minInclusive",
    "xs:maxInclusive",
    "xs:fractionDigits",
    "xs:totalDigits",
    "xs:pattern"
}


def parse_simpletype(simple_type_obj):
    """
        Parse a simpletype object
    """

    # sample simple_type_obj
    # {
    #   "@name": "VersionType",
    #   "xs:annotation": {
    #     "xs:documentation": "Version identifier of the data collection."
    #   },
    #   "xs:restriction": {
    #     "@base": "xs:string"
    #   }
    # }

    intermediate_dict = {}

    if '@name' in simple_type_obj:
        intermediate_dict['name'] = simple_type_obj['@name']

    # restrictions object within the simpleType
    restrictions = simple_type_obj['xs:restriction']

    try:
        intermediate_dict['type'] = restrictions['@base'].split(':')[1]
    except IndexError:
        # print(f"go get the definition of {restrictions['@base']}")
        intermediate_dict['type'] = f"#/definitions/{restrictions['@base']}"

    if intermediate_dict['type'] == "decimal":
        intermediate_dict['type'] = "number"

    # if we miss a key, we want to find out about it
    restriction_key_set = set(restrictions.keys())
    if not (restriction_key_set.issubset(conversion_key_set)):
        # fail loudly
        assert False, (restriction_key_set - conversion_key_set)

    if "xs:enumeration" in restrictions:
        try:
            intermediate_dict['enum'] = [i['@value'] for i in restrictions["xs:enumeration"]]
        except TypeError:
            intermediate_dict['enum'] = restrictions["xs:enumeration"]["@value"]

    if "xs:minLength" in restrictions:
        intermediate_dict['minLength'] = int(restrictions["xs:minLength"]["@value"])

    if "xs:maxLength" in restrictions:
        intermediate_dict['maxLength'] = int(restrictions["xs:maxLength"]["@value"])

    if "xs:minInclusive" in restrictions:
        intermediate_dict['inclusiveMinimum'] = float(restrictions["xs:minInclusive"]["@value"])

    if "xs:maxInclusive" in restrictions:
        intermediate_dict['inclusiveMaximum'] = float(restrictions["xs:maxInclusive"]["@value"])

    if "xs:minExclusive" in restrictions:
        intermediate_dict['exclusiveMinimum'] = float(restrictions["xs:minExclusive"]["@value"])

    if "xs:maxExclusive" in restrictions:
        intermediate_dict['exclusiveMaximum'] = float(restrictions["xs:maxExclusive"]["@value"])

    if "xs:fractionDigits" in restrictions:
        intermediate_dict['multipleOf'] = 1 / (10**int(restrictions["xs:fractionDigits"]["@value"]))

    if "xs:totalDigits" in restrictions:
        intermediate_dict['maximum'] = 10**(int(restrictions["xs:totalDigits"]["@value"]) - 1)

    if "xs:pattern" in restrictions:
        intermediate_dict['pattern'] = restrictions["xs:pattern"]["@value"]

    if ("xs:annotation" in simple_type_obj) and ("xs:appinfo" in simple_type_obj["xs:annotation"]):
        intermediate_dict['appinfo'] = simple_type_obj["xs:annotation"]["xs:appinfo"]

    if "xs:annotation" in simple_type_obj:
        intermediate_dict['description'] = simple_type_obj["xs:annotation"]["xs:documentation"]

    return intermediate_dict


def process_simpletypes():
    """
        Process simpletypes first
    """

    for simple_type_obj in myjson["xs:schema"]["xs:simpleType"]:
        intermediate_dict = parse_simpletype(simple_type_obj)

        result_dict['simpleType'].append(intermediate_dict)
    return result_dict['simpleType']


def parse_element(element):
    """
        An element is a part of a sequence.
        This function takes an element and converts it to JSON schema-ish
    """

    element_dict = {}
    element_dict["name"] = element["@name"]

    if "@type" in element:
        # remove the "xs:"
        if len(element["@type"].split(':')) > 1:
            element_dict["type"] = element["@type"].split(':')[1]
        else:
            element_dict["type"] = element["@type"]

    if "xs:simpleType" in element:
        element_dict.update(parse_simpletype(element["xs:simpleType"]))

    if "@minOccurs" in element:
        element_dict["minOccurs"] = element["@minOccurs"]

    if "@maxOccurs" in element:
        element_dict["maxOccurs"] = element["@maxOccurs"]

    if "xs:annotation" in element:
        element_dict['description'] = element["xs:annotation"]["xs:documentation"]

    return element_dict


def process_sequence(sequence):
    """
        Process a sequence and return a list of element dictionaries
    """

    elements = sequence["xs:element"]
    intermediate_list = []

    if isinstance(elements, list):
        for element in elements:
            element_dict = parse_element(element)

            # change this:
            intermediate_list.append(element_dict)

    elif isinstance(elements, dict):
        element_dict = parse_element(elements)
        intermediate_list.append(element_dict)

    else:
        raise TypeError("'sequence' must be either a list or a dict")

    return intermediate_list


def process_complextypes():
    """
        Goes through all the xs:complexType structures and returns a list
    """

    for complex_type_obj in myjson["xs:schema"]["xs:complexType"]:
        intermediate_dict = {}
        intermediate_dict['name'] = complex_type_obj['@name']

        # get the description string
        if "xs:annotation" in complex_type_obj:
            intermediate_dict['description'] = complex_type_obj["xs:annotation"]["xs:documentation"]

        if "xs:attribute" in complex_type_obj:
            intermediate_dict['attribute'] = {
                "name": complex_type_obj["xs:attribute"]["@name"],
                "type": f'#/definitions/{complex_type_obj["xs:attribute"]["@type"]}'
            }

        if ("xs:annotation" in complex_type_obj) and ("xs:appinfo" in complex_type_obj["xs:annotation"]):
            intermediate_dict['appinfo'] = complex_type_obj["xs:annotation"]["xs:appinfo"]

        # regular xs:sequence > xs: elements
        try:
            sequence = complex_type_obj["xs:sequence"]
            intermediate_dict["elements"] = [process_sequence(sequence)]
        except KeyError:
            # these ones most likely have choice
            # xs:choice > [xs:sequence > xs: elements]
            try:
                intermediate_dict["elements"] = []
                sequences = complex_type_obj["xs:choice"]['xs:sequence']
                for sequence in sequences:
                    intermediate_dict["elements"].append(process_sequence(sequence))
            except KeyError:
                # this one is just empty type
                # TODO: print some logs here
                # this could be "xs:simpleContent" or "xs:complexContent"
                if not (("xs:simpleContent" in complex_type_obj) or ("xs:complexContent" in complex_type_obj)):
                    print("No sequence, no choice", intermediate_dict['name'])
                    continue

                if "xs:simpleContent" in complex_type_obj:
                    sequence = {
                        "xs:element": {
                            "@name": complex_type_obj["xs:simpleContent"]["xs:extension"]["xs:attribute"]["@name"],
                            "@type": complex_type_obj["xs:simpleContent"]["xs:extension"]["xs:attribute"]["@type"]
                        }
                    }

                if "xs:complexContent" in complex_type_obj:
                    sequence = {
                        "xs:element": {
                            "@name": complex_type_obj["xs:complexContent"]["xs:extension"]["@base"],
                            "@type": complex_type_obj["xs:complexContent"]["xs:extension"]["@base"]
                        }
                    }

                intermediate_dict["elements"] = [process_sequence(sequence)]
                print("Got here for ", intermediate_dict['name'])
                print(intermediate_dict["elements"])

        result_dict['complexType'].append(intermediate_dict)
    return result_dict['complexType']


def to_dict(dict_list):
    """
        Convert to a JSON schema style dictionary
        - Remove name
        - Use the name as the key
    """

    final_dict = {}

    for mydict in dict_list:
        name = mydict['name']
        mydict.pop("name", None)
        final_dict[name] = mydict

    return final_dict


def to_dict_elems(elem_list):
    """
        Convert element list of lists to a dictionary
    """

    # Example input
    # elem_list = [
    #     [{'name': 'Point', 'type': 'Point', 'minOccurs': '2', 'maxOccurs': 'unbounded'},
    #         {'name': 'CenterPoint', 'type': 'Point', 'minOccurs': '0'}]
    # ]

    final_dict = {}

    # handle xs:choice field
    if len(elem_list) > 1:
        final_dict = {"oneOf": []}
        for dict_list in elem_list:
            final_dict["oneOf"].append(to_dict(dict_list))
    else:
        final_dict = to_dict(elem_list[0])

    return final_dict


def process_type(elem_type):
    """
        Returns a link to a type in definitions
        or a base type
    """

    if elem_type in ['string', 'decimal', 'dateTime', 'int', 'integer', 'date', 'anyURI']:
        return elem_type
    else:
        return {"$ref": f"#/definitions/{elem_type}"}


def process_elem_dict(elems_dict):
    """
        Converts stuff to an array if necessary
        Adds #/definitions/ to the type definition if necessary
        Changes minOccurs -> minItems, maxOccurs -> maxItems inside array
        Sets as optional if minOccurs = 0
    """

    # Example of input
    # elems_dict = {"DataCenter": {"type": "string", "minLength": 1, "maxLength": 80,
    # "minOccurs": "0", },
    # "Collections": {"type": "ListOfCollections", "minOccurs": "0", }, }

    for elem_name, elem in elems_dict.items():
        try:
            elem_type = elem["type"]
        except KeyError:
            # print(f'setting {elem_name} type to string')
            elem_type = 'string'

        min_occurs = 'minOccurs' in elem
        max_occurs = 'maxOccurs' in elem

        min_0 = (min_occurs and elem['minOccurs'] == "0")
        optional = min_0 and not max_occurs
        no_occurs = not min_occurs and not max_occurs

        # not an array
        if optional or no_occurs:
            elem["type"] = process_type(elem_type)
        # an array
        else:
            elem["type"] = "array"
            elem["items"] = process_type(elem_type)

        # is min_occurs used to represent optional
        if min_occurs:
            if optional:
                elem['required'] = False
            else:
                elem['minItems'] = elem['minOccurs']
            elem.pop('minOccurs')

        if max_occurs:
            elem['maxItems'] = elem['maxOccurs']
            elem.pop('maxOccurs')

    return elems_dict


def complex_types_to_json_schema(complex_t_dict):
    """
        Takes a regular dictionary of complex types
        and makes it conform to JSON schema standard vocabulary
    """

    for item in complex_t_dict.values():
        elems = item['elements']

        if (len(elems) == 0):
            import ipdb
            ipdb.set_trace()

        elems_dict = to_dict_elems(elems)

        item["type"] = "object"

        # xs:choice fields are handled differently
        if 'oneOf' in elems_dict:
            properties = {"oneOf": [process_elem_dict(d) for d in elems_dict['oneOf']]}
        else:
            properties = process_elem_dict(elems_dict)

        item["properties"] = properties

        # eliminate elements entirely
        item.pop("elements", None)
    return complex_t_dict


if __name__ == '__main__':
    simple_types = process_simpletypes()
    complex_types = process_complextypes()

    simple_types_dictionary = to_dict(simple_types)
    complex_types_dictionary = complex_types_to_json_schema(to_dict(complex_types))

    final_schema = {
        "$schema": "http://json-schema.org/schema#",
        # definitions of simple types and complex types go together
        "definitions": {**simple_types_dictionary, **complex_types_dictionary},
        # here we only have definitions of types. The actual schema would look like:
        # "type": "object",
        # "properties": {}
    }

    # output to a json file
    print(f"Writing to {str(OUTPUT_FILE)}")
    with open(OUTPUT_FILE, 'w') as testing:
        testing.write(json.dumps(final_schema))
