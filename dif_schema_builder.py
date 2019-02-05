'''
DIF Schema Builder
This class allows a user to input a schema URL, and then export it as a python dict or a JSON file.
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
BENCHMARK_DICT = {"GranuleSpatialRepresentationEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC", "ORBIT", "NO_SPATIAL"]}}, "CoordinateSystemEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC"]}}, "OrganizationPersonnelRoleEnum": {"restriction": {"type": "string", "values": ["DATA CENTER CONTACT"]}}, "DistributionSizeUnitTypeEnum": {"restriction": {"type": "string", "values": ["KB", "MB", "GB", "TB", "PB"]}}, "DistributionFormatTypeEnum": {"restriction": {"type": "string", "values": ["Native", "Supported"]}}, "OrganizationTypeEnum": {"restriction": {"type": "string", "values": ["DISTRIBUTOR", "ARCHIVER", "ORIGINATOR", "PROCESSOR"]}}, "PersonnelRoleEnum": {"restriction": {"type": "string", "values": ["INVESTIGATOR", "INVESTIGATOR, TECHNICAL CONTACT", "METADATA AUTHOR", "METADATA AUTHOR, TECHNICAL CONTACT", "TECHNICAL CONTACT"]}}, "PlatformTypeEnum": {"restriction": {"type": "string", "values": ["Not provided", "Not applicable", "Aircraft", "Balloons/Rockets", "Earth Observation Satellites", "In Situ Land-based Platforms", "In Situ Ocean-based Platforms", "Interplanetary Spacecraft", "Maps/Charts/Photographs", "Models/Analyses", "Navigation Platforms", "Solar/Space Observation Satellites", "Space Stations/Manned Spacecraft"]}}, "DatasetLanguageEnum": {"restriction": {"type": "string", "values": ["English", "Afrikaans", "Arabic", "Bosnian", "Bulgarian", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "Estonian", "Finnish", "French", "German", "Hebrew", "Hungarian", "Indonesian", "Italian", "Japanese", "Korean", "Latvian", "Lithuanian", "Norwegian", "Polish", "Portuguese", "Romanian", "Russian", "Slovak", "Spanish", "Ukrainian", "Vietnamese"]}}, "CollectionDataTypeEnum": {"restriction": {"type": "string", "values": ["SCIENCE_QUALITY", "NEAR_REAL_TIME", "ON_DEMAND", "OTHER"]}}, "ProductFlagEnum": {"restriction": {"type": "string", "values": ["Not provided", "DATA_PRODUCT_FILE", "INSTRUMENT_ANCILLARY_FILE", "SYSTEM/SPACECRAFT_FILE", "EXTERNAL_DATA"]}}, "DurationUnitEnum": {"restriction": {"type": "string", "values": ["DAY", "MONTH", "YEAR"]}}, "SpatialCoverageTypeEnum": {"restriction": {"type": "string", "values": [
    "Horizontal", "HorizontalVertical", "Orbit", "Vertical", "Horizon&Vert"]}}, "PhoneTypeEnum": {"restriction": {"type": "string", "values": ["Direct Line", "Primary", "Telephone", "Fax", "Mobile", "Modem", "TDD/TTY Phone", "U.S. toll free", "Other"]}}, "MetadataAssociationTypeEnum": {"restriction": {"type": "string", "values": ["Parent", "Child", "Related", "Dependent", "Input", "Science Associated"]}}, "PrivateEnum": {"restriction": {"type": "string", "values": ["True", "False"]}}, "MetadataVersionEnum": {"restriction": {"type": "string", "values": ["VERSION 9.8.1", "VERSION 9.8.2", "VERSION 9.8.2.2", "VERSION 9.8.3", "VERSION 9.8.4", "VERSION 9.9.3", "VERSION 10.2"]}}, "ProductLevelIdEnum": {"restriction": {"type": "string", "values": ["Not provided", "0", "1", "1A", "1B", "1T", "2", "2G", "2P", "3", "4", "NA"]}}, "DatasetProgressEnum": {"restriction": {"type": "string", "values": ["PLANNED", "IN WORK", "COMPLETE", "NOT APPLICABLE", "NOT PROVIDED"]}}, "DisplayableTextEnum": {"restriction": {"type": "string", "values": ["text/plain", "text/markdown"]}}, "DisplayableTextTypeBaseType": {"restriction": {"type": "string"}}, "PersistentIdentifierEnum": {"restriction": {"type": "string", "values": ["DOI", "ARK"]}}, "MissingReasonEnum": {"restriction": {"type": "string", "values": ["Not applicable"]}}, "DateOrEnumType": {"union": {"memberTypes": "xs:date DateEnum"}}, "TimeOrEnumType": {"union": {"memberTypes": "xs:dateTime DateEnum"}}, "DateOrTimeOrEnumType": {"union": {"memberTypes": "xs:date xs:dateTime DateEnum"}}, "DateEnum": {"restriction": {"type": "string", "values": ["Not provided", "unknown", "present", "unbounded", "future"]}}, "UuidType": {"restriction": {"type": "string", "patern": "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89abAB][0-9a-f]{3}-[0-9a-f]{12}"}}, "PersistentIdentifierType": {"sequences": [{"elements": [{"type": "PersistentIdentifierEnum", "name": "Type"}, {"type": "string", "name": "Identifier"}, {"name": "Authority", "minOccurs": "0", "restriction": {"type": "string", "maxLength": "80", "minLength": "1"}}]}, {"elements": [{"type": "MissingReasonEnum", "name": "MissingReason"}, {"type": "string", "name": "Explanation", "minOccurs": "0"}]}]}}


class DifSchemaBuilder:

    def __init__(self, schema_url_input=SCHEMA_URL):
        '''
        Purpose: Initializes all class-wide variables, including importing the default schema and building a default tree.
        Arguments: Accepts a schema_url from the user. This should be a valid XSD file.
        '''

        self.schema_dict = dict()
        self.schema_tree = None

        self.xsd_import(schema_url_input)
        self.build_dict()  # building the dictionary upon init allows the user to save directly

    def xsd_import(self, schema_url_input):
        '''
        Purpose: Grabs xsd from the internet and creates an eTree object. Will flag invalid XLM.
        Arguments: Accepts a valid schema_url.
        Network: External function, is called during init, but can also be modified by user after class creation.
        '''

        response = requests.get(schema_url_input)
        schema_file = BytesIO(response.content)

        try:
            self.schema_tree = etree.parse(schema_file)
        except:
            self.schema_tree = None
            print('Schema import failed. Check that URL input leads to a valid XML file. Object schema tree is now blank.')

    def save_json(self):
        '''
        Purpose: Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        self.schema_dict = self.build_dict()

        if self.schema_tree == None:
            print('Object schema tree is blank. Empty JSON saved.')

        with open('tree_dict.json', 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def self_test(self):
        '''
        Purpose: Compares self.build_dict() output against the benchmark dict stored in memory. Allows for easy testing of new code changes.
        '''

        # query the known schema to compare against the known python dict
        self.xsd_import('https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster')

        if self.build_dict() == BENCHMARK_DICT:
            print('Self test passed')
        else:
            print('Self test failed')

    def build_dict(self):
        '''
        Function: Creates a custom python dictionary from the XSD file selected upon init or giving in self.xsd_import().
        '''

        if self.schema_tree == None:
            print('Object schema tree is blank. Object schema dict is now empty.')
            self.schema_dict = {}
            return self.schema_dict

        self._typeFinder('simpleType')
        self._typeFinder('complexType')

        return self.schema_dict

    def _typeFinder(self, elemTypeStr):
        for elemType in self.schema_tree.findall(BASE_SCHEMA + elemTypeStr):
            elemType_name = elemType.get('name')
            self.schema_dict[elemType_name] = {}
            elemParent = self.schema_dict[elemType_name]

            if elemTypeStr == 'simpleType':
                self._getSimpleTypes(elemParent, elemType)

            if elemTypeStr == 'complexType':
                self._getComplexTypes(elemParent, elemType)

    def _getSimpleTypes(self, simpleParent, simpleType):

        # restrictions
        for restriction in simpleType.findall(BASE_SCHEMA + 'restriction'):
            restriction_type = restriction.get('base').replace('xs:', '')
            simpleParent['restriction'] = {'type': restriction_type}

            # enumerations
            enum_test = restriction.find(BASE_SCHEMA + 'enumeration')
            if enum_test != None:
                enumeration_list = []
                for enumeration in restriction.findall(BASE_SCHEMA + 'enumeration'):
                    enumeration_list.append(enumeration.get('value'))
                simpleParent['restriction']['values'] = enumeration_list

            # maxLength
            for maxLength in restriction.findall(BASE_SCHEMA + 'maxLength'):
                simpleParent['restriction']['maxLength'] = maxLength.get('value')

            # minLength
            for minLength in restriction.findall(BASE_SCHEMA + 'minLength'):
                simpleParent['restriction']['minLength'] = minLength.get('value')

            # paterns
            patern = restriction.find(BASE_SCHEMA + 'pattern')
            if patern != None:
                pattern_value = patern.get('value')
                simpleParent['restriction']['patern'] = pattern_value

        # unions
        for union in simpleType.findall(BASE_SCHEMA + 'union'):
            simpleParent['union'] = {'memberTypes': union.get('memberTypes')}

    def _getComplexTypes(self, complexParent, complexType):

        # choices
        for choice in complexType.findall(BASE_SCHEMA + 'choice'):
            complexParent['sequences'] = []

            # sequences?
            for count_seq, sequence in enumerate(choice.findall(BASE_SCHEMA + 'sequence')):
                complexParent['sequences'].append({'elements': []})

                # sequences?
                for count_elem, element in enumerate(sequence):
                    complexParent['sequences'][count_seq]['elements'].append({})

                    # items
                    for item in ['type', 'name', 'minOccurs', 'maxOccurs']:
                        if element.get(item) != None:
                            complexParent['sequences'][count_seq]['elements'][count_elem][item] = element.get(item).replace('xs:', '')

                    # simpleTypes
                    newSimpleParent = complexParent['sequences'][count_seq]['elements'][count_elem]
                    for simpleType in element.findall(BASE_SCHEMA + 'simpleType'):
                        self._getSimpleTypes(newSimpleParent, simpleType)
