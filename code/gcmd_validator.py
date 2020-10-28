import csv

from .constants import SCHEMA_PATHS


class GcmdValidator:

    def __init__(self):
        self.keywords = {
            "science": GcmdValidator._create_science_keywords_dict(
                GcmdValidator._read_from_csv("science_keywords")
            ),
            "provider_short_name": GcmdValidator._read_from_csv("providers", 4),
            "instrument_short_name": GcmdValidator._read_from_csv("instruments", 4),
            "instrument_long_name": GcmdValidator._read_from_csv("instruments", 5)
        }

    @staticmethod
    def _create_science_keywords_dict(keywords):
        all_keywords = [[each for each in kw[:-1] if each.strip()] for kw in keywords]
        science_keywords_dict = {}
        for row in all_keywords:
            row_dict = GcmdValidator.create_dict_from_list(row)
            GcmdValidator.merge(science_keywords_dict, row_dict)
        return science_keywords_dict

    @staticmethod
    def _read_from_csv(keyword_kind, row_num=None):
        with open(SCHEMA_PATHS[keyword_kind]) as csvfile:
            reader = csv.reader(csvfile)
            if row_num:
                return_value = [
                    row[row_num]
                        for row in list(reader)[2:]
                            if row[row_num].strip()
                ]
            else:
                return_value = list(reader)[2:]
        return return_value

    @staticmethod
    def prepare_received_gcmd_keywords_list(*args):
        keywords_lists_unordered = [arg for arg in args if arg is not None]
        ordered_keyword_list = list(zip(*keywords_lists_unordered))
        received_keywords = []
        for keywords in ordered_keyword_list:
            received_keywords.append(
                # converting the keywords to uppercase and
                # stripping any whitespaces for consistency
                # stripping any extra slashes in case there's no value for the field
                # '/'.join([keyword.upper().strip() for keyword in keywords]).strip('/')
                [keyword.upper().strip() for keyword in keywords if keyword.strip()]
            )
        return received_keywords

    @staticmethod
    def create_dict_from_list(row):
        intermediate_dict = {}
        if len(row) == 1:
            return {row[0]: None}
        else:
            intermediate_dict[row[0]] = GcmdValidator.create_dict_from_list(row[1:])
        return intermediate_dict

    @staticmethod
    def merge(parent, child):
        if not (child):
            return parent, child
        else:
            for key in child:
                if parent.get(key):
                    parent[key], _ = GcmdValidator.merge(parent[key], child[key])
                else:
                    parent[key] = child[key]
        return parent, child

    @staticmethod
    def validate_recursively(all_keywords, input_keyword_list):
        current_val = input_keyword_list[0]
        try:
            subset_dict = all_keywords[current_val]
        except:
            return False, current_val
        if len(input_keyword_list) == 1:
            return True, None
        return GcmdValidator.validate_recursively(subset_dict, input_keyword_list[1:])

    def validate_science_keyword(self, input_keyword):
        return GcmdValidator.validate_recursively(self.keywords["science"], input_keyword)

    def validate_instrument_short_name(self, input_keyword):
        return input_keyword in self.keywords["instrument_short_name"]

    def validate_instrument_long_name(self, input_keyword):
        return input_keyword in self.keywords["instrument_long_name"]

    def validate_provider_short_name(self, input_keyword):
        return input_keyword in self.keywords["provider_short_name"]

