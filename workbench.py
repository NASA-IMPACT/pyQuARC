'''
A file to test code.
'''

# Import necessary files
from dif_schema_builder import DifSchemaBuilder
import json

# Workspace
dif_dictionary = dict()
variable_list = ['GranuleSpatialRepresentationEnum', 'CoordinateSystemEnum',
'OrganizationTypeEnum' ,'PersonnelRoleEnum','DatasetLanguageEnum',
'SpatialCoverageTypeEnum', 'PhoneTypeEnum', 'DatasetProgressEnum',
'PersistentIdentifierEnum']

for variable in variable_list:
    dif_dictionary[variable] = DifSchemaBuilder.dif_schema(variable)

with open('dif_schema_output.json', 'w') as outfile:
    json.dump(dif_dictionary, outfile)
