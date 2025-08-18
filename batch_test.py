from pyQuARC.main import ARC
from pyQuARC.code.constants import ECHO10_C, CMR_URL
import json

concept_ids = ["C1000000007-CDDIS","C1000000018-CDDIS", "C1000000012-CDDIS", 
               "C1000000014-CDDIS","C1000000015-CDDIS","C1000000016-CDDIS",
               "C1000000018-CDDIS","C1000000024-CDDIS","C1000000081-CDDIS",
               ]
               
metadata_format = ECHO10_C

# Specify one or the other
rule_name = "Horizontal_datum_check"
field_name = "SpatialRepresentationInfo/HorizontalCoordinateSystem/GeodeticModel/HorizontalDatumName"


arc = ARC(
    input_concept_ids=concept_ids,
    metadata_format=metadata_format,
    cmr_host=CMR_URL,
)
results = arc.validate()


'''
Example results:
[
    {
        'concept_id': 'C1000000010-CDDIS',
        'errors': {
            'OtherIdentifiers': {
                'schema': {
                    'message': ['Error: This element is not expected. Expected is ( InsertTime ).'],
                    'valid': False
                }
            },
            'Collection/UseConstraints/FreeAndOpenData': {
                'free_and_open_data_presence_check': {
                    'valid': False,
                    'value': [None],
                    'message': ['Warning: No FreeAndOpenData value was given.'],
                    'remediation': "Recommend providing a FreeAndOpenData value of 'true'."
                    }
            },
        }
        'pyquarc_errors': []
    }
]
'''

# Optionally: extract failing IDs for a specific rule/field

erroring_concept_ids = set()

print("\n====================== SUMMARY OF PASSED ID ======================\n")
for concept_id_results in results:
    concept_id = concept_id_results.get("concept_id")
    failed = False  # Track if this concept_id failed

    for field, errors in concept_id_results.get("errors").items():
        if field == field_name and rule_name in errors:
            rule_result = errors[rule_name]
            if not rule_result.get("valid", True):  # explicitly check validity
                failed = True
                print(f"❌ {concept_id} FAILED rule '{rule_name}' on field '{field_name}'")
            else:
                print(f"✅ {concept_id} PASSED rule '{rule_name}' on field '{field_name}'")

    if not failed:
        # If field/rule wasn't present at all → treat as passed
        print(f"✅ {concept_id} PASSED rule '{rule_name}' on field '{field_name}'")
 
