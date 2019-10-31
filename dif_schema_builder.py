'''
DIF Schema Builder
'''

# Import necessary libraries
import requests
import json
from io import BytesIO
from lxml import etree

# Shared global values
SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
VARIABLE_LIST = ['GranuleSpatialRepresentationEnum', 'CoordinateSystemEnum',
                 'OrganizationTypeEnum', 'PersonnelRoleEnum', 'DatasetLanguageEnum',
                 'SpatialCoverageTypeEnum', 'PhoneTypeEnum', 'DatasetProgressEnum',
                 'PersistentIdentifierEnum']
dif_dictionary = dict()


class DifSchemaBuilder:
    def __init__(self):
        self.dif_dictionary = dict()

    def parse_url(self):
        response = requests.get(SCHEMA_URL)
        schema_xsd = BytesIO(response.content)
        xsd_file = etree.parse(schema_xsd)
        return xsd_file

    def build_schema(self):
        schema_output = []
        type_output = []
        # parse value function
        for variable in VARIABLE_LIST:
            for value in self.parse_url().findall('*'):
                if value.get('name') == variable:
                    restrictions = value.findall('{http://www.w3.org/2001/XMLSchema}restriction')[0]
                    type_output.append(restrictions.get('base'))
                    for restriction in restrictions.findall('*'):
                        schema_output.append(restriction.get('value'))
            self.dif_dictionary[variable] = schema_output

    def save(self):
        with open('dif_schema_output.json', 'w') as outfile:
            json.dump(self.dif_dictionary, outfile)
