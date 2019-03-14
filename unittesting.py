import unittest

from schema_builders import SchemaBuilder
import json

config = {'ECHO':
          {'url': 'https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/raw/schemas/10.0/Collection.xsd',
           'benchmark_path': 'test files/ECHO_benchmark.json',
           'test_path': 'test files/ECHO_test.json'
           },
          'DIF':
          {'url': 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd',
           'benchmark_path': 'test files/DIF-10_benchmark.json',
           'test_path': 'test files/DIF-10_test.json'
           }
          }


class TestDIF(unittest.TestCase):

    def setUp(self):
        with open(config['DIF']['benchmark_path']) as json_file:
            self.DIF_JSON = json.load(json_file)

        with open(config['ECHO']['benchmark_path']) as json_file:
            self.ECHO_JSON = json.load(json_file)

    def test_build_dict_DIF(self):
        '''
        Checks the output of the build_dict() function against a known correct JSON file
        '''

        # create class object and build dict
        test = SchemaBuilder(config['DIF']['url'])
        # compare the dicts
        self.assertEqual(test.schema_dict, self.DIF_JSON)

    def test_save_json_DIF(self):
        '''
        Checks the output of the save_json() function against a known correct JSON file.
        '''

        # generate the test JSON
        test = SchemaBuilder(config['DIF']['url'])

        test.save_json(config['DIF']['test_path'])

        with open(config['DIF']['test_path']) as json_file:
            test_json = json.load(json_file)

        # compare the JSON files
        self.assertEqual(test_json, self.DIF_JSON)

    def test_save_json_ECHO(self):
        '''
        Checks the output of the save_json() function against a known correct JSON file.
        '''

        # generate the test JSON
        test = SchemaBuilder(config['ECHO']['url'])

        test.save_json(config['ECHO']['test_path'])

        with open(config['ECHO']['test_path']) as json_file:
            test_json = json.load(json_file)

        # compare the JSON files
        self.assertEqual(test_json, self.ECHO_JSON)


if __name__ == '__main__':
    unittest.main(warnings='ignore', verbosity=2)
