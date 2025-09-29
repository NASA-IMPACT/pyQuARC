import json
import requests
import os
import xml.etree.ElementTree as ET

# Step 1: Download schemas from URLs if not present
SCHEMA_URLS = {
    'echo-c': 'https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/raw/schemas/10.0/Collection.xsd?at=refs%2Fheads%2Fmaster',
    'echo-g': 'https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/raw/schemas/10.0/Granule.xsd?at=refs%2Fheads%2Fmaster',
    'dif10':  'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/dif_v10.3.xsd?at=refs%2Fheads%2Fmaster',
    'umm-c':  'https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/raw/collection/v1.18.4/umm-c-json-schema.json?at=refs%2Fheads%2Fmaster',
    'umm-g':  'https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/raw/granule/v1.6.6/umm-g-json-schema.json?at=refs%2Fheads%2Fmaster'
}

LOCAL_FILE_NAMES = {
   'echo-c': 'schema_echo_c.xsd',
    'echo-g': 'schema_echo_g.xsd',
    'dif10':  'schema_diff10.xsd',
    'umm-c':  'schema_umm_c.json',
    'umm-g':  'schema_umm_g.json'
}
ELEMENT_JSONS = {
    'echo-c': 'Collection_elements.json',
    'echo-g': 'Granule_elements.json',
    'dif10':  'dif10_elements.json',
    'umm-c':  'schema_umm_c.json',      # already a JSON schema
    'umm-g':  'schema_umm_g.json'
}

def download_schema_files():
    for schema, url in SCHEMA_URLS.items():
        out_filename = LOCAL_FILE_NAMES[schema]
        if not os.path.exists(out_filename):
            print(f"Downloading {schema} schema from {url} ...")
            r = requests.get(url)
            if r.status_code == 200:
                with open(out_filename, 'w', encoding="utf-8") as f:
                    f.write(r.text)
                print(f"Saved to {out_filename}")
            else:
                print(f"Failed to download {schema} schema: {r.status_code}")
        else:
            print(f"{out_filename} already exists, skipping download.")

# Step 2: Extract element names from XSDs to JSONs (your function)
def extract_element_names(xsd_path, json_out_path):
    tree = ET.parse(xsd_path)
    root = tree.getroot()
    namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    elements = set()
    for elem in root.findall('.//xs:element', namespace):
        name = elem.get('name')
        if name:
            elements.add(name)
    with open(json_out_path, "w") as f:
        json.dump(list(elements), f, indent=2)
    print(f"Extracted element names to {json_out_path}")

# Step 3: Load rules mapping field paths
def get_fields_to_apply(json_path):
    with open(json_path, "r") as f:
        rules = json.load(f)
    schema_fields = {k: set() for k in ELEMENT_JSONS.keys()}
    for rule in rules.values():
        if "fields_to_apply" in rule:
            for schema in schema_fields.keys():
                if schema in rule["fields_to_apply"]:
                    for block in rule["fields_to_apply"][schema]:
                        for path in block.get("fields", []):
                            schema_fields[schema].add(path)
    for schema in schema_fields:
        schema_fields[schema] = sorted(schema_fields[schema])
    return schema_fields

# Step 4: Load JSON element file (XSD converted or UMM JSON schema)
def get_element_names_from_json(json_path, is_umm=False):
    with open(json_path, "r") as f:
        data = json.load(f)
    if not is_umm:  # XSD elements: list
        return set(data)
    else:           # UMM: schema dict
        if "properties" in data:
            return set(data["properties"].keys())
        else:
            return set(data.keys())

# Step 5: Check fields
def check_paths_in_json(paths, element_names, schema):
    for path in paths:
        segments = path.split('/')
        fieldname = segments[0] if schema in {"umm-c", "umm-g"} else segments[-1]
        if fieldname not in element_names:
            print(f"{schema.upper()} From path: {path}, {fieldname}: Missing in schema")

# Main workflow
if __name__ == "__main__":
    download_schema_files()

    # Convert XSDs to element list JSONs
    for key in ["echo-c", "echo-g", "dif10"]:
        xsd_path = LOCAL_FILE_NAMES[key]
        json_path = ELEMENT_JSONS[key]
        if not os.path.exists(json_path):
            extract_element_names(xsd_path, json_path)
        else:
            print(f"{json_path} already exists, skipping conversion.")

    # Do the field checking
    RULES_JSON_PATH = "rule_mapping.json"
    all_fields = get_fields_to_apply(RULES_JSON_PATH)
    for schema, json_path in ELEMENT_JSONS.items():
        field_paths = all_fields[schema]
        if field_paths:
            print(f"\nChecking {schema.upper()}:")
            is_umm = schema in {"umm-c", "umm-g"}
            element_names = get_element_names_from_json(json_path, is_umm)
            check_paths_in_json(field_paths, element_names, schema)
