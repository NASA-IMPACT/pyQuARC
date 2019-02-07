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

# shared global values
SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'

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

    def save_json(self, json_path='tree_dict.json'):
        '''
        Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        self.schema_dict = self.build_dict()

        if self.schema_tree is None:
            print('Object schema tree is blank. Empty JSON saved.')

        with open(json_path, 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def build_dict(self):
        '''
        Creates a custom python dictionary from the XSD file selected upon init or given in self.xsd_import().
        '''

        self.schema_dict = {}
        if self.schema_tree is None:
            print('Object schema tree is blank. Object schema dict is now empty.')
        else:
            self._type_finder('simpleType', self._get_simple_types)
            self._type_finder('complexType', self._get_complex_types)
        return self.schema_dict

    def _type_finder(self, elem_type_str, get_func):
        for elem_type in self.schema_tree.findall(BASE_SCHEMA + elem_type_str):
            elem_type_name = elem_type.get('name')
            self.schema_dict[elem_type_name] = {}
            elem_parent = self.schema_dict[elem_type_name]

            get_func(elem_parent, elem_type)

    def _get_simple_types(self, simple_parent, simple_type):

        # restrictions
        for restriction in simple_type.findall(BASE_SCHEMA + 'restriction'):
            restriction_type = restriction.get('base').replace('xs:', '')
            simple_parent['restriction'] = {'type': restriction_type}

            for enumeration in restriction.findall(BASE_SCHEMA + 'enumeration'):
                values = simple_parent['restriction'].get('values',[])
                values.append(enumeration.get('value'))
                simple_parent['restriction']['values'] = values

            # minLength, maxLength, pattern
            for attribute_str in ['minLength', 'maxLength', 'pattern']:  # len_lim_str is length limit string
                for attribute_obj in restriction.findall(BASE_SCHEMA + attribute_str):
                    simple_parent['restriction'][attribute_str] = attribute_obj.get('value')

        # unions
        for union in simple_type.findall(BASE_SCHEMA + 'union'):
            simple_parent['union'] = {'memberTypes': union.get('memberTypes')}

    def _get_complex_types(self, complex_parent, complex_type):

        # choices
        for choice in complex_type.findall(BASE_SCHEMA + 'choice'):
            complex_parent['sequences'] = []

            # sequences?
            for count_seq, sequence in enumerate(choice.findall(BASE_SCHEMA + 'sequence')):
                complex_parent['sequences'].append({'elements': []})

                # sequences?
                for count_elem, element in enumerate(sequence):
                    complex_parent['sequences'][count_seq]['elements'].append({})

                    # attributes
                    for attribute in ['type', 'name', 'minOccurs', 'maxOccurs']:
                        if element.get(attribute) is not None:
                            complex_parent['sequences'][count_seq]['elements'][count_elem][attribute] = element.get(attribute).replace('xs:', '')

                    # simpleTypes
                    simple_parent = complex_parent['sequences'][count_seq]['elements'][count_elem]
                    for simple_type in element.findall(BASE_SCHEMA + 'simpleType'):
                        self._get_simple_types(simple_parent, simple_type)
