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
SCHEMA_URL_DIF = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd'
SCHEMA_URL_ECHO = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/raw/schemas/10.0/Collection.xsd'
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'


class SchemaTools:

    def __init__(self, schema_url_input):
        '''
        Purpose: Initializes all class-wide variables, including importing the default schema and building a default tree.
        Arguments: Accepts a schema_url from the user. This should be a valid XSD file.
        '''

        self.schema_dict = dict()
        self.schema_tree = None
        self.schema_url = schema_url_input

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

    def save_json(self, json_path='schema.json'):
        '''
        Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        self.build_dict()

        with open(json_path, 'w') as outfile:
            json.dump(self.schema_dict, outfile)

    def _attribute_dict(self, element):
        return dict(zip(element.attrib, map(lambda x: x.replace('xs:', ''), element.attrib.values())))

    def print_xsd_structure(self):
        for count, element in enumerate(self.schema_tree.findall('*')):
            print(f'{count}: {self._extract_tag(element)}: {element.get("name")}')
            # self._print_tag(0, element)
            self._explore_tree(element, 1)
            print()

    def _extract_tag(self, element):
        return element.tag.replace('{http://www.w3.org/2001/XMLSchema}', '')

    def _extract_parent_tag(self, element):
        return element.getparent().tag.replace('{http://www.w3.org/2001/XMLSchema}', '')

    def _print_tag(self, depth, element):
        element_tag = self._extract_tag(element)
        spacer = '    '
        if element_tag not in ['annotation', 'documentation', 'p', 'appinfo']:
            pnt_str = f'    {spacer * depth}{element_tag}'
            if element.items():
                # pnt_str += ' - ' + str(element.items())
                pnt_str += ' - ' + str(element.attrib)
            print(pnt_str)

    def _explore_tree(self, element, depth=-1):
        '''Recusively explore the eTree'''

        if depth < 10:
            for sub_element in element:
                if type(sub_element) != etree._Comment:
                    self._print_tag(depth, sub_element)
                    self._explore_tree(sub_element, depth+1)



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


class DifSchema(SchemaTools):
    def __init__(self, schema_url_input=SCHEMA_URL_DIF):
        '''
        init
        '''

        SchemaTools.__init__(self, schema_url_input)
        self.build_dict()

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
    #
    # def _get_simple_data(self, simple_type):
    #
    #     simple_dict = {}
    #
    #     # unions
    #     for union in simple_type.findall(BASE_SCHEMA + 'union'):
    #         simple_dict['union'] = {'memberTypes': union.get('memberTypes')}
    #
    #     # restrictions
    #     for restriction in simple_type.findall(BASE_SCHEMA + 'restriction'):
    #         restriction_type = restriction.get('base').replace('xs:', '')
    #         simple_dict['restriction'] = {'type': restriction_type}
    #
    #         # enumerations
    #         for enumeration in restriction.findall(BASE_SCHEMA + 'enumeration'):
    #             values = simple_dict['restriction'].get('values', [])
    #             values.append(enumeration.get('value'))
    #             simple_dict['restriction']['values'] = values
    #
    #         # minLength, maxLength, pattern
    #         for attribute_str in ['minLength', 'maxLength', 'pattern']:
    #             for attribute_obj in restriction.findall(BASE_SCHEMA + attribute_str):
    #                 simple_dict['restriction'][attribute_str] = attribute_obj.get('value')
    #
    #     return simple_dict

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
                    complex_dict['sequences'][count_seq]['elements'][count_elem].update(self._attribute_dict(element))

                    # simpleTypes
                    for simple_type in element.findall(BASE_SCHEMA + 'simpleType'):
                        simple_dict = self._get_simple_data(simple_type)
                        complex_dict['sequences'][count_seq]['elements'][count_elem].update(simple_dict)

        return complex_dict


class EchoSchema(SchemaTools):
    def __init__(self, schema_url_input=SCHEMA_URL_ECHO):
        '''init'''
        SchemaTools.__init__(self, schema_url_input)

        self.elem_functions = {'elementTag': 'matchingFunction',
                               'sequence': self._sequence,
                               'element': self._element,
                               'simpleType': self._simpleType}

        self._temp = dict()
        self._temp_sub = dict()
        self.build_dict()

    def build_dict(self):

        self.schema_dict = {}

        for element in self.schema_tree.findall('*'):
            if element.tag == (BASE_SCHEMA + 'simpleType') or element.tag == (BASE_SCHEMA + 'complexType'):

                element_name = element.get('name')

                self._temp = {}
                self.schema_dict[element_name] = self._explore_tree_sub(element, 1)

        # print(self.schema_dict)

    def _explore_tree_sub(self, element, depth=-1):
        '''
        each explore tree only looks at the children of one top level element
        such as simpleType of complexType
        cleans the temp dict and builds a new one. The sub-functions build on it, they do not return it between themselves
        '''

        if depth < 10:
            for sub_element in element:
                if self._extract_tag(sub_element) in self.elem_functions.keys():  # if there is a function for the element tag
                    self._build_temp(sub_element)
                    self._explore_tree_sub(sub_element, depth+1)

        return self._temp

    def _build_temp(self, element):
        '''
        runs correct function for the current element
        '''

        self.elem_functions[self._extract_tag(element)](element)

    def _sequence(self, element):
        if self._is_base(element):
            self._temp = {'sequence': []}
            self._temp_sub = self._temp['sequence']

    def _element(self, element):
        '''are elements always inside of sequences?'''

        # parent is [sequence]
        if self._extract_tag(element.getparent()) == 'sequence':  # and self._is_base(element.getparent()):
            # self._temp_sub.append(element.attrib)  #
            self._temp['sequence'].append(element.attrib)

            # if this element has a valid child, then it will prepare the temp dict for that child to store into
            child_tags = list(map(self._extract_tag, element.getchildren()))
            for child_tag in child_tags:
                if child_tag in self.elem_functions.keys():
                    pass
                    # self._temp_sub = self._temp_sub[-1]

    def _simpleType(self, element):
        # How do I know where to put this data in the self._temp???
        # The parent must be storing it's data somewhere??
        pass
        # if element.parent
        # print(self._get_simple_data(element))

    def _is_base(self, element):
        '''tests if element is direct child of a simple/complex/etc'''

        return self._extract_tag(element.getparent().getparent())=='schema'