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
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'


class SchemaBuilder:

    def __init__(self, schema_url_input):
        '''
        Purpose: Initializes all class-wide variables, including importing the default schema and building a default tree.
        Arguments: Accepts a schema_url from the user. This should be a valid XSD file.
        '''

        self.schema_dict = dict()
        self.schema_tree = None
        self.schema_url = schema_url_input

        self.elem_functions = {'element': self._element,
                               'simpleType': self._simple}

        self.xsd_import(self.schema_url)

    def xsd_import(self, schema_url_input):
        '''
        Purpose: Grabs xsd from the internet and creates an eTree object. Will flag invalid XLM.
        Arguments: Accepts a valid schema_url.
        Network: External function, is called during init, but can also be modified by user after class creation.
        '''

        response = requests.get(schema_url_input, headers={'Connection': 'close'})
        schema_file = BytesIO(response.content)

        self.schema_tree = etree.parse(schema_file)  # could fail for a lot of reasons

        self.build_dict()

    def save_json(self, json_path='schema.json'):
        '''
        Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        with open(json_path, 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def build_dict(self):
        '''  loop of all the top level elements '''

        self.schema_dict = {}

        for main_Type in self.schema_tree.findall('*'):
            if self._extract_tag(main_Type) == 'simpleType':
                self.schema_dict[main_Type.get('name')] = self._simple(main_Type)
            elif self._extract_tag(main_Type) == 'complexType':
                self.schema_dict[main_Type.get('name')] = {}
                for element in main_Type:
                    self.schema_dict[main_Type.get('name')].update(self._recursion(element))

    def _recursion(self, element):

        element_tag = self._extract_tag(element)
        current_level_dict = dict()

        if element_tag in ['choice', 'sequence']:
            current_level_dict[element_tag] = []

            for sub_element in element:
                current_level_dict[element_tag].append(self._recursion(sub_element))

        elif element_tag in ['element', 'simpleType']:
            current_level_dict = self.elem_functions[element_tag](element)

        return current_level_dict

    def _element(self, element):
        element_attributes = self._extract_attributes(element)

        for simpleType in element:
            element_attributes.update(self._simple(simpleType))

        return element_attributes

    @staticmethod
    def _simple(simple_type):

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

    @staticmethod
    def _extract_attributes(element):
        return dict(zip(element.attrib, map(lambda x: x.replace('xs:', ''), element.attrib.values())))

    @staticmethod
    def _extract_tag(element):
        return element.tag.replace('{http://www.w3.org/2001/XMLSchema}', '')

    ############################################
    # printing functions for debug and testing #
    ############################################

    def print_xsd_structure(self):
        for count, element in enumerate(self.schema_tree.findall('*')):
            print(f'{count}: {self._extract_tag(element)}: {element.get("name")}')
            self._explore_tree(element)
            print()

    def _print_tag(self, depth, element):
        element_tag = self._extract_tag(element)
        spacer = '    '
        if element_tag not in ['annotation', 'documentation', 'p', 'appinfo']:
            pnt_str = f'    {spacer * depth}{element_tag}'
            if element.items():
                pnt_str += ' - ' + str(self._extract_attributes(element))
            print(pnt_str)

    def _explore_tree(self, element, depth=1):

        if element.getchildren():
            for sub_element in element:
                if type(sub_element) != etree._Comment:
                    self._print_tag(depth, sub_element)
                    self._explore_tree(sub_element, depth+1)
