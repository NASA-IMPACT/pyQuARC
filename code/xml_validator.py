from lxml import etree
from io import BytesIO
import os
from urllib.request import pathname2url
import re

from constants import ECHO10, SCHEMA_PATHS


# if "XML_CATALOG_FILES" not in os.environ:
#     # Path to catalog must be a url.
#     catalog_path = f"file:{pathname2url(str(SCHEMA_PATHS['catalog']))}"
#     # Temporarily set the environment variable.
#     os.environ['XML_CATALOG_FILES'] = catalog_path

# # open and read schema file
# with open(SCHEMA_PATHS[ECHO10], 'r') as schema_file:
#     schema_to_check = schema_file.read().encode()

# # open and read xml file
# with open("tests/fixtures/test_cmr_metadata.echo10", 'r') as xml_file:
#     xml_to_check = xml_file.read().encode()

# xmlschema_doc = etree.parse(BytesIO(schema_to_check))
# xmlschema = etree.XMLSchema(xmlschema_doc)

# # parse xml
# try:
#     doc = etree.parse(BytesIO(xml_to_check))
#     print('XML well formed, syntax ok.')

# # check for file IO error
# except IOError:
#     print('Invalid File')

# # check for XML syntax errors
# except etree.XMLSyntaxError as err:
#     print('XML Syntax Error, see error_syntax.log')
#     with open('error_syntax.log', 'w') as error_log_file:
#         error_log_file.write(str(err.error_log))
#     quit()

# except:
#     print('Unknown error, exiting.')
#     quit()

# # validate against schema
# try:
#     xmlschema.assertValid(doc)
#     print('XML valid, schema validation ok.')

# except etree.DocumentInvalid as err:
#     print('Schema validation error, see error_schema.log')
#     with open('error_schema.log', 'w') as error_log_file:
#         error_log_file.write(str(err.error_log))
#     quit()

# except:
#     print('Unknown error, exiting.')
#     quit()

with open('error_schema.log', 'r') as filename:
    content = filename.read()

lines = content.splitlines()
messages = [
    {
        "message": re.search("Element\s\'\w+\':\s(\[.*\])?(.*)", line)[2].strip(),
        "field": re.search("Element\s\'(\w+)\'", line)[1]
    }
    for line in lines
    ]
import json
print(json.dumps(messages, indent=4))