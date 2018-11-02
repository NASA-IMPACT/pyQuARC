'''
DIF Schema Builder
'''

# Import necessary libraries
import requests
import lxml.etree

class DifSchemaBuilder:

    def dif_schema(self, url):
        self.url = url

    def load_schema(self):
        self.schema = requests.get(url)
        return self.schema
