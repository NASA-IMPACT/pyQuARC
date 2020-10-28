import csv

from .constants import SCHEMA_PATHS


class GcmdValidator:

    def __init__(self):
        all_keywords = []
        with open(SCHEMA_PATHS["science_keywords"]) as csvfile:
            reader = csv.reader(csvfile)
            all_keywords = list(reader)[2:]

        all_keywords = [[each for each in kw[:-1] if each.strip()] for kw in all_keywords]
        self.gcmd_keywords_dict = {}
        for row in all_keywords:
            row_dict = GcmdValidator.create_dict_from_list(row)
            GcmdValidator.merge(self.gcmd_keywords_dict, row_dict)

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

    def validate(self, input_keyword):
        return GcmdValidator.validate_recursively(self.gcmd_keywords_dict, input_keyword)
