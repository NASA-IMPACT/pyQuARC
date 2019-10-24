1. Download xsd files from here: https://git.earthdata.nasa.gov/projects/EMFD/repos/echo-schemas/browse/schemas/10.0

2. Put them in data/xsd/

3. pip install -r requirements.txt

3. Go into code/lib/xml_to_json.py and edit the INPUT_XSD and OUTPUT_JSON constants

4. Run the code/lib/xml_to_json.py script, as needed.
The outputs are now stored in the output/ directory

5. Run code/lib/xsd_to_json_schema.py

6. The final json schema is stored in the output/ directory
