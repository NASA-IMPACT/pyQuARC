import json
import requests
import os
import xml.etree.ElementTree as ET


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
    'echo-c': 'schema_echo_c.json',
    'echo-g': 'schema_echo_g.json',
    'dif10':  'schema_diff10.json',
    'umm-c':  'schema_umm_c.json',      
    'umm-g':  'schema_umm_g.json'       
}


def download_schema_files():
    """Downloads schema files from URLs if they don't exist locally."""
    for schema, url in SCHEMA_URLS.items():
        out_filename = LOCAL_FILE_NAMES[schema]
        if not os.path.exists(out_filename):
            print(f"Downloading {schema} schema...")
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(out_filename, 'w', encoding="utf-8") as f:
                        f.write(r.text)
                    print(f"✅ Saved to {out_filename}")
                else:
                    print(f"❌ Failed to download {schema} schema: {r.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error downloading {schema} schema: {e}")
        else:
            print(f"☑️ {out_filename} already exists, skipping download.")


def extract_all_xsd_element_names(xsd_path, json_out_path):
    """Parses XSD to extract ALL unique element names (at all levels)."""
    try:
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        # Use common XSD namespace
        namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        elements = set()
        
        # Find all element tags, regardless of depth or complex type nesting
        for elem in root.findall('.//xs:element', namespace):
            name = elem.get('name')
            if name:
                elements.add(name)
        
        with open(json_out_path, "w") as f:
            json.dump(list(elements), f, indent=2)
        print(f"✅ Extracted ALL element names (at all levels) to {json_out_path}")
        return elements
    except Exception as e:
        print(f"❌ Error parsing XSD {xsd_path}: {e}")
        return set()

def extract_all_umm_properties_recursively(data, property_names):
    """Recursively extracts all property names from UMM JSON Schema."""
    if isinstance(data, dict):
        if "properties" in data:
            for name, sub_data in data["properties"].items():
               
                clean_name = name.split('?')[0]
                property_names.add(clean_name)
                
                extract_all_umm_properties_recursively(sub_data, property_names)
        
        
        if "items" in data:
            extract_all_umm_properties_recursively(data["items"], property_names)
            
       
        for key in ["anyOf", "allOf", "oneOf"]:
            if key in data and isinstance(data[key], list):
                for sub_schema in data[key]:
                    extract_all_umm_properties_recursively(sub_schema, property_names)
        
        
        for value in data.values():
            extract_all_umm_properties_recursively(value, property_names)

def get_element_names_from_json(json_path, is_umm=False):
    """Loads JSON element file (XSD converted) or parses UMM schema for all names."""
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if not is_umm:  
            return set(data)
        else:           
            property_names = set()
            extract_all_umm_properties_recursively(data, property_names)
            return property_names
    except Exception as e:
        print(f"❌ Error loading or parsing {json_path}: {e}")
        return set()


def get_fields_to_apply(json_path):
    """Loads rules and extracts all field paths, grouped by schema."""
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



def check_all_segments_of_paths(paths, element_names):
    """Checks every segment of every nested path against the set of all known element names."""
    missing_segments = []
    
    for full_path in paths:
       
        segments = [s.split('?')[0] for s in full_path.split('/')]
        
        for segment in segments:
          
            if not segment:
                continue

            if segment not in element_names:
                missing_segments.append((full_path, segment))
                break 
    
    if missing_segments:
        print("\n❌ MISSING SEGMENTS FOUND:")
        for path, segment in missing_segments:
            print(f"Path: {path}, Segment '{segment}' is missing in the schema's element list.")
    else:
        print("\n✅ All segments in all paths are present in the schema's element list.")


if __name__ == "__main__":
    RULES_JSON_PATH = "rule_mapping.json" 

    print("--- STEP 1: DOWNLOAD SCHEMAS ---")
    download_schema_files()

    print("\n--- STEP 2: EXTRACT ALL SCHEMA ELEMENT/PROPERTY NAMES ---")
    # Convert XSDs to a flat list of ALL element names (at any level)
    for key in ["echo-c", "echo-g", "dif10"]:
        xsd_path = LOCAL_FILE_NAMES[key]
        json_path = ELEMENT_JSONS[key]
        if not os.path.exists(json_path) or json_path.endswith("_all_elements.json"):
            extract_all_xsd_element_names(xsd_path, json_path)
        else:
            print(f"☑️ {json_path} already exists, skipping conversion.")


    print("\n--- STEP 3 & 4: LOAD RULES AND SCHEMA ELEMENTS ---")
    all_fields = get_fields_to_apply(RULES_JSON_PATH)
    
    for schema, json_path in ELEMENT_JSONS.items():
        field_paths = all_fields.get(schema)
        if field_paths:
            print(f"\nProcessing {schema.upper()}...")
            is_umm = schema in {"umm-c", "umm-g"}
            element_names = get_element_names_from_json(json_path, is_umm)
            
            # For debugging/verification, print the count and first few elements
            print(f"Schema has {len(element_names)} unique element/property names.")
            
            # --- Perform the deep check (MODIFIED STEP 5) ---
            print(f"\nChecking all {len(field_paths)} field paths for {schema.upper()}...")
          
            check_all_segments_of_paths(field_paths, element_names)
        else:
            print(f"No rules found for {schema.upper()}.")