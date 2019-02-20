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
SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd'
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'


class DifSchema:

    def __init__(self, schema_url_input=SCHEMA_URL):
        '''
        Purpose: Initializes all class-wide variables, including importing the default schema and building a default tree.
        Arguments: Accepts a schema_url from the user. This should be a valid XSD file.
        '''

        self.schema_dict = dict()
        self.schema_tree = None
        self.schema_url = schema_url_input

        self.xsd_import(self.schema_url)
        self.build_dict()  # building the dictionary upon init allows the user to save directly

    def xsd_import(self, schema_url_input):
        '''
        Purpose: Grabs xsd from the internet and creates an eTree object. Will flag invalid XLM.
        Arguments: Accepts a valid schema_url.
        Network: External function, is called during init, but can also be modified by user after class creation.
        '''

        response = requests.get(schema_url_input, headers={'Connection': 'close'})
        schema_file = BytesIO(response.content)

        self.schema_tree = etree.parse(schema_file)  # could fail for a lot of reasons

    def save_json(self, json_path='DIF-10.json'):
        '''
        Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        self.build_dict()

        with open(json_path, 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def build_dict(self):
        '''
        Creates a custom python dictionary from the XSD file selected upon init or given in self.xsd_import().
        '''

        self.schema_dict = {}

        self.schema_dict.update(self._element_loop('simpleType', self._get_simple_data))
        self.schema_dict.update(self._element_loop('complexType', self._get_complex_data))

        return self.schema_dict

    def _element_loop(self, elem_type_str, get_data_func):

        loop_dict = {}

        for elem_obj in self.schema_tree.findall(BASE_SCHEMA + elem_type_str):
            elem_name = elem_obj.get('name')
            loop_dict[elem_name] = get_data_func(elem_obj)

        return loop_dict

    def _get_simple_data(self, simple_type):

        simple_dict = {}

        # unions
        for union in simple_type.findall(BASE_SCHEMA + 'union'):
            simple_dict['union'] = {'memberTypes': union.get('memberTypes')}

        # restrictions
        for restriction in simple_type.findall(BASE_SCHEMA + 'restriction'):
            restriction_type = restriction.get('base').replace('xs:', '')
            simple_dict['restriction'] = {'type': restriction_type}

            # enumerations
            for enumeration in restriction.findall(BASE_SCHEMA + 'enumeration'):
                values = simple_dict['restriction'].get('values', [])
                values.append(enumeration.get('value'))
                simple_dict['restriction']['values'] = values

            # minLength, maxLength, pattern
            for attribute_str in ['minLength', 'maxLength', 'pattern']:
                for attribute_obj in restriction.findall(BASE_SCHEMA + attribute_str):
                    simple_dict['restriction'][attribute_str] = attribute_obj.get('value')

        return simple_dict

    def _get_complex_data(self, complex_type):

        complex_dict = {}

        # choices
        for choice in complex_type.findall(BASE_SCHEMA + 'choice'):
            complex_dict['sequences'] = []

            # sequences?
            for count_seq, sequence in enumerate(choice.findall(BASE_SCHEMA + 'sequence')):
                complex_dict['sequences'].append({'elements': []})

                # sequences?
                for count_elem, element in enumerate(sequence):
                    complex_dict['sequences'][count_seq]['elements'].append({})

                    # attributes
                    for attribute_str in ['type', 'name', 'minOccurs', 'maxOccurs']:
                        if element.get(attribute_str) is not None:
                            complex_dict['sequences'][count_seq]['elements'][count_elem][attribute_str] = element.get(attribute_str).replace('xs:', '')

                    # simpleTypes
                    for simple_type in element.findall(BASE_SCHEMA + 'simpleType'):
                        simple_dict = self._get_simple_data(simple_type)
                        complex_dict['sequences'][count_seq]['elements'][count_elem].update(simple_dict)

        return complex_dict

