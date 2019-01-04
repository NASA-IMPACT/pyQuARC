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

#shared global values
SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'
BENCHMARK_DICT = {"GranuleSpatialRepresentationEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC", "ORBIT", "NO_SPATIAL"]}}, "CoordinateSystemEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC"]}}, "OrganizationPersonnelRoleEnum": {"restriction": {"type": "string", "values": ["DATA CENTER CONTACT"]}}, "DistributionSizeUnitTypeEnum": {"restriction": {"type": "string", "values": ["KB", "MB", "GB", "TB", "PB"]}}, "DistributionFormatTypeEnum": {"restriction": {"type": "string", "values": ["Native", "Supported"]}}, "OrganizationTypeEnum": {"restriction": {"type": "string", "values": ["DISTRIBUTOR", "ARCHIVER", "ORIGINATOR", "PROCESSOR"]}}, "PersonnelRoleEnum": {"restriction": {"type": "string", "values": ["INVESTIGATOR", "INVESTIGATOR, TECHNICAL CONTACT", "METADATA AUTHOR", "METADATA AUTHOR, TECHNICAL CONTACT", "TECHNICAL CONTACT"]}}, "PlatformTypeEnum": {"restriction": {"type": "string", "values": ["Not provided", "Not applicable", "Aircraft", "Balloons/Rockets", "Earth Observation Satellites", "In Situ Land-based Platforms", "In Situ Ocean-based Platforms", "Interplanetary Spacecraft", "Maps/Charts/Photographs", "Models/Analyses", "Navigation Platforms", "Solar/Space Observation Satellites", "Space Stations/Manned Spacecraft"]}}, "DatasetLanguageEnum": {"restriction": {"type": "string", "values": ["English", "Afrikaans", "Arabic", "Bosnian", "Bulgarian", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "Estonian", "Finnish", "French", "German", "Hebrew", "Hungarian", "Indonesian", "Italian", "Japanese", "Korean", "Latvian", "Lithuanian", "Norwegian", "Polish", "Portuguese", "Romanian", "Russian", "Slovak", "Spanish", "Ukrainian", "Vietnamese"]}}, "CollectionDataTypeEnum": {"restriction": {"type": "string", "values": ["SCIENCE_QUALITY", "NEAR_REAL_TIME", "ON_DEMAND", "OTHER"]}}, "ProductFlagEnum": {"restriction": {"type": "string", "values": ["Not provided", "DATA_PRODUCT_FILE", "INSTRUMENT_ANCILLARY_FILE", "SYSTEM/SPACECRAFT_FILE", "EXTERNAL_DATA"]}}, "DurationUnitEnum": {"restriction": {"type": "string", "values": ["DAY", "MONTH", "YEAR"]}}, "SpatialCoverageTypeEnum": {"restriction": {"type": "string", "values": ["Horizontal", "HorizontalVertical", "Orbit", "Vertical", "Horizon&Vert"]}}, "PhoneTypeEnum": {"restriction": {"type": "string", "values": ["Direct Line", "Primary", "Telephone", "Fax", "Mobile", "Modem", "TDD/TTY Phone", "U.S. toll free", "Other"]}}, "MetadataAssociationTypeEnum": {"restriction": {"type": "string", "values": ["Parent", "Child", "Related", "Dependent", "Input", "Science Associated"]}}, "PrivateEnum": {"restriction": {"type": "string", "values": ["True", "False"]}}, "MetadataVersionEnum": {"restriction": {"type": "string", "values": ["VERSION 9.8.1", "VERSION 9.8.2", "VERSION 9.8.2.2", "VERSION 9.8.3", "VERSION 9.8.4", "VERSION 9.9.3", "VERSION 10.2"]}}, "ProductLevelIdEnum": {"restriction": {"type": "string", "values": ["Not provided", "0", "1", "1A", "1B", "1T", "2", "2G", "2P", "3", "4", "NA"]}}, "DatasetProgressEnum": {"restriction": {"type": "string", "values": ["PLANNED", "IN WORK", "COMPLETE", "NOT APPLICABLE", "NOT PROVIDED"]}}, "DisplayableTextEnum": {"restriction": {"type": "string", "values": ["text/plain", "text/markdown"]}}, "DisplayableTextTypeBaseType": {"restriction": {"type": "string"}}, "PersistentIdentifierType": {"sequences": [{"elements": [{"type": "PersistentIdentifierEnum", "name": "Type"}, {"type": "string", "name": "Identifier"}, {"name": "Authority", "minOccurs": "0", "restriction": {"type": "string", "maxLength": "80", "minLength": "1"}}]}, {"elements": [{"type": "MissingReasonEnum", "name": "MissingReason"}, {"type": "string", "name": "Explanation", "minOccurs": "0"}]}]}, "PersistentIdentifierEnum": {"restriction": {"type": "string", "values": ["DOI", "ARK"]}}, "MissingReasonEnum": {"restriction": {"type": "string", "values": ["Not applicable"]}}, "DateOrEnumType": {}, "TimeOrEnumType": {}, "DateOrTimeOrEnumType": {}, "DateEnum": {"restriction": {"type": "string", "values": ["Not provided", "unknown", "present", "unbounded", "future"]}}, "UuidType": {"restriction": {"type": "string"}}}

#could consolidate items on fewer lines, but this format is prefered for readability and later updates
MATCHER= dict()
MATCHER['restriction']='base'  
MATCHER['enumeration']='value'
MATCHER['choice']='choice'
MATCHER['sequence']='sequence'
MATCHER['element']=['type','name','minOccurs','maxOccurs']
MATCHER['union']='memberTypes'
MATCHER['simpleType']='name'
MATCHER['complexType']='name'
MATCHER['minLength']='value'
MATCHER['maxLength']='value'
MATCHER['pattern']='value'
MATCHER['documentation']='documentation' #returns None
MATCHER['annotation']='annotation' #returns None
MATCHER['appinfo']='details' #returns None
MATCHER['*']='*' #returns None
MATCHER['/*']='*' #returns None
MATCHER['/comment()']='comment'

class DifSchemaBuilder:

    def __init__(self, schema_url_input=SCHEMA_URL):
        '''
        Purpose: Initializes all class-wide variables, including importing the default schema and building a default tree.
        Arguments: Accepts a schema_url from the user. This should be a valid XSD file, as there is no error checking.
        Network: Internal function, is called on initialization.
        '''

        self.schema_dict = dict()
        self.schema_tree =None

        self._tracker = None
        self._choice_count = None
        self._schema_dict_parent = dict()

        self.test_result = True

        self.xsd_import(schema_url_input)
        self.build_dict() #building the dictionary upon init allows the user to save directly


    def _get_elem_key(self,current,parent=''):
        '''
        Purpose: Finds the unique path of the current etree object and removes syntax to return the relevant keyword for use in the dictionary.
        Arguments: Accepts the current and parent etree objects.
        Network: Internal function, is called by self._get_elem_value()
        '''

        path_current = self.schema_tree.getpath(current)
        replace_string = '/xs:schema/xs:'
        
        if parent != '':
            path_parent = self.schema_tree.getpath(parent)
            replace_string = path_parent
        
        path_dif = path_current.replace(replace_string, '').replace('/xs:','')
        elem_key = re.sub(r'\[\d+\]','',path_dif)

        return elem_key


    def _get_elem_value(self,current,parent=''):  
        '''
        Purpose: Looks up the elem_key in the matcher dictionary to return the correct elem_value_query(s). Then queries 
        the etree model to return the corresponding elem_value(s).
        Arguments: Accepts the current and parent etree objects.
        Network: Internal function, is called by self._print_tree_line() and self._dict_entry()
        '''

        elem_key = self._get_elem_key(current,parent)
        elem_value_query = MATCHER[elem_key]
        
        if type(elem_value_query) is list:
            elem_values_dict = dict()

            for i in elem_value_query:
                result = current.get(i)

                if not(result==None):
                    result = result.replace('xs:','')
                    elem_values_dict[i]=result                   
            
            elem_value = elem_values_dict
            return elem_value

        else:
            elem_value = current.get(elem_value_query)
            
            if elem_value == None:
                elem_value = 'None'
            else:
                elem_value = current.get(elem_value_query).replace('xs:','')

            return elem_value


    def _print_tree_line(self,spcr,current,parent=''):
        '''
        Purpose: Outputs a single line of the schema with correct lead spacing.
        Arguments: Accepts the spcr as an int, and the current and parent etree objects.
        Network: Internal function, is called by self.print_tree()
        '''
        
        elem_key = self._get_elem_key(current,parent)
        elem_value = str(self._get_elem_value(current,parent)) #necessary to convert occasional dict to str

        return print('   '*spcr + elem_key + ': ' + elem_value)

   
    def _dict_entry(self,current,parent,grandparent):
        '''
        Purpose: Examines current etree node and its parents to determine what, if anything, to add to the python dictionary.
        Arguments: Accepts current, parent, and grandparent etree objects. When no grandparent exists, give as empty string.
        Network: Internal function, is called by self.build_dict().
        '''

        #main variable assignment
        elem_key = self._get_elem_key(current,parent)
        elem_value = self._get_elem_value(current,parent)

        if parent == '':
            elem_value_parent = 'None'
        else:
            elem_value_parent = self._get_elem_value(parent,grandparent)

        #main dictionary assignment section        
        if elem_key == 'simpleType': 
            if elem_value != 'None': #only occurs in that nested simple types
                self.schema_dict[elem_value]={}
            
        elif elem_key == 'restriction':
            if elem_value_parent=='None': #this only happens in the nested simple type
                self._schema_dict_parent['restriction']={'type':elem_value}
            else:
                self.schema_dict[self._get_elem_value(parent,grandparent)]={'restriction':{'type':elem_value}}
                self._tracker = elem_value_parent

        elif elem_key == 'maxLength':
            self._schema_dict_parent['restriction'][elem_key]=elem_value
            
        elif elem_key == 'minLength':
            self._schema_dict_parent['restriction'][elem_key]=elem_value
        
        elif elem_key == 'enumeration':
            values = self.schema_dict[self._tracker]['restriction'].get('values', [])
            values.append(elem_value)
            self.schema_dict[self._tracker]['restriction']['values'] = values            
                
        elif elem_key == 'complexType': #this is not going to work for nested complexTypes, however none currently exist in the schema
            self.schema_dict[elem_value]={}
        
        elif elem_key == 'choice':
            
            if self._get_elem_value(parent,grandparent)=='None':
                None #keep tracker as it was
            else:
                self._tracker = elem_value_parent
                
            self.schema_dict[self._tracker]['sequences']=[] 
            self._choice_count = -1
            
        elif elem_key == 'sequence':
            try:
                self.schema_dict[self._tracker]['sequences'].append({'elements':[]})
            except:
                print(f'sequence error, tracker= {self._tracker}, choice count = {self._choice_count}')
            self._choice_count += 1
            
        elif elem_key == 'element':
            try:
                elements = self.schema_dict[self._tracker]['sequences'][self._choice_count].get('elements',[])
                elements.append(elem_value)                
                self.schema_dict[self._tracker]['sequences'][self._choice_count]['elements']=elements
            except:
                print(f'element error, tracker={self._tracker}, choice_count={self._choice_count}')
                
            #stores current location in dictionary for use when adding child simple type
            self._schema_dict_parent = self.schema_dict[self._tracker]['sequences'][self._choice_count]['elements'] #returns list
            self._schema_dict_parent = self._schema_dict_parent[len(self._schema_dict_parent)-1] #gives only the most recent item in list
            
        elif elem_key == 'patern':
            None


    def xsd_import(self,schema_url_input):
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


    def build_dict(self):
        '''
        Purpose: Creates a python dictionary from the schema url given at class creation or the manual xsd_import.
        Arguments: Takes no input. If class was created with no arguments, it will be using the defualt url.
        Network: External function, called by user and self.save_json().
        '''
        
        if self.test_result == False:
            return print('Dictionary build aborted')

        for i in self.schema_tree.findall('*'):
            self._dict_entry(i,'','') 

            for ii in i:
                self._dict_entry(ii,i,'')
                
                for iii in ii:
                    self._dict_entry(iii,ii,i)
                    
                    for iv in iii:
                        self._dict_entry(iv,iii,ii)

                        for v in iv:
                            self._dict_entry(v,iv,iii)
                            
                            for vi in v:
                                self._dict_entry(vi,v,iv)
                                
                                for vii in vi:
                                    self._dict_entry(vii,vi,v)

        return self.schema_dict


    def print_tree(self):
        '''
        Purpose: Prints a visual form of the xsd to the console for easy inspection.
        '''
        
        if self.test_result == False:
            return print('Console print aborted')

        #add a bit to fail if tree isn't built yet
        for i in self.schema_tree.findall('*'):
            self._print_tree_line(0,i,'')

            for ii in i:
                self._print_tree_line(1,ii,i)

                for iii in ii:
                    self._print_tree_line(2,iii,ii)

                    for iv in iii:
                        self._print_tree_line(3,iv,iii)

                        for v in iv:
                            self._print_tree_line(4,v,iv)

                            for vi in v:
                                self._print_tree_line(5,vi,v)

                                for vii in vi:
                                    self._print_tree_line(6,vii,vi)                         

                                    for viii in vii:
                                        self._print_tree_line(7,viii,vii)  


    def save_json(self):
        '''
        Purpose: Rebuilds the dictionary (in case user has imported new url), and saves a json file.
        '''

        if self.test_result == False:
            return print('Save JSON aborted')

        self.schema_dict = self.build_dict()

        with open('tree_dict.json', 'w') as outfile:
            json.dump(self.schema_dict, outfile)


    def self_test(self):
        '''
        Purpose: Compares self.build_dict() output against the benchmark dict stored in memory. Allows for easy testing of new code changes.
        '''

        print()

        #query the known schema to compare against the known python dict
        self.xsd_import('https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster')

        if self.build_dict() == BENCHMARK_DICT and self.test_result:
            print('Self test passed')
        else:
            print('Self test failed')
