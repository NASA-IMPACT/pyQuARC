'''
DIF Schema Builder
'''

# Import necessary libraries
import requests
from io import BytesIO
from lxml import etree

class DifSchemaBuilder:

    def dif_schema(variable_name):
        schema_output = []
        dif_schema_url = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
        response = requests.get(dif_schema_url)
        schema_xsd = BytesIO(response.content)
        xsd_file = etree.parse(schema_xsd)
        for value in xsd_file.findall('*'):
            if value.get('name') == variable_name:
                restrictions = value.findall('{http://www.w3.org/2001/XMLSchema}restriction')[0]
                for restriction in restrictions.findall('*'):
                    schema_output.append(restriction.get('value'))                    
        return schema_output
