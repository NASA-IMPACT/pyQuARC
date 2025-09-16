import json
import xml.etree.ElementTree as ET

def get_fields_to_apply(json_path):
    with open(json_path, 'r') as f:
        rules = json.load(f)
    schema_fields = {'echo-c': set(), 'echo-g': set(), 'dif10': set()}
    for rule in rules.values():
        if "fields_to_apply" in rule:
            for schema in schema_fields.keys():
                if schema in rule["fields_to_apply"]:
                    for block in rule["fields_to_apply"][schema]:
                        fields = block.get("fields", [])
                        for path in fields:
                            schema_fields[schema].add(path)
    for schema in schema_fields:
        schema_fields[schema] = sorted(schema_fields[schema])
    return schema_fields

def get_xsd_elements(xsd_path):
    tree = ET.parse(xsd_path)
    root = tree.getroot()
    namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    elements = set()
    for elem in root.findall('.//xs:element', namespace):
        name = elem.get('name')
        if name:
            elements.add(name)
    return elements

def check_fields_in_xsd(fields, xsd_elements):
    result = {}
    for field_path in fields:
        segments = field_path.split('/')
        result[field_path] = all(seg in xsd_elements for seg in segments)
    return result

RULES_JSON_PATH = 'rule_mapping.json'
SCHEMA_PATHS = {
    'echo-c': 'echo-c_schema.xsd',
    'echo-g': 'echo-g_schema.xsd',
    'dif10': 'dif10_schema.xsd'
}

if __name__ == "__main__":
    all_fields = get_fields_to_apply(RULES_JSON_PATH)
    for schema, xsd_path in SCHEMA_PATHS.items():
        # Load only if there are fields for this schema
        if all_fields[schema]:
            xsd_elems = get_xsd_elements(xsd_path)
            check = check_fields_in_xsd(all_fields[schema], xsd_elems)
            for path, exists in check.items():
                if not exists:
                    print(f"{schema.upper()} {path}: Missing")
