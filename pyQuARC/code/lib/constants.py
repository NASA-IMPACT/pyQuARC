_int_num_type = [
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
    "integer": _int_num_type,
    "number": _int_num_type,
    # type objects use the same thing
}
