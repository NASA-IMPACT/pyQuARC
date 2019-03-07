from schema_builders import *

SCHEMA_URL_DIF = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd'
SCHEMA_URL_ECHO = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/raw/schemas/10.0/Collection.xsd'

#
# testDif = SchemaBuilder(SCHEMA_URL_DIF)
# testDif.print_xsd_structure()
# testDif.save_json('test_DIF.json')

testEcho = SchemaBuilder(SCHEMA_URL_ECHO)
# testEcho.print_xsd_structure()
# testEcho.save_json('no control.json')


