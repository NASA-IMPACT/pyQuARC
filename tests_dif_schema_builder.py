from dif_schema_builder import DifSchemaBuilder
import json

BENCHMARK_SCHEMA_URL = 'https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster'
BENCHMARK_DICT = {"GranuleSpatialRepresentationEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC", "ORBIT", "NO_SPATIAL"]}}, "CoordinateSystemEnum": {"restriction": {"type": "string", "values": ["CARTESIAN", "GEODETIC"]}}, "OrganizationPersonnelRoleEnum": {"restriction": {"type": "string", "values": ["DATA CENTER CONTACT"]}}, "DistributionSizeUnitTypeEnum": {"restriction": {"type": "string", "values": ["KB", "MB", "GB", "TB", "PB"]}}, "DistributionFormatTypeEnum": {"restriction": {"type": "string", "values": ["Native", "Supported"]}}, "OrganizationTypeEnum": {"restriction": {"type": "string", "values": ["DISTRIBUTOR", "ARCHIVER", "ORIGINATOR", "PROCESSOR"]}}, "PersonnelRoleEnum": {"restriction": {"type": "string", "values": ["INVESTIGATOR", "INVESTIGATOR, TECHNICAL CONTACT", "METADATA AUTHOR", "METADATA AUTHOR, TECHNICAL CONTACT", "TECHNICAL CONTACT"]}}, "PlatformTypeEnum": {"restriction": {"type": "string", "values": ["Not provided", "Not applicable", "Aircraft", "Balloons/Rockets", "Earth Observation Satellites", "In Situ Land-based Platforms", "In Situ Ocean-based Platforms", "Interplanetary Spacecraft", "Maps/Charts/Photographs", "Models/Analyses", "Navigation Platforms", "Solar/Space Observation Satellites", "Space Stations/Manned Spacecraft"]}}, "DatasetLanguageEnum": {"restriction": {"type": "string", "values": ["English", "Afrikaans", "Arabic", "Bosnian", "Bulgarian", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "Estonian", "Finnish", "French", "German", "Hebrew", "Hungarian", "Indonesian", "Italian", "Japanese", "Korean", "Latvian", "Lithuanian", "Norwegian", "Polish", "Portuguese", "Romanian", "Russian", "Slovak", "Spanish", "Ukrainian", "Vietnamese"]}}, "CollectionDataTypeEnum": {"restriction": {"type": "string", "values": ["SCIENCE_QUALITY", "NEAR_REAL_TIME", "ON_DEMAND", "OTHER"]}}, "ProductFlagEnum": {"restriction": {"type": "string", "values": ["Not provided", "DATA_PRODUCT_FILE", "INSTRUMENT_ANCILLARY_FILE", "SYSTEM/SPACECRAFT_FILE", "EXTERNAL_DATA"]}}, "DurationUnitEnum": {"restriction": {"type": "string", "values": ["DAY", "MONTH", "YEAR"]}}, "SpatialCoverageTypeEnum": {"restriction": {"type": "string", "values": [
    "Horizontal", "HorizontalVertical", "Orbit", "Vertical", "Horizon&Vert"]}}, "PhoneTypeEnum": {"restriction": {"type": "string", "values": ["Direct Line", "Primary", "Telephone", "Fax", "Mobile", "Modem", "TDD/TTY Phone", "U.S. toll free", "Other"]}}, "MetadataAssociationTypeEnum": {"restriction": {"type": "string", "values": ["Parent", "Child", "Related", "Dependent", "Input", "Science Associated"]}}, "PrivateEnum": {"restriction": {"type": "string", "values": ["True", "False"]}}, "MetadataVersionEnum": {"restriction": {"type": "string", "values": ["VERSION 9.8.1", "VERSION 9.8.2", "VERSION 9.8.2.2", "VERSION 9.8.3", "VERSION 9.8.4", "VERSION 9.9.3", "VERSION 10.2"]}}, "ProductLevelIdEnum": {"restriction": {"type": "string", "values": ["Not provided", "0", "1", "1A", "1B", "1T", "2", "2G", "2P", "3", "4", "NA"]}}, "DatasetProgressEnum": {"restriction": {"type": "string", "values": ["PLANNED", "IN WORK", "COMPLETE", "NOT APPLICABLE", "NOT PROVIDED"]}}, "DisplayableTextEnum": {"restriction": {"type": "string", "values": ["text/plain", "text/markdown"]}}, "DisplayableTextTypeBaseType": {"restriction": {"type": "string"}}, "PersistentIdentifierEnum": {"restriction": {"type": "string", "values": ["DOI", "ARK"]}}, "MissingReasonEnum": {"restriction": {"type": "string", "values": ["Not applicable"]}}, "DateOrEnumType": {"union": {"memberTypes": "xs:date DateEnum"}}, "TimeOrEnumType": {"union": {"memberTypes": "xs:dateTime DateEnum"}}, "DateOrTimeOrEnumType": {"union": {"memberTypes": "xs:date xs:dateTime DateEnum"}}, "DateEnum": {"restriction": {"type": "string", "values": ["Not provided", "unknown", "present", "unbounded", "future"]}}, "UuidType": {"restriction": {"type": "string", "patern": "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89abAB][0-9a-f]{3}-[0-9a-f]{12}"}}, "PersistentIdentifierType": {"sequences": [{"elements": [{"type": "PersistentIdentifierEnum", "name": "Type"}, {"type": "string", "name": "Identifier"}, {"name": "Authority", "minOccurs": "0", "restriction": {"type": "string", "maxLength": "80", "minLength": "1"}}]}, {"elements": [{"type": "MissingReasonEnum", "name": "MissingReason"}, {"type": "string", "name": "Explanation", "minOccurs": "0"}]}]}}
BENCHMARK_JSON_PATH = 'tree_dict_benchmark.json'
TEST_JSON_PATH = 'tree_dict_test.json'


def test_build_dict():
    '''
    Checks the output of the build_dict() function against a known correct dictionary
    '''
    test = DifSchemaBuilder(BENCHMARK_SCHEMA_URL)

    if test.build_dict() == BENCHMARK_DICT:
        return 'Passed: build_dict()'
    else:
        return 'Failed: build_dict()'


def test_save_json():
    '''
    Checks the output of the save_json() function against a known correct JSON file.
    '''

    # generate the test JSON
    test = DifSchemaBuilder(BENCHMARK_SCHEMA_URL)
    test.save_json(TEST_JSON_PATH)

    # open the two JSON files
    with open(BENCHMARK_JSON_PATH) as json_file:
        benchmark_json = json.load(json_file)

    with open(TEST_JSON_PATH) as json_file:
        test_json = json.load(json_file)

    # compare the JSON files
    if test_json == benchmark_json:
        return 'Passed: save_json()'
    else:
        return 'Failed: save_json()'


def test_bad_schema():
    '''
    There is some error handling built into the class that will respond to a failed schema import.
    This function should check whether that error handling is working correctly.
    '''
    return 'no schema test yet'

    if False:
        return 'Passed: schema test'
    else:
        return 'Failed: schema test'
