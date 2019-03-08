'''
DIF Schema Builder
This class allows a user to input a schema URL, and then export it as a python dict or a JSON file.
The URL can be specified at init or after creation using the _xsd_import method.
A cleaned representation of the XSD file can be printed to the console using print_xsd_structure.
'''

# Import necessary libraries
import requests
import json
from io import BytesIO
from lxml import etree

# shared global values
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'


class SchemaBuilder:

    def __init__(self, xsd_file_url):
        self._build_functions = {'element': self._element,
                                 'simpleType': self._simple}
        self.schema_url = xsd_file_url
        self.schema_tree = self._xsd_import()
        self.schema_dict = self._build_dict()

    def _xsd_import(self):
        response = requests.get(self.schema_url, headers={'Connection': 'close'})
        schema_file = BytesIO(response.content)
        schema_tree = etree.parse(schema_file)  # could fail for a lot of reasons
        return schema_tree

    def save_json(self, json_path='schema.json'):
        with open(json_path, 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def _build_dict(self):
        schema_dict = {}

        for element in self.schema_tree.findall('*'):
            if self._extract_tag(element) in ['simpleType', 'complexType']:
                schema_dict.update(self._recursion(element))

        return schema_dict

    def _recursion(self, element):
        element_tag = self._extract_tag(element)
        element_name = element.get('name')
        current_level_dict = dict()

        if element_tag in ['choice', 'sequence']:
            current_level_dict[element_tag] = []

            for sub_element in element:
                current_level_dict[element_tag].append(self._recursion(sub_element))

        elif element_tag == 'element':
            current_level_dict = self._element(element)

        # child simpleType
        elif element_tag == 'simpleType' and not self._is_base(element):
            current_level_dict = self._simple(element)

        # parent simpleType
        elif element_tag == 'simpleType' and self._is_base(element):
            current_level_dict[element_name] = self._simple(element)

        elif element_tag == 'complexType':
            current_level_dict[element_name] = {}
            for sub_element in element:
                current_level_dict[element_name].update(self._recursion(sub_element))

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

    def _is_base(self, element):
        '''tests if element is a top level simple/complex/etc'''
        return self._extract_tag(element.getparent()) == 'schema'

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
        if element_tag not in ['annotation', 'documentation', 'p', 'appinfo', 'a']:
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
