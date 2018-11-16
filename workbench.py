'''
A file to test code.
'''

# Import necessary files
from dif_schema_builder import DifSchemaBuilder
import json

# Workspace
dsb = DifSchemaBuilder()
dsb.build_schema()
dsb.save()
