'''
DIF Schema Builder
This class allows a user to input a schema URL, and then export it to the console, as a python dict, or a JSON file.
The URL can be specified at init or after creation using the xsd_import method.
'''

# Import necessary libraries
import requests
import json
from io import BytesIO
from lxml import etree
import re

# shared global values
SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'
BENCHMARK_DICT = {"GranuleSpatialRepresentationEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC", "ORBIT", "NO_SPATIAL"]}}, "CoordinateSystemEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC"]}}, "OrganizationPersonnelRoleEnum": {"restriction": {"type": "string", "values": ["DATA CENTER CONTACT"]}}, "DistributionSizeUnitTypeEnum": {"restriction": {"type": "string", "values": ["KB", "MB", "GB", "TB", "PB"]}}, "DistributionFormatTypeEnum": {"restriction": {"type": "string", "values": ["Native", "Supported"]}}, "OrganizationTypeEnum": {"restriction": {"type": "string", "values": ["DISTRIBUTOR", "ARCHIVER", "ORIGINATOR", "PROCESSOR"]}}, "PersonnelRoleEnum": {"restriction": {"type": "string", "values": ["INVESTIGATOR", "INVESTIGATOR, TECHNICAL CONTACT", "METADATA AUTHOR", "METADATA AUTHOR, TECHNICAL CONTACT", "TECHNICAL CONTACT"]}}, "PlatformTypeEnum": {"restriction": {"type": "string", "values": ["Not provided", "Not applicable", "Aircraft", "Balloons/Rockets", "Earth Observation Satellites", "In Situ Land-based Platforms", "In Situ Ocean-based Platforms", "Interplanetary Spacecraft", "Maps/Charts/Photographs", "Models/Analyses", "Navigation Platforms", "Solar/Space Observation Satellites", "Space Stations/Manned Spacecraft"]}}, "DatasetLanguageEnum": {"restriction": {"type": "string", "values": ["English", "Afrikaans", "Arabic", "Bosnian", "Bulgarian", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "Estonian", "Finnish", "French", "German", "Hebrew", "Hungarian", "Indonesian", "Italian", "Japanese", "Korean", "Latvian", "Lithuanian", "Norwegian", "Polish", "Portuguese", "Romanian", "Russian", "Slovak", "Spanish", "Ukrainian", "Vietnamese"]}}, "CollectionDataTypeEnum": {"restriction": {"type": "string", "values": ["SCIENCE_QUALITY", "NEAR_REAL_TIME", "ON_DEMAND", "OTHER"]}}, "ProductFlagEnum": {"restriction": {"type": "string", "values": ["Not provided", "DATA_PRODUCT_FILE", "INSTRUMENT_ANCILLARY_FILE", "SYSTEM/SPACECRAFT_FILE", "EXTERNAL_DATA"]}}, "DurationUnitEnum": {"restriction": {
    "type": "string", "values": ["DAY", "MONTH", "YEAR"]}}, "SpatialCoverageTypeEnum": {"restriction": {"type": "string", "values": ["Horizontal", "HorizontalVertical", "Orbit", "Vertical", "Horizon&Vert"]}}, "PhoneTypeEnum": {"restriction": {"type": "string", "values": ["Direct Line", "Primary", "Telephone", "Fax", "Mobile", "Modem", "TDD/TTY Phone", "U.S. toll free", "Other"]}}, "MetadataAssociationTypeEnum": {"restriction": {"type": "string", "values": ["Parent", "Child", "Related", "Dependent", "Input", "Science Associated"]}}, "PrivateEnum": {"restriction": {"type": "string", "values": ["True", "False"]}}, "MetadataVersionEnum": {"restriction": {"type": "string", "values": ["VERSION 9.8.1", "VERSION 9.8.2", "VERSION 9.8.2.2", "VERSION 9.8.3", "VERSION 9.8.4", "VERSION 9.9.3", "VERSION 10.2"]}}, "ProductLevelIdEnum": {"restriction": {"type": "string", "values": ["Not provided", "0", "1", "1A", "1B", "1T", "2", "2G", "2P", "3", "4", "NA"]}}, "DatasetProgressEnum": {"restriction": {"type": "string", "values": ["PLANNED", "IN WORK", "COMPLETE", "NOT APPLICABLE", "NOT PROVIDED"]}}, "DisplayableTextEnum": {"restriction": {"type": "string", "values": ["text/plain", "text/markdown"]}}, "DisplayableTextTypeBaseType": {"restriction": {"type": "string"}}, "PersistentIdentifierType": {"sequences": [{"elements": [{"type": "PersistentIdentifierEnum", "name": "Type"}, {"type": "string", "name": "Identifier"}, {"name": "Authority", "minOccurs": "0", "restriction": {"type": "string", "maxLength": "80", "minLength": "1"}}]}, {"elements": [{"type": "MissingReasonEnum", "name": "MissingReason"}, {"type": "string", "name": "Explanation", "minOccurs": "0"}]}]}, "PersistentIdentifierEnum": {"restriction": {"type": "string", "values": ["DOI", "ARK"]}}, "MissingReasonEnum": {"restriction": {"type": "string", "values": ["Not applicable"]}}, "DateOrEnumType": {}, "TimeOrEnumType": {}, "DateOrTimeOrEnumType": {}, "DateEnum": {"restriction": {"type": "string", "values": ["Not provided", "unknown", "present", "unbounded", "future"]}}, "UuidType": {"restriction": {"type": "string"}}}


class DifSchemaBuilder:

    def __init__(self, schema_url_input=SCHEMA_URL):
        '''
        Purpose: Initializes all class-wide variables, including importing the default schema and building a default tree.
        Arguments: Accepts a schema_url from the user. This should be a valid XSD file, as there is no error checking.
        Network: Internal function, is called on initialization.
        '''

        self.schema_dict = dict()
        self.schema_tree = None
        self.test_result = True
        self.xsd_import(schema_url_input)
        self.build_dict()  # building the dictionary upon init allows the user to save directly

    def xsd_import(self, schema_url_input):
        '''
        Purpose: Grabs xsd from the internet and creates an eTree object.
        Arguments: Accepts a valid schema_url. There is no error checking.
        Network: External function, is called during init, but can also be modified by user after class creation.
        '''

        response = requests.get(schema_url_input)
        schema_file = BytesIO(response.content)
        try:
            self.schema_tree = etree.parse(schema_file)
        except:
            print('Schema import failed. Check that URL input leads to a valid XSD file. Schema file not updated.')
            self.test_result = False

    def save_json(self):
        '''
        Purpose: Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        if self.test_result == False:
            return print('Save JSON aborted')

        self.schema_dict = self.build_dict()

        with open('tree_dict_refactor.json', 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def self_test(self):
        '''
        Purpose: Compares self.build_dict() output against the benchmark dict stored in memory. Allows for easy testing of new code changes.
        '''

        print()

        # query the known schema to compare against the known python dict
        self.xsd_import('https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster')

        if self.build_dict() == BENCHMARK_DICT and self.test_result:
            print('Self test passed')
        else:
            print('Self test failed')

    def build_dict(self):
        '''
        Function: Searches for all simples types and processes them.
        '''

        for simpleType in self.schema_tree.findall(BASE_SCHEMA + 'simpleType'):
            simpleType_name = simpleType.get('name')
            self.schema_dict[simpleType_name] = {}

            for restriction in simpleType.findall(BASE_SCHEMA + 'restriction'):
                restriction_type = restriction.get('base').replace('xs:', '')
                self.schema_dict[simpleType_name]['restriction'] = {'type': restriction_type}

                enum_test = restriction.find(BASE_SCHEMA + 'enumeration')
                if enum_test != None:
                    enumeration_list = []
                    for enumeration in restriction.findall(BASE_SCHEMA + 'enumeration'):
                        enumeration_list.append(enumeration.get('value'))
                    self.schema_dict[simpleType_name]['restriction']['values'] = enumeration_list

                patern = restriction.find(BASE_SCHEMA + 'pattern')
                if patern != None:
                    pattern_value = patern.get('value')
                    self.schema_dict[simpleType_name]['restriction']['patern'] = pattern_value

            for union in simpleType.findall(BASE_SCHEMA + 'union'):
                self.schema_dict[simpleType_name]['union'] = {'memberTypes': union.get('memberTypes')}

        for complexType in self.schema_tree.findall(BASE_SCHEMA + 'complexType'):
            complexType_name = complexType.get('name')
            self.schema_dict[complexType_name] = {}

            for choice in complexType.findall(BASE_SCHEMA + 'choice'):
                self.schema_dict[complexType_name] = {'sequences': []}

                for count_seq, sequence in enumerate(choice.findall(BASE_SCHEMA + 'sequence')):
                    self.schema_dict[complexType_name]['sequences'].append({'elements': []})

                    for count_elem, element in enumerate(sequence):
                        self.schema_dict[complexType_name]['sequences'][count_seq]['elements'].append({})

                        for item in ['type', 'name', 'minOccurs', 'maxOccurs']:
                            if element.get(item) != None:
                                self.schema_dict[complexType_name]['sequences'][count_seq]['elements'][count_elem][item] = element.get(item).replace('xs:', '')

                        for simpleType in element.findall(BASE_SCHEMA + 'simpleType'):
                            for restriction in simpleType.findall(BASE_SCHEMA+'restriction'):
                                self.schema_dict[complexType_name]['sequences'][count_seq]['elements'][count_elem]['restriction'] = {'type': restriction.get('base').replace('xs:', '')}

                                for maxLength in restriction.findall(BASE_SCHEMA + 'maxLength'):
                                    self.schema_dict[complexType_name]['sequences'][count_seq]['elements'][count_elem]['restriction']['maxLength'] = maxLength.get('value')

                                for minLength in restriction.findall(BASE_SCHEMA + 'minLength'):
                                    self.schema_dict[complexType_name]['sequences'][count_seq]['elements'][count_elem]['restriction']['minLength'] = minLength.get('value')

        return self.schema_dict
