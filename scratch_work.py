from dif_schema_builder import DifSchemaBuilder

dsb = DifSchemaBuilder('https://git.earthdata.nasa.gov/projects/EMFD/repos/dif-schemas/raw/10.x/dif_v10.3.xsd?at=refs%2Fheads%2Fmaster')
dsb.load_schema()
