from schema_builders import *


class Echo(SchemaTools):
    def __init__(self, schema_url_input=SCHEMA_URL_ECHO):

        SchemaTools.__init__(self, schema_url_input)

        self.elem_functions = {'sequence': self._sequence,
                               'element': self._element,
                               'simpleType': self._simpleType,
                               'choice': self._choice,
                               'complexType': self._complexType}

        self.build_dict()

    def build_dict(self):
        '''
        loop of all the top level elements
        '''

        self.schema_dict = {}

        for main_Type in self.schema_tree.findall('*'):
            if self._extract_tag(main_Type) in ['simpleType', 'complexType']:
                self.schema_dict[main_Type.get('name')] = {}
                for element in main_Type:
                    self.schema_dict[main_Type.get('name')].update(self._recursion(element))

    def _recursion(self, element):

        element_tag = self._extract_tag(element)
        current_level_dict = dict()

        if element_tag in ['choice', 'sequence']:
            current_level_dict[element_tag] = []

            for sub_element in element:
                # sub_element_tag = self._extract_tag(sub_element)
                current_level_dict[element_tag].append(self._recursion(sub_element))
                # if self._extract_tag(sub_element) in self.elem_functions.keys():  # if there is a function for the element tag
        elif element_tag in ['element', 'simpleType']:
            current_level_dict = self.elem_functions[element_tag](element)

        return current_level_dict


        #
        # children = element.getchildren()
        # current_level_dict = dict()
        # if choice or sequence: # figure out control logic
        #
        #     # the same as calling choice or sequence
        #     current_level_dict[element_type] = []#choice / sequence / simpletype etc
        #
        #     for sub_element in element:
        #         current_level_dict[element_type].append(self._recursion(sub_element))
        #         # if self._extract_tag(sub_element) in self.elem_functions.keys():  # if there is a function for the element tag
        #
        #         #     self._recursion(sub_element, depth+1)
        # else:
        #     # current_level_dict = handle current element
        #     # call simple type
        #     # call element
        # return current_level_dict

    ###################################################################################################################
    def _sequence(self, element):
        sequence_dict = {'sequence': []}
        return sequence_dict

    def _choice(self, element):
        choice_dict = {'choice': []}
        return choice_dict

    def _element(self, element):
        element_attributes = self._attribute_dict(element)
        return element_attributes

    def _simpleType(self, element):
        simple_dict = self._get_simple_data(element)
        return simple_dict

    def _complexType(self, element):
        return {'complex':'complexData'}