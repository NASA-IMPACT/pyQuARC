import csv
import os
import requests

from .utils import get_headers

from .constants import SCHEMA_PATHS, GCMD_LINKS, VERSION_FILE
from datetime import datetime

LEAF = "this_is_the_leaf_node"
DATE_FORMAT = "%Y-%m-%d"


class GcmdValidator:
    """
    Validator class for all the GCMD keywords (science, instruments, providers)
    """

    downloaded = {keyword: False for keyword in GCMD_LINKS}

    def __init__(self):
        GcmdValidator._download_files()
        self.file_content = GcmdValidator._load_csvs()
        self.keywords = {
            "science": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv("sciencekeywords")
            ),
            "spatial_keyword": self._read_from_csv(
                "locations",
                columns=[
                    "Location_Category",
                    "Location_Type",
                    "Location_Subregion1",
                    "Location_Subregion2",
                    "Location_Subregion3",
                ],
            ),
            "locations": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv("locations")
            ),
            "provider": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv(
                    "providers", columns=["Short_Name", "Long_Name"], hierarchy=True
                )
            ),
            "provider_short_name": self._read_from_csv(
                "providers", columns=["Short_Name"]
            ),
            "provider_long_name": self._read_from_csv(
                "providers", columns=["Long_Name"]
            ),
            "instrument": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv(
                    "instruments", columns=["Short_Name", "Long_Name"], hierarchy=True
                )
            ),
            "instrument_short_name": self._read_from_csv(
                "instruments", columns=["Short_Name"]
            ),
            "instrument_long_name": self._read_from_csv(
                "instruments", columns=["Long_Name"]
            ),
            "campaign": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv(
                    "projects", columns=["Short_Name", "Long_Name"], hierarchy=True
                )
            ),
            "campaign_short_name": self._read_from_csv(
                "projects", columns=["Short_Name"]
            ),
            "campaign_long_name": self._read_from_csv(
                "projects", columns=["Long_Name"]
            ),
            "granule_data_format": self._read_from_csv(
                "granuledataformat", columns=["Short_Name", "Long_Name"]
            ),
            "platform": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv(
                    "platforms", columns=["Short_Name", "Long_Name"], hierarchy=True
                )
            ),
            "platform_short_name": self._read_from_csv(
                "platforms", columns=["Short_Name"]
            ),
            "platform_long_name": self._read_from_csv(
                "platforms", columns=["Long_Name"]
            ),
            "platform_type": self._read_from_csv("platforms", columns=["Category"]),
            "rucontenttype": self._read_from_csv(
                "rucontenttype", columns=["Type", "Subtype"]
            ),
            "chronounits": GcmdValidator._create_hierarchy_dict(
                self._read_from_csv("chronounits")
            ),
            "horizontalresolutionrange": self._read_from_csv(
                "horizontalresolutionrange", columns=["Horizontal_Resolution_Range"]
            ),
            "verticalresolutionrange": self._read_from_csv(
                "verticalresolutionrange", columns=["Vertical_Resolution_Range"]
            ),
            "temporalresolutionrange": self._read_from_csv(
                "temporalresolutionrange", columns=["Temporal_Resolution_Range"]
            ),
            "mimetype": self._read_from_csv("MimeType", columns=["MimeType"]),
            "idnnode_shortname": self._read_from_csv("idnnode", columns=["Short_Name"]),
        }

    @staticmethod
    def _download_files(force=False):
        """
        Downloads and maintains a copy of the csv files from the gcmd server once a day
        """
        current_datetime = datetime.now()
        headers = get_headers()
        date_str = current_datetime.strftime(DATE_FORMAT)
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE) as file:
                date_str = file.readline().replace("\n", "")
        gcmd_date = datetime.strptime(date_str, DATE_FORMAT)
        if gcmd_date.date() < current_datetime.date() or force:
            try:
                for keyword, link in GCMD_LINKS.items():
                    # Downloading updated gcmd keyword files
                    response = requests.get(link, headers=headers)
                    data = response.text
                    with open(
                        SCHEMA_PATHS[keyword], "w", encoding="utf-8"
                    ) as download_file:
                        download_file.write(data)
                with open(VERSION_FILE, "w") as version_file:
                    version_file.write(current_datetime.strftime(DATE_FORMAT))
            except:
                # Download of files failed. Using local copies, which are already there
                pass

    @staticmethod
    def _create_hierarchy_dict(rows):
        """
        Creates the hierarchy dictionary from the values from the csv

        Args:
            rows (list): List of list of row values from the csv file

        Returns:
            (dict): The lookup dictionary for GCMD hierarchy
        """
        all_keywords = [
            [keyword.upper() for keyword in row if keyword.strip()]
            for row in rows
            if row
        ]
        hierarchy_dict = {}
        for row in all_keywords:
            row_dict = GcmdValidator.dict_from_list(row)
            GcmdValidator.merge_dicts(hierarchy_dict, row_dict)
        return hierarchy_dict

    @staticmethod
    def _load_csvs():
        content = {}
        for key, _ in GCMD_LINKS.items():
            csvfile = open(SCHEMA_PATHS[key])
            reader = csv.reader(csvfile)
            next(reader)  # Remove the metadata (1st column)
            headers = next(reader)  # Get the headers (2nd column)
            list_of_rows = list(reader)
            csvfile.close()
            content[key] = headers, list_of_rows
        return content

    def _read_from_csv(self, keyword_kind, columns=None, hierarchy=False):
        """
        Reads keywords from the corresponding csv based on the kind of keyword

        Args:
            keyword_kind (str): The kind of keyword
                (could be: sciencekeywords, projects, providers, instruments, locations)
            columns (list of int, optional): The columns to read. Defaults to None.
                If columns is provided, returns keywords from that specific column
                If not, returns all useful keywords based on the keyword kind

        Returns:
            (list): list of keywords or list of list of rows from the csv
        """
        headers, list_of_rows = self.file_content[keyword_kind]
        if (not hierarchy) and columns:
            return_value = []
            for column in columns:
                return_value.extend(
                    keyword.upper()
                    for row in list_of_rows
                    if (keyword := row[headers.index(column)].strip())
                )
        else:
            start = 1 if keyword_kind == "projects" else 0
            start = headers.index(columns[0]) if columns else 0
            end = (headers.index(columns[-1]) + 1) if columns else None
            # handling cases when there are multiple entries for same shortname but the first entry has missing long name
            return_value = [
                [
                    clean_keyword
                    for keyword in useful_data
                    if (clean_keyword := keyword.strip() or "N/A")
                ]
                for row in list_of_rows
                if (
                    useful_data := row[
                        start : end if end else (len(row) - 1)
                    ]  # remove UUID (last column)
                )
            ]
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
                if parent.get(key) and not (parent.get(key) == LEAF):
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

    def validate_instrument_short_long_name_consistency(self, input_keyword):
        """
        Validates GCMD instrument short name and long name consistency
        """
        return GcmdValidator.validate_recursively(
            self.keywords["instrument"], input_keyword
        )[0]

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

    def validate_platform_short_name(self, input_keyword):
        """
        Validates GCMD Platform short name
        """
        return input_keyword in self.keywords["platform_short_name"]

    def validate_platform_long_name(self, input_keyword):
        """
        Validates GCMD Platform long name
        """
        return input_keyword in self.keywords["platform_long_name"]

    def validate_platform_type(self, input_keyword):
        """
        Validates GCMD platform type
        """
        return input_keyword in self.keywords["platform_type"]

    def validate_platform_short_long_name_consistency(self, input_keyword):
        """
        Validates GCMD platform short name and long name consistency
        """
        return GcmdValidator.validate_recursively(
            self.keywords["platform"], input_keyword
        )[0]

    def validate_provider_short_name(self, input_keyword):
        """
        Validates GCMD provider short name
        """
        return input_keyword in self.keywords["provider_short_name"]

    def validate_provider_long_name(self, input_keyword):
        """
        Validates GCMD provider long name
        """
        return input_keyword in self.keywords["provider_long_name"]

    def validate_provider_short_long_name_consistency(self, input_keyword):
        """
        Validates GCMD provider short name and long name consistency
        """
        return GcmdValidator.validate_recursively(
            self.keywords["provider"], input_keyword
        )[0]

    def validate_spatial_keyword(self, input_keyword):
        """
        Validates GCMD spatial keyword
        """
        return input_keyword in self.keywords["spatial_keyword"]

    def validate_location_hierarchy(self, input_keyword):
        """
        Validates the Location hierarchy against GCMD 'locations' list
        """
        return GcmdValidator.validate_recursively(
            self.keywords["locations"], input_keyword
        )

    def validate_campaign_short_long_name_consistency(self, input_keyword):
        """
        Validates GCMD campaign short name and long name consistency
        """
        return GcmdValidator.validate_recursively(
            self.keywords["campaign"], input_keyword
        )[0]

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

    def validate_online_resource_type(self, input_keyword):
        """
        Validates the Online Resource Type against GCMD 'rucontent' list
        """
        return input_keyword in self.keywords["rucontenttype"]

    def validate_mime_type(self, input_keyword):
        """
        Validates the Mime Type against GCMD 'MimeType' list
        """
        return input_keyword in self.keywords["mimetype"]

    def validate_horizontal_resolution_range(self, input_keyword):
        """
        Validates the Horizontal Resolution Range against GCMD 'horizontalresolutionrange' list
        """
        return input_keyword in self.keywords["horizontalresolutionrange"]

    def validate_vertical_resolution_range(self, input_keyword):
        """
        Validates the vertical Resolution Range against GCMD 'verticalresolutionrange' list
        """
        return input_keyword in self.keywords["verticalresolutionrange"]

    def validate_temporal_resolution_range(self, input_keyword):
        """
        Validates the temporal Resolution Range against GCMD 'temporalresolutionrange' list
        """
        return input_keyword in self.keywords["temporalresolutionrange"]

    def validate_chrono_unit_hierarchy(self, input_keyword):
        """
        Validates GCMD science keywords
        """
        return GcmdValidator.validate_recursively(
            self.keywords["chronounits"], input_keyword
        )

    def validate_idnnode_shortname(self, input_keyword):
        """
        Validates GCMD science keywords
        """
        return input_keyword in self.keywords["idnnode_shortname"]
