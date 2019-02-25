import unittest

from schema_builders import *

SCHEMA_URL_DIF = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd'
SCHEMA_URL_ECHO = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/raw/schemas/10.0/Collection.xsd'

BENCHMARK_SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
BENCHMARK_JSON_PATH = 'test files/DIF-10_benchmark.json'
TEST_JSON_PATH = 'test files/DIF-10_test.json'


class TestDIF(unittest.TestCase):

    def setUp(self):
        with open(BENCHMARK_JSON_PATH) as json_file:
            self.BENCHMARK_JSON = json.load(json_file)

    def test_build_dict(self):
        '''
        Checks the output of the build_dict() function against a known correct JSON file
        '''

        # create class object and build dict
        test = SchemaBuilder(BENCHMARK_SCHEMA_URL)
        # compare the dicts
        self.assertEqual(test.schema_dict, self.BENCHMARK_JSON)

    def test_save_json(self):
        '''
        Checks the output of the save_json() function against a known correct JSON file.
        '''

        # generate the test JSON
        test = SchemaBuilder(BENCHMARK_SCHEMA_URL)

        test.save_json(TEST_JSON_PATH)

        with open(TEST_JSON_PATH) as json_file:
            test_json = json.load(json_file)

        # compare the JSON files
        self.assertEqual(test_json, self.BENCHMARK_JSON)


if __name__ == '__main__':
    unittest.main(warnings='ignore', verbosity=2)

