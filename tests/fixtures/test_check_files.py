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
# note: field / relation / data values should be added to test files in valid / invalid lists
code_checker = Checker()
format_dict = {'dif10': dif10_checks, 'echo-c': echo_c_checks, 'echo-g': echo_g_checks, 'umm-c': umm_c_checks, 'umm-g': umm_g_checks}
format_in = ''
rule = ''
check_id = ''
data_type = ''
check_function = ''

# functions to call validator function and return what is returned from validator function when given valid or invalid values as arguments
def DatetimeValidator_iso_format_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error (within DatetimeValidator_iso_format_check_test function)'
def DatetimeValidator_compare_test(val_function, value):
    dependency = code_checker.map_to_function("datetime", "iso_format_check")
    dependency_bool = True
    if (isinstance(value[0],list)):
        i = 0
        for x in value:
            temp = DatetimeValidator_iso_format_check_test(dependency, value[i])
            if temp['valid'] == False:
                return 'Fails dependency'
    if (isinstance(value[0],str)):
        temp = DatetimeValidator_iso_format_check_test(dependency, value)
        if temp['valid'] == False:
            return 'Fails dependency'
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            try: 
                DatetimeValidator_iso_format_check_test(dependency, value[0])
            except:
                print('dependency error')
            return val_function(value[0], value[1], value[2])
    except:
        return 'error'
def DatetimeValidator_date_or_datetime_format_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
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
                i = i + 1
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
                return val_function(value[0], value[1])
    except:
        return 'error'

def CustomValidator_one_item_presence_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'
def StringValidator_compare_test(val_function, value):
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
        return 'error'
def CustomValidator_availability_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1])
    except:
        return 'error'
def StringValidator_science_keywords_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3], value[i][4], value[i][5]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3], value[4], value[5])
    except:
        return 'error'
def StringValidator_location_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'
def CustomValidator_ends_at_present_flag_logic_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                if value[i][0] == "True" or value[i][0] == "true":
                    return_list.append(val_function(True, value[i][1], value[i][2]))
                elif value[i][0] == "False" or value[i][0] == "false":
                    return_list.append(val_function(False, value[i][1], value[i][2]))
                else:
                    print("error")
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2])
    except:
        return 'error'
def CustomValidator_ends_at_present_flag_presence_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                if value[i][0] == "":
                    return_list.append(val_function(None, value[i][1], value[i][2]))
                else:
                    return_list.append(val_function(value[i][0], value[i][1], value[i][2]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            if value[0] == "":
                return val_function(None, value[1], value[2])
            else:
                return val_function(value[0], value[1], value[2])
    except:
        return 'error'
def CustomValidator_mime_type_check_test(val_function, value):
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
        return 'error'
def CustomValidator_bounding_coordinate_logic_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3])
    except:
        return 'error'
def CustomValidator_user_services_check_test(val_function, value):
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
        return 'error'
def CustomValidator_doi_missing_reason_explanation_test(val_function, value):
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
        return 'error'
def DatetimeValidator_validate_ending_datetime_against_granules_test(val_function, value):
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
        return 'error'
def DatetimeValidator_validate_beginning_datetime_against_granules_test(val_function, value):
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
        return 'error'
def StringValidator_controlled_keywords_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1])
    except:
        return 'error'


def UrlValidator_Url_check(val_function, value):
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
def CustomValidator_count_check_test(val_function, value):
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
        return 'error'
def CustomValidator_collection_progress_consistency_check_test(val_function, value):
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
        return 'error'
def StringValidator_organization_short_name_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def UrlValidator_doi_check_test(val_function, value):
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
def StringValidator_organization_long_name_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'


def UrlValidator_get_data_url_check(val_function, value):
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

def StringValidator_instrument_short_name_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'    

def CustomValidator_shortname_uniqueness(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i +1
                return return_list
            if (isinstance(value[0], str)):
                return val_function(value[0])
    except:
        return 'error'

def StringValidator_instrument_long_name_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'    
def StringValidator_platform_short_name_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_data_format_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'

def StringValidator_platform_long_name_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_spatial_keyword_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_platform_type_gcmd_check_test(valfunction, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'

def StringValidator_abstract_length_check(val_function, value):
    try:
        if(isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i +1
                return return_list
            if (isinstance(value[0], str)):
                return val_function(value[0])
    except:
        return 'warning'

def StringValidator_characteristic_name_length_check(val_function, value):
    try:
        if(isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i +1
                return return_list
            if (isinstance(value[0], str)):
                return val_function(value[0])
    except:
        return 'error'

def StringValidator_campaign_short_name_gcmd_check_test(valfunction, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_characteristic_desc_length_check(val_function, value):
    try:
        if(isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2]))
                i = i +1
                return return_list
            if (isinstance(value[0],str)):
                return val_function(value[0], value[1], value[2])
    except:
        return 'error'
def StringValidator_Campaign_long_name_gcmd_check_test(valfunction, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_horizontal_range_res_gcmd_check_test(valfunction, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_vertical_range_res_gcmd_check_test(valfunction, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_temporal_range_res_gcmd_check_test(valfunction, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_mime_type_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_idnnode_shortname_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_chrono_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'


def StringValidator_characteristic_unit_length_check(val_function, value):
    try:
        if(isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2]))
                i = i +1
                return return_list
            if (isinstance(value[0], str)):
                return val_function(value[0], value[1], value[2])
    except:
        return 'error'
def StringValidator_length_check_test(val_function, value):
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
        return 'error'

def StringValidator_characteristic_value_length_check(val_function, value):
    try:
        if(isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i +1
                return return_list
            if (isinstance(value[0], str)):
                return val_function(value[0])
    except:
        return 'error'
def StringValidator_validate_granule_instrument_against_collection_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3])
    except:
        return 'error'
def CustomValidator_boolean_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
def StringValidator_online_resource_type_gcmd_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0])
    except:
        return 'error'
                

def CustomValidator_uniqueness_check_test(val_function, value):
    try:
        if (isinstance(value[0][0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1]))
                i = i + 1
            return return_list
        if (isinstance(value[0][0],dict)):
            return val_function(value[0], value[1])
    except:
        return 'error'
def StringValidator_validate_granule_platform_against_collection_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3])
    except:
        return 'error'
def StringValidator_granule_project_short_name_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3])
    except:
        return 'error'
def StringValidator_granule_sensor_short_name_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3])
    except:

        return 'error'
def StringValidator_validate_granule_data_format_against_collection_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1], value[i][2], value[i][3]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(value[0], value[1], value[2], value[3])
    except:
        return 'error'
def StringValidator_organization_short_long_name_consistency_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'
def StringValidator_instrument_short_long_name_consistency_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'
def StringValidator_platform_short_long_name_consistency_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'
def StringValidator_campaign_short_long_name_consistency_check_test(val_function, value):
    try:
        if (isinstance(value[0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(*value[i]))
                i = i + 1
            return return_list
        if (isinstance(value[0],str)):
            return val_function(*value)
    except:
        return 'error'
def CustomValidator_get_data_url_check_test(val_function, value):
    try:
        if (isinstance(value[0][0],list)):
            i = 0
            return_list = []
            for x in value:
                return_list.append(val_function(value[i][0], value[i][1]))
                i = i + 1
            return return_list
        if (isinstance(value[0][0],dict)):
            return val_function(value[0], value[1])
    except:
        return 'error
# iterate through metadata formats
for k in format_dict.keys():
    format_in = k
    print('\n----------------------------------------------\n')
    print(f'Test output for format {format_in}:')
    print('\n----------------------------------------------\n')
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
                pass
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
                if val_function_name == 'UrlValidator.doi_link_update':
                    print(f"with valid test input: {DOI_update_check(val_function, valid)}")
                    print(f"with invalid test input: {DOI_update_check(val_function, invalid)}")
                if val_function_name == 'DatetimeValidator.date_or_datetime_format_check':
                    print(f"with valid test input: {DatetimeValidator_date_or_datetime_format_check_test(val_function, valid)}")
                    print(f"with invalid test input: {DatetimeValidator_date_or_datetime_format_check_test(val_function, invalid)}")
                    # assert_func(val_function, DatetimeValidator_date_or_datetime_format_check_test, valid, invalid)
                if val_function_name == 'UrlValidator.doi_check':
                    print(f"with valid test input: {UrlValidator_doi_check_test(val_function, valid)}")
                    print(f"with invalid test input: {UrlValidator_doi_check_test(val_function, invalid)}")
                    # assert_func(val_function, DatetimeValidator_date_or_datetime_format_check_test, valid, invalid)
                if val_function_name == 'UrlValidator.health_and_status_check':
                    print(f"with valid test input: {UrlValidator_health_and_status_check_test(val_function, valid)}")
                    print(f"with invalid test input: {UrlValidator_health_and_status_check_test(val_function, invalid)}")
                    # assert_func(val_function, UrlValidator_health_and_status_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.one_item_presence_check':
                    print(f"with valid test input: {CustomValidator_one_item_presence_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_one_item_presence_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_one_item_presence_check_test, valid, invalid)
                if val_function_name == 'StringValidator.compare':
                    print(f"with valid test input: {StringValidator_compare_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_compare_test(val_function, invalid)}")
                    # assert_func(val_function, StringValidator_compare_test, valid, invalid)
                if val_function_name == 'CustomValidator.availability_check':
                    print(f"with valid test input: {CustomValidator_availability_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_availability_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_availability_check_test, valid, invalid)
                if val_function_name == 'StringValidator.science_keywords_gcmd_check':
                    print(f"with valid test input: {StringValidator_science_keywords_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_science_keywords_gcmd_check_test(val_function, invalid)}")
                    # assert_func(val_function, StringValidator_science_keywords_gcmd_check_test, valid, invalid)
                if val_function_name == 'StringValidator.location_gcmd_check':
                    print(f"with valid test input: {StringValidator_location_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_location_gcmd_check_test(val_function, invalid)}")
                    # assert_func(val_function, StringValidator_location_gcmd_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.ends_at_present_flag_logic_check':
                    print(f"with valid test input: {CustomValidator_ends_at_present_flag_logic_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_ends_at_present_flag_logic_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_ends_at_present_flag_logic_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.ends_at_present_flag_presence_check':
                    print(f"with valid test input: {CustomValidator_ends_at_present_flag_presence_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_ends_at_present_flag_presence_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_ends_at_present_flag_presence_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.mime_type_check':
                    print(f"with valid test input: {CustomValidator_mime_type_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_mime_type_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_mime_type_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.bounding_coordinate_logic_check':
                    print(f"with valid test input: {CustomValidator_bounding_coordinate_logic_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_bounding_coordinate_logic_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_bounding_coordinate_logic_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.user_services_check':
                    print(f"with valid test input: {CustomValidator_user_services_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_user_services_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_user_services_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.doi_missing_reason_explanation':
                    print(f"with valid test input: {CustomValidator_doi_missing_reason_explanation_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_doi_missing_reason_explanation_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_doi_missing_reason_explanation_test, valid, invalid)
                if val_function_name == 'DatetimeValidator.validate_ending_datetime_against_granules':
                    print(f"with valid test input: {DatetimeValidator_validate_ending_datetime_against_granules_test(val_function, valid)}")
                    print(f"with invalid test input: {DatetimeValidator_validate_ending_datetime_against_granules_test(val_function, invalid)}")
                    # assert_func(val_function, DatetimeValidator_validate_ending_datetime_against_granules_test, valid, invalid)
                if val_function_name == 'DatetimeValidator.validate_beginning_datetime_against_granules':
                    print(f"with valid test input: {DatetimeValidator_validate_beginning_datetime_against_granules_test(val_function, valid)}")
                    print(f"with invalid test input: {DatetimeValidator_validate_beginning_datetime_against_granules_test(val_function, invalid)}")
                    # assert_func(val_function, DatetimeValidator_validate_beginning_datetime_against_granules_test, valid, invalid)
                if val_function_name == 'StringValidator.controlled_keywords_check':
                    print(f"with valid test input: {StringValidator_controlled_keywords_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_controlled_keywords_check_test(val_function, invalid)}")
                    # assert_func(val_function, StringValidator_controlled_keywords_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.count_check':
                    print(f"with valid test input: {CustomValidator_count_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_count_check_test(val_function, invalid)}")
                    # assert_func(val_function, CustomValidator_count_check_test, valid, invalid)
                if val_function_name == 'CustomValidator.collection_progress_consistency_check':
                    print(f"with valid test input: {CustomValidator_collection_progress_consistency_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_collection_progress_consistency_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.organization_short_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_organization_short_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_organization_short_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.organization_long_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_organization_long_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_organization_long_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.instrument_short_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_instrument_short_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_instrument_short_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.instrument_long_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_instrument_long_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_instrument_long_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.platform_short_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_platform_short_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_platform_short_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.data_format_gcmd_check':
                    print(f"with valid test input: {StringValidator_data_format_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_data_format_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.platform_long_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_platform_long_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_platform_long_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.spatial_keyword_gcmd_check':
                    print(f"with valid test input: {StringValidator_spatial_keyword_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_spatial_keyword_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.platform_type_gcmd_check':
                    print(f"with valid test input: {StringValidator_platform_type_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_platform_type_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.campaign_short_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_campaign_short_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_campaign_short_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.campaign_long_name_gcmd_check':
                    print(f"with valid test input: {StringValidator_Campaign_long_name_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_Campaign_long_name_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.horizontal_range_res_gcmd_check':
                    print(f"with valid test input: {StringValidator_horizontal_range_res_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_horizontal_range_res_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.vertical_range_res_gcmd_check':
                    print(f"with valid test input: {StringValidator_vertical_range_res_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_vertical_range_res_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.temporal_range_res_gcmd_check':
                    print(f"with valid test input: {StringValidator_temporal_range_res_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_temporal_range_res_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.mime_type_gcmd_check':
                    print(f"with valid test input: {StringValidator_mime_type_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_mime_type_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.idnnode_shortname_gcmd_check':
                    print(f"with valid test input: {StringValidator_idnnode_shortname_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_idnnode_shortname_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.chrono_gcmd_check':
                    print(f"with valid test input: {StringValidator_chrono_gcmd_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_chrono_gcmd_check_test(val_function, invalid)}")
                if val_function_name == 'DatetimeValidator.iso_format_check':
                    print(f"with valid test input: {DatetimeValidator_iso_format_check_test(val_function, valid)}")
                    print(f"with invalid test input: {DatetimeValidator_iso_format_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.length_check':
                    print(f"with valid test input: {StringValidator_length_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_length_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.validate_granule_instrument_against_collection':
                    print(f"with valid test input: {StringValidator_validate_granule_instrument_against_collection_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_validate_granule_instrument_against_collection_test(val_function, invalid)}")
                if val_function_name == 'CustomValidator.boolean_check':
                    print(f"with valid test input: {CustomValidator_boolean_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_boolean_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.online_resource_type_gcmd_check':
                    print(f"with valid test input: {CustomValidator_boolean_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_boolean_check_test(val_function, invalid)}")
                if val_function_name == 'CustomValidator.uniqueness_check':
                    print(f"with valid test input: {CustomValidator_uniqueness_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_uniqueness_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.validate_granule_platform_against_collection':
                    print(f"with valid test input: {StringValidator_validate_granule_platform_against_collection_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_validate_granule_platform_against_collection_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.granule_project_short_name_check':
                    print(f"with valid test input: {StringValidator_granule_project_short_name_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_granule_project_short_name_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.granule_sensor_short_name_check':
                    print(f"with valid test input: {StringValidator_granule_sensor_short_name_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_granule_sensor_short_name_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.validate_granule_data_format_against_collection':
                    print(f"with valid test input: {StringValidator_validate_granule_data_format_against_collection_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_validate_granule_data_format_against_collection_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.organization_short_long_name_consistency_check':
                    print(f"with valid test input: {StringValidator_organization_short_long_name_consistency_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_organization_short_long_name_consistency_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.instrument_short_long_name_consistency_check':
                    print(f"with valid test input: {StringValidator_instrument_short_long_name_consistency_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_instrument_short_long_name_consistency_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.platform_short_long_name_consistency_check':
                    print(f"with valid test input: {StringValidator_platform_short_long_name_consistency_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_platform_short_long_name_consistency_check_test(val_function, invalid)}")
                if val_function_name == 'StringValidator.campaign_short_long_name_consistency_check':
                    print(f"with valid test input: {StringValidator_campaign_short_long_name_consistency_check_test(val_function, valid)}")
                    print(f"with invalid test input: {StringValidator_campaign_short_long_name_consistency_check_test(val_function, invalid)}")
                if val_function_name == 'CustomValidator.get_data_url_check':
                    print(f"with valid test input: {CustomValidator_get_data_url_check_test(val_function, valid)}")
                    print(f"with invalid test input: {CustomValidator_get_data_url_check_test(val_function, invalid)}")                # possibly: - create a list of validator check test functions
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
