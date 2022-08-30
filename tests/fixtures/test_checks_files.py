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
sys.path.append(f'{os.getcwd()}')
from pyQuARC.code.checker import Checker
code_checker = Checker()
# Opening JSON files
f = open('tests/fixtures/checks_dif10_master_test_file.json')
f2 = open('tests/fixtures/checks_echo-c_master_test_file.json')
f3 = open('tests/fixtures/checks_echo-g_master_test_file.json')
f4 = open('tests/fixtures/checks_umm-c_master_test_file.json')
f5 = open('tests/fixtures/checks_umm-g_master_test_file.json')
f6 = open('pyQuARC/schemas/rule_mapping.json')
f7 = open('pyQuARC/schemas/checks.json')
check = ''  # 'check'
check_id = ''
relation = ''
# returning JSON objects as dictionaries
dif10_checks = json.load(f)
echo_c_checks = json.load(f2)
echo_g_checks = json.load(f3)
umm_c_checks = json.load(f4)
umm_g_checks = json.load(f5)
rule_mapping = json.load(f6)
checks = json.load(f7)
# iterating through the json
for i in dif10_checks:  # test --> change to variable / iteration
    if i in rule_mapping:
        try:
            check_id = rule_mapping[i]['check_id']
            if check_id in checks:
                check = checks[check_id]
                var = code_checker.map_to_function(check['data_type'],check['check_function'])
                if (isinstance(dif10_checks[i]['valid'][0], str)):
                    relation = rule_mapping[i]["fields_to_apply"]["dif10"][0]["relation"]
                    print(var(dif10_checks[i]['valid'][0],dif10_checks[i]['valid'][1], relation))
                else:
                    print('skip')
                # type(dif10_checks[i]['invalid'][0] / [1] / ... --> string or list
                # assert var  #test
        except KeyError:
            print('skip') #f"'check_id' Key does not exist for {rule_mapping[i]['rule_name']} rule in rule_mapping.json --> or other error tbd")
# close files
f.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()