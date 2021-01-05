import csv

from .constants import SCHEMA_PATHS

LEAF = "this_is_the_leaf_node"


class GcmdValidator:
    """
    Validator class for all the GCMD keywords (science, instruments, providers)
    """

    def __init__(self):
        self.keywords = {
            "science": GcmdValidator._create_science_keywords_dict(
                GcmdValidator._read_from_csv("science_keywords")
            ),
            "spatial_keyword": GcmdValidator._read_from_csv("locations", [1, 2, 3, 4]),
            "provider_short_name": GcmdValidator._read_from_csv("providers", [4]),
            "instrument_short_name": GcmdValidator._read_from_csv("instruments", [4]),
            "instrument_long_name": GcmdValidator._read_from_csv("instruments", [5]),
            "campaign_short_name": GcmdValidator._read_from_csv("projects", [1]),
            "campaign_long_name": GcmdValidator._read_from_csv("projects", [2]),
            "granule_data_format": GcmdValidator._read_from_csv("granuledataformat", [0, 1]),
        }

    @staticmethod
    def _create_science_keywords_dict(keywords):
        """
        Creates the science keywords dictionary from the values from the csv

        Args:
            keywords (list): List of list of row values from the csv file

        Returns:
            (dict): The lookup dictionary for GCMD science keywords
        """
        all_keywords = [[each.upper() for each in kw[:-1] if each.strip()] for kw in keywords]
        science_keywords_dict = {}
        for row in all_keywords:
            row_dict = GcmdValidator.dict_from_list(row)
            GcmdValidator.merge_dicts(science_keywords_dict, row_dict)
        return science_keywords_dict

    @staticmethod
    def _read_from_csv(keyword_kind, row_nums=None):
        """
        Reads keywords from the corresponding csv based on the kind of keyword

        Args:
            keyword_kind (str): The kind of keyword
                                (could be: science_keywords, projects, providers, instruments, locations)
            row_num (int, optional): The row number (zero indexed). Defaults to None.
                                     If row_num is provided, returns keywords from that specific row
                                     If not, returns all the rows

        Returns:
            (list): list of keywords or list of list of rows from the csv
        """
        with open(SCHEMA_PATHS[keyword_kind]) as csvfile:
            reader = csv.reader(csvfile)
            list_of_rows = list(reader)[2:]
            if row_nums:
                return_value = []
                for row_num in row_nums:
                    return_value.extend(
                        keyword.upper() for row in list_of_rows 
                            if (keyword := row[row_num].strip())
                    )
            else:
                return_value = list_of_rows
        return return_value

    @staticmethod
    def dict_from_list(row):
        """
        Converts a list to a nested dict
        """
        intermediate_dict = {row[0]: LEAF}
        if len(row) > 1:
            intermediate_dict[row[0]] = GcmdValidator.dict_from_list(row[1:])
        return intermediate_dict

    @staticmethod
    def merge_dicts(parent, child):
        """
        Merges child dict to the parent dict avoiding repetitions
        """
        if child == LEAF:
            return parent, child
        else:
            for key in child:
                if parent.get(key):
                    parent[key], _ = GcmdValidator.merge_dicts(parent[key], child[key])
                else:
                    parent[key] = child[key]
        return parent, child

    @staticmethod
    def validate_recursively(all_keywords, input_keyword):
        """
        Validates if the input_keyword is a valid keyword from all_keywords

        Args:
            all_keywords (dict): The dictionary of science keywords
            input_keyword (list): The input keyword as a list based on the hierarchy

        Returns:
            (bool, str/None): The validity of the keyword and the invalid keyword (if any)
        """
        current_val = input_keyword[0]
        subset_dict = all_keywords.get(current_val)
        if not subset_dict:
            return False, current_val
        if len(input_keyword) == 1:
            return True, None
        return GcmdValidator.validate_recursively(subset_dict, input_keyword[1:])

    def validate_science_keyword(self, input_keyword):
        """
        Validates GCMD science keywords
        """
        return GcmdValidator.validate_recursively(
            self.keywords["science"], input_keyword
        )

    def validate_instrument_short_name(self, input_keyword):
        """
        Validates GCMD instrument short name
        """
        return input_keyword in self.keywords["instrument_short_name"]

    def validate_instrument_long_name(self, input_keyword):
        """
        Validates GCMD instrument long name
        """
        return input_keyword in self.keywords["instrument_long_name"]

    def validate_provider_short_name(self, input_keyword):
        """
        Validates GCMD provider short name
        """
        return input_keyword in self.keywords["provider_short_name"]

    def validate_spatial_keyword(self, input_keyword):
        """
        Validates GCMD spatial keyword
        """
        return input_keyword in self.keywords["spatial_keyword"]

    def validate_campaign_short_name(self, input_keyword):
        """
        Validates GCMD Campaign Short Name
        """
        return input_keyword in self.keywords["campaign_short_name"]

    def validate_campaign_long_name(self, input_keyword):
        """
        Validates GCMD Campaign Long Name
        """
        return input_keyword in self.keywords["campaign_long_name"]

    def validate_data_format(self, input_keyword):
        """
        Validates GCMD Granule Data Format
        """
        return input_keyword in self.keywords["granule_data_format"]
