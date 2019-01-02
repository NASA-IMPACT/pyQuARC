'''
DIF Schema Builder 
This class allows a user to input a schema URL, and then export it to the console, as a python dict, or a JSON file.
The URL can be specified at init or after creation using the xsd_import method.
'''

#double check the difference between using self.variable and other possibilities

# Import necessary libraries
import requests
import json
from io import BytesIO
from lxml import etree
import re

#shared global values
SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
BASE_SCHEMA = '{http://www.w3.org/2001/XMLSchema}'

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

        #could consolidate items on fewer lines, but this format is prefered for readability and later updates
        self._matcher= dict()
        self._matcher['restriction']='base'  
        self._matcher['enumeration']='value'
        self._matcher['choice']='choice'
        self._matcher['sequence']='sequence'
        self._matcher['element']=['type','name','minOccurs','maxOccurs']
        self._matcher['union']='memberTypes'
        self._matcher['simpleType']='name'
        self._matcher['complexType']='name'
        self._matcher['minLength']='value'
        self._matcher['maxLength']='value'
        self._matcher['pattern']='value'
        self._matcher['documentation']='documentation' #returns None
        self._matcher['annotation']='annotation' #returns None
        self._matcher['appinfo']='details' #returns None
        self._matcher['*']='*' #returns None
        self._matcher['/*']='*' #returns None
        self._matcher['/comment()']='comment'

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
        elem_key = str(re.sub(r'\[\d+\]','',path_dif))
        
        return elem_key


    def _get_elem_value(self,current,parent=''):  
        '''
        Purpose: Looks up the elem_key in the matcher dictionary to return the correct elem_value_query(s). Then queries 
        the etree model to return the corresponding elem_value(s).
        Arguments: Accepts the current and parent etree objects.
        Network: Internal function, is called by self._print_tree_line() and self._dict_entry()
        '''

        elem_key = self._get_elem_key(current,parent)
        elem_value_query = self._matcher[elem_key]
        
        if type(elem_value_query) is list:
            valuedict = dict()

            for i in elem_value_query:
                result = current.get(i)

                try: 
                    result = result.replace('xs:','')
                except:
                    None

                if not(result==None):
                    valuedict[i]=result
            
            elem_value = str(valuedict)
            return elem_value

        else:
            elem_value = str(current.get(elem_value_query)).replace('xs:','')
            return elem_value


    def _print_tree_line(self,spcr,current,parent=''):
        '''
        Purpose: Outputs a single line of the schema with correct lead spacing.
        Arguments: Accepts the spcr as an int, and the current and parent etree objects.
        Network: Internal function, is called by self.print_tree()
        '''
        
        elem_key = self._get_elem_key(current,parent)
        elem_value = self._get_elem_value(current,parent)

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

        try:
            elem_value_parent = self._get_elem_value(parent,grandparent)
        except:
            elem_value_parent = 'None'

        #main dictionary assignment section        
        if elem_key == 'simpleType': 
            if elem_value != 'None': #only occurs in that nested simple types
                self.schema_dict[elem_value]={}
            
        elif elem_key == 'annotation':
            None
            
        elif elem_key == 'documentation':
            None
            
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
            
            try:
                self.schema_dict[self._tracker]['restriction']['values'].append(elem_value)
            except:
                self.schema_dict[self._tracker]['restriction']['values']=[elem_value]
                
        elif elem_key == 'complexType': #this is not going to work for nested complexTypes, however none current exist
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
                try:
                    self.schema_dict[self._tracker]['sequences'][self._choice_count]['elements'].append(eval(elem_value))
                except:
                    self.schema_dict[self._tracker]['sequences'][self._choice_count]['elements']=[eval(elem_value)]
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
        self.schema_tree = etree.parse(schema_file)


    def build_dict(self):
        '''
        Purpose: Creates a python dictionary from the schema url given at class creation or the manual xsd_import.
        Arguments: Takes no input. If class was created with no arguments, it will be using the defualt url.
        Network: External function, called by user and self.save_json().
        '''
        
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
        Purpose: Rebuilds the dictionary (incase user has imported new url), and saves a json file.
        '''

        self.schema_dict = self.build_dict()

        with open('tree_dict.json', 'w') as outfile:
            json.dump(self.schema_dict, outfile)

