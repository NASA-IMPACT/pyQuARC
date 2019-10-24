import json
import xmltodict

from pathlib import Path

p = Path(__file__).resolve().parents[2]


INPUT_XSD = 'Collection.xsd'
OUTPUT_JSON = 'collection.json'

INPUT_DIR = p / 'data' / 'xsd'
OUTPUT_DIR = p / 'output'

with open(INPUT_DIR / INPUT_XSD, 'r') as collection_xml:
    o = xmltodict.parse(collection_xml.read())

with open(OUTPUT_DIR / OUTPUT_JSON, 'w') as metadata:
    metadata.write(json.dumps(o))
