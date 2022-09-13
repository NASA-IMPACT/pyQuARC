# psuedocode -
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
# note: adding relation / data values to test files in valid / invalid lists
code_checker = Checker()
format_dict = {'dif10': dif10_checks, 'echo-c': echo_c_checks, 'echo-g': echo_c_checks, 'umm-c': umm_g_checks, 'umm-g': umm_g_checks}
format_in = ''
rule = ''
check_id = ''
data_type = ''
check_function = ''
# functions to call and return what is returned from validator function when given valid or invalid values as arguments
def DatetimeValidator_compare_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2])
    except:
        return 'error'  # can expand
def DatetimeValidator_date_or_datetime_format_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i +1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def UrlValidator_health_and_status_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i +1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'

def DOI_update_check(val_function, value):
    try:
        if (isinstance(value[0],list)):
                i = 0
                return_list = []
                for x in value:
                    return_list.append(val_function(value[i][0], value[i][1]))
                    i = i +1
                return return_list
        elif (isinstance(value[0],str)):
                return val_function(value[0])
    except:
        return 'error'

# def StringValidator_compare_test(val_function, value): and so on... for validator functions --> could move these functions to another file
# input format
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
            pass
        try:
            check_id = rule_mapping[i]['check_id']
            print(f'check_id: {check_id}')
        except KeyError:
            print(f"'check_id' key does not exist for {rule_mapping[i]['rule_name']} rule in rule_mapping.json")
        if check_id in checks:
            data_type = checks[check_id]['data_type']
            check_function = checks[check_id]['check_function']
            val_function = code_checker.map_to_function(data_type, check_function)
            val_function_name = f"{data_type.title()}Validator.{check_function}"
            print(f"validator function: {val_function_name}")
            valid = format_choice[i]['valid']
            invalid = format_choice[i]['invalid']
            print("test output:")
            if val_function_name == 'DatetimeValidator.compare':
                print(f"with valid test input: {DatetimeValidator_compare_test(val_function, valid)}")
                print(f"with invalid test input: {DatetimeValidator_compare_test(val_function, invalid)}")
            if val_function_name == 'DatetimeValidator.date_or_datetime_format_check':
                print(f"with valid test input: {DatetimeValidator_date_or_datetime_format_check_test(val_function, valid)}")
                print(f"with invalid test input: {DatetimeValidator_date_or_datetime_format_check_test(val_function, invalid)}")
            if val_function_name == 'UrlValidator.health_and_status_check':
                print(f"with valid test input: {UrlValidator_health_and_status_check_test(val_function, valid)}")
                print(f"with invalid test input: {UrlValidator_health_and_status_check_test(val_function, invalid)}")
            if val_function_name == 'UrlValidator.doi_link_update':
                print(f"with valid test input: {DOI_update_check(val_function, valid)}")
                print(f"with invalid test input: {DOI_update_check(val_function, invalid)}")
            # if val_function_name == 'StringValidator.compare':
                # print()  and so on ... for validator functions
            #
            # possibly: - create a list of validator check test functions
            # - see if modified val_function_name in function list (ex: f"{data_type.title()}Validator_{check_function}_test)
            # - call this func with valid and invalid values
    print('----------------------------------------------')
# close files
f.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()