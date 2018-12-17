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


class DifSchemaBuilder:
    def __init__(self):
        self.dif_dictionary = dict()

    def parse_url(self, schema_url_input=SCHEMA_URL):
        response = requests.get(schema_url_input)
        schema_xsd = BytesIO(response.content)
        xsd_file = etree.parse(schema_xsd)
        return xsd_file

    def build_schema(self):
        schema_output = []
        type_output = []
        # parse value function
        for variable in VARIABLE_LIST:
            for value in self.parse_url(SCHEMA_URL).findall('*'):
                if value.get('name') == variable:
                    restrictions = value.findall(
                        '{http://www.w3.org/2001/XMLSchema}restriction')[0]
                    type_output.append(restrictions.get('base'))
                    for restriction in restrictions.findall('*'):
                        schema_output.append(restriction.get('value'))
            self.dif_dictionary[variable] = schema_output

    def build_schema_new(self, schema_url_input=SCHEMA_URL):
        # retrieve, parse, and create iterable schema
        xsd_file = self.parse_url(schema_url_input)
        elements = xsd_file.findall('*')

        for element in elements:
            # element name
            element_name = element.get('name')
            self.dif_dictionary[element_name] = {}

            # restrictions
            for restriction in element.findall('{http://www.w3.org/2001/XMLSchema}restriction'):
                self.dif_dictionary[element_name]['Restriction Type'] = restriction.get('base')
                enumerations = []
                for enumeration in restriction:
                    enumerations.append(enumeration.get('value'))
                self.dif_dictionary[element_name]['Restriction List'] = enumerations

            # documentation
            for annotation in element.findall('{http://www.w3.org/2001/XMLSchema}annotation'):
                for documentation in annotation.findall('{http://www.w3.org/2001/XMLSchema}documentation'):
                    self.dif_dictionary[element_name]['Documentation'] = documentation.text.strip()

    def save(self):
        with open('dif_schema_output_new.json', 'w') as outfile:
            json.dump(self.dif_dictionary, outfile)
