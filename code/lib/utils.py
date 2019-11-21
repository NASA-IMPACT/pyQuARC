def _min_occurs(x):
    return "@minOccurs" in x


def _max_occurs(x):
    return "@maxOccurs" in x


def _min_0(x):
    return _min_occurs(x) and x.get("@minOccurs") == "0"


def _optional(x):
    return _min_0(x) and not _max_occurs(x)


def _no_occurs(x):
    return not _min_occurs(x) and not _max_occurs(x)


def _int_function(val):
    return int(val)


def _float_function(val):
    return float(val)


def _process_type(elem_type):
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


def _name_extractor(inp_obj):
    try:
        return {"name": inp_obj["@name"]}
    except KeyError:
        # this lets us know when some object doesn't have a name
        import ipdb
        ipdb.set_trace()


def _description_extractor(inp_obj):
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


def _type_extractor(inp_obj):
    """
        Extract the type information from the input object
    """

    # the order of ifs matter, hence the mapping is not put in a dictionary
    field_type = "string"
    if "xs:simpleType" in inp_obj:
        return _type_extractor(inp_obj["xs:simpleType"])

    if "xs:simpleContent" in inp_obj:
        temp = inp_obj["xs:simpleContent"]["xs:extension"]
        temp_dict = _process_type(temp["@base"])
        temp_dict.update({"type_ref": temp["xs:attribute"]["@type"]})
        return temp_dict

    elif "xs:complexContent" in inp_obj:
        temp = inp_obj["xs:complexContent"]["xs:extension"]
        return _process_type(temp["@base"])

    elif "xs:sequence" in inp_obj or "xs:choice" in inp_obj:
        field_type = "object"

    elif "xs:restriction" in inp_obj:
        field_type = _process_type(inp_obj["xs:restriction"]["@base"])

    elif not (_optional(inp_obj) or _no_occurs(inp_obj)):
        field_type = "array"

    elif "@type" in inp_obj:
        field_type = _process_type(inp_obj["@type"])

    else:
        field_type = "N/A"

    if isinstance(field_type, dict):
        return field_type
    return {"type": field_type}


def _optional_extractor(inp_object):
    """
        Determine if an object is _optional
    """

    if _min_occurs(inp_object) and _optional(inp_object):
        return {"_optional": True}
    return {}


extraction_keys = ["name", "description", "type", "optional"]
key_extractor_fuctions = {
    "name": _name_extractor,
    "description": _description_extractor,
    "type": _type_extractor,
    "optional": _optional_extractor,
}


global_conversion_schema = {
    'minLength': {
        'in_key': 'xs:minLength',
        'converter_function': _int_function
    },
    'maxLength': {
        'in_key': 'xs:maxLength',
        'converter_function': _int_function
    },
    'inclusiveMinimum': {
        'in_key': 'xs:minInclusive',
        'converter_function': _float_function
    },
    'inclusiveMaximum': {
        'in_key': 'xs:maxInclusive',
        'converter_function': _float_function
    },
    'exclusiveMinimum': {
        'in_key': 'xs:minExclusive',
        'converter_function': _float_function
    },
    'exclusiveMaximum': {
        'in_key': 'xs:maxExclusive',
        'converter_function': _float_function
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
        'converter_function': _int_function
    },
    'maxItems': {
        'in_key': '@maxOccurs',
        'converter_function': _int_function
    },
    'items': {
        'in_key': '@type',
        'converter_function': lambda x: _process_type(x)
    }
}
