from dif_schema_builder import DifSchemaBuilder

# tests using default file
test = DifSchemaBuilder()
test.save_json()
test.self_test()

# # test using user entered file
test_2 = DifSchemaBuilder('https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster')
test_2.save_json()
test_2.self_test()
