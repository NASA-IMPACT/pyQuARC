from dif_schema_builder_refactor import DifSchemaBuilder

# tests using default file
test = DifSchemaBuilder()


test.save_json()

# test using user enterd file
# test_2 = DifSchemaBuilder('https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/UmmCommon_1.3.xsd?at=refs%2Fheads%2Fmaster')
# test_2.print_tree()
# test_2.save_json()
# test_2.self_test()
