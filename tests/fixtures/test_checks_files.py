# for each check in test_json
#     find the same check in checks_json, assign it to `check`
#     based on the `data_type` and `check_function` in `check`, find the function that it maps to (for example: StringValidator.organization_short_name_gcmd_check) [code already exists in code/checker.py]
#     call the function with the 'valid' and 'invalid' arguments from test_json
#     assert that the function returns the correct result
#     example:
#       assert function(*test_json['valid']).get('validity') == True
#       assert function(*test_json['invalid']).get('validity') == False
import json
import sys
import os
sys.path.append(os.getcwd())
from pyQuARC.code.constants import SCHEMAS
from pyQuARC.code.checker import Checker
# Opening JSON files
f = open('tests/fixtures/checks_dif10_master_test_file.json')
f2 = open('tests/fixtures/checks_echo-c_master_test_file.json')
f3 = open('tests/fixtures/checks_echo-g_master_test_file.json')
f4 = open('tests/fixtures/checks_umm-c_master_test_file.json')
f5 = open('tests/fixtures/checks_umm-g_master_test_file.json')
f6 = open('pyQuARC/schemas/rule_mapping.json')
f7 = open('pyQuARC/schemas/checks.json')
# returning JSON objects as dictionaries
dif10_checks = json.load(f)
echo_c_checks = json.load(f2)
echo_g_checks = json.load(f3)
umm_c_checks = json.load(f4)
umm_g_checks = json.load(f5)
rule_mapping = json.load(f6)
checks = json.load(f7)
check = ''  # 'check'
code_checker = Checker()
format_dict = {'dif10': dif10_checks, 'echo-c': echo_c_checks, 'echo-g': echo_c_checks, 'umm-c': umm_g_checks, 'umm-g': umm_g_checks}
format_in = ''
rule = ''
check_id = ''
data_type = ''
check_function = ''
relation = ''
while format_in not in format_dict.keys():
    format_in = input("Enter the metadata format. Choices are: echo-c (echo10 collection), echo-g (echo10 granule), dif10 (dif10 collection), umm-c (umm-json collection), umm-g (umm-json granules)\n")
format_choice = format_dict[format_in]
# iterating through the json
for i in format_choice:
    if i in rule_mapping:
        try:
            rule = rule_mapping[i]['rule_name']
            print(f'rule_name: {rule}')
        except KeyError:
            print(f"'rule_name' key does not exist for {rule_mapping[i]['rule_name']} rule in rule_mapping.json")                
        try:
            check_id = rule_mapping[i]['check_id']
            print(f'check_id: {check_id}')
        except KeyError:
            print(f"'check_id' key does not exist for {rule_mapping[i]['rule_name']} rule in rule_mapping.json")
        if check_id in checks:
            data_type = checks[check_id]['data_type'] # try, except
            check_function = checks[check_id]['check_function'] # try, except
            val_function = code_checker.map_to_function(data_type, check_function) # try, except
            print(f'Validator function: {data_type.title()}Validator.{check_function}')
            if (isinstance(format_choice[i]['valid'][0], str)):
                relation = rule_mapping[i]["fields_to_apply"]["dif10"][0]["relation"]
                print(val_function(format_choice[i]['valid'][0],format_choice[i]['valid'][1], relation))
            else:
                print('skip (2)')
            # type(format_choice[i]['invalid'][0] / [1] / ... --> string or list
            # assert val_function  #test
# close files
f.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()