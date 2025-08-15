from pyQuARC.main import ARC
from pyQuARC.code.constants import ECHO10_C, CMR_URL

concept_ids = ["C1000000003-CDDIS"]
metadata_format = ECHO10_C

# Specify one or the other
rule_name = "data_format_presence_check"
field_name = "Collection/UseConstraints/FreeAndOpenData"


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
        'concept_id': 'C1000000003-CDDIS',
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

erroring_concept_ids = set()

for concept_id_results in results:
    concept_id = concept_id_results.get('concept_id')
    for field, errors in concept_id_results.get('errors').items():
        if field in field_name:
            erroring_concept_ids.add(concept_id)

        if rule_name in errors.keys():
            erroring_concept_ids.add(concept_id)

print("\n========================================================================================================")
print(f"The following concept ids failed the rule {rule_name} / field {field_name}: \n")
for concept_id in erroring_concept_ids:
    print("\t", concept_id, "\n")
