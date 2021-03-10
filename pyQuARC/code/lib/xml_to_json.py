import json
import xmltodict

from pathlib import Path

# go up two directories # ../../
path = Path(__file__).resolve().parents[2]

INPUT_XSD = 'MetadataCommon.xsd'
OUTPUT_JSON = 'metadata.json'

INPUT_DIR = path / 'data' / 'xsd'
OUTPUT_DIR = path / 'output'

with open(INPUT_DIR / INPUT_XSD, 'r') as collection_xml:
    parsed = xmltodict.parse(collection_xml.read())

with open(OUTPUT_DIR / OUTPUT_JSON, 'w') as metadata:
    metadata.write(json.dumps(parsed))
