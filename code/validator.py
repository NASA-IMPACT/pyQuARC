import csv
import json
import re
import requests

from datetime import datetime
from urlextract import URLExtract

from .constants import SCHEMA_PATHS
from .utils import prepare_received_gcmd_keywords_list, prepare_gcmd_keywords_dict


class BaseValidator:
    """
    Base class for all the validators
    """

    def __init__(self):
        pass

    @staticmethod
    def eq(first, second):
        return first == second

    @staticmethod
    def neq(first, second):
        return first == second

    @staticmethod
    def lt(first, second):
        return first < second

    @staticmethod
    def lte(first, second):
        return first <= second

    @staticmethod
    def gt(first, second):
        return first > second

    @staticmethod
    def gte(first, second):
        return first >= second

    @staticmethod
    def is_in(value, list_of_values):
        return value in list_of_values

    @staticmethod
    def compare(first, second, relation):
        func = getattr(BaseValidator, relation)
        return func(first, second)


class DatetimeValidator(BaseValidator):
    """
    Validator class for datetime datatype
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def _iso_datetime(datetime_string):
        """
        Converts the input datetime string to iso datetime object

        Args:
            datetime_string (str): the datetime string

        Returns:
            (datetime.datetime) If the string is valid iso string, False otherwise
        """

        REGEX = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
        match_iso8601 = re.compile(REGEX).match
        try:
            if match_iso8601(datetime_string) is not None:
                if datetime_string.endswith("Z"):
                    datetime_string = datetime_string.replace("Z", "+00:00")
                value = datetime.fromisoformat(datetime_string)
                return value
        except:
            pass
        return False

    @staticmethod
    def iso_format_check(datetime_string):
        """
        Performs the Date/DateTime ISO Format Check - checks if the datetime
        is valid ISO formatted datetime string

        Args:
            datetime_string (str): The datetime string
        
        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": bool(DatetimeValidator._iso_datetime(datetime_string)),
            "value": datetime_string
        }

    @staticmethod
    def compare(first, second, relation):
        """
        Compares two datetime values based on the argument relation

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        values = [DatetimeValidator._iso_datetime(time) for time in [first, second]]
        result = BaseValidator.compare(*values, relation)
        return {
            "valid": result,
            "value": (first, second)
        }

    @staticmethod
    def delete_time_check(datetime_string):
        delete_time = DatetimeValidator._iso_datetime(datetime_string)
        result = BaseValidator.compare(
            delete_time.replace(tzinfo=None), # need to make it offset-naive for comparison
            datetime.now(),
            "gte"
            )
        return {
            "valid": result,
            "value": datetime_string
        }

class StringValidator(BaseValidator):
    """
    Validator class for string values
    """
    all_keywords = []
    with open(SCHEMA_PATHS["science_keywords"]) as csvfile:
        reader = csv.reader(csvfile)
        # each row in the csv file corresponds to one valid hierarchy instance of GCMD keyword
        all_keywords = list(reader)

    def __init__(self):
        super().__init__()

    @staticmethod
    def length_check(string, args):
        """
        Checks if the length of the string is valid based on the extent 
        and relation provided in the args

        Args:
            string (str): The input string
            args (list): [extent (int), relation (str)] The extent and the relation

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        extent, relation = args
        length = len(string)
        return {
            "valid": BaseValidator.compare(length, extent, relation),
            "value": length
        }

    @staticmethod
    def compare(first, second, relation):
        """
        Compares two strings based on the relationship

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": BaseValidator.compare(first, second, relation),
            "value": (first, second)
        }

    @staticmethod
    def controlled_keywords_check(value, keywords_list):
        """
        Checks if `value` is in `keywords_list`

        Args:
            value (str/int): The value of the field
            keyword_list (list): The controlled keywords list

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        return {
            "valid": str(value) in keywords_list,
            "value": value
        }
    
    @staticmethod
    def gcmd_keywords_check(*args):
        """
        Checks if the GCMD keyword hierarchy is correct

        Args:
            args (list of lists): List of lists of the keywords in order of hierarchy
                If there are multiple GCMD keywords, it'll be in the form:
                [
                    [Category_1, Category_2, ...],
                    [Topic_1, Topic_2, ...],
                    [Term_1, Term_2, ...],
                    [VariableLevel1_1, VariableLevel1_2, ...],
                    [VariableLevel2_1, VariableLevel2_2, ...],
                    [VariableLevel3_1, VariableLevel3_2, ...],
                    [DetailedVariable_1, DetailedVariable_2, ...]
                ]

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        GCMD_KEYWORDS = prepare_gcmd_keywords_dict(
            StringValidator.all_keywords
        )

        received_keywords = prepare_received_gcmd_keywords_list(*args)

        valid = True
        value = []

        for keyword in received_keywords:
            if not BaseValidator.compare(keyword, GCMD_KEYWORDS, "is_in"):
                valid = False
                value.append(keyword)
        
        return {
            "valid": valid,
            "value": value if value else received_keywords
        }

    @staticmethod
    def ends_at_present_flag_logic_check(
        ends_at_present_flag,
        ending_date_time,
        collection_state
        ):
        valid = True
        if ends_at_present_flag == "true":
            if ending_date_time.strip() or collection_state == "COMPLETE":
                valid = False
        elif ends_at_present_flag == "false":
            if not ending_date_time.strip() or collection_state == "ACTIVE":
                valid = False

        return {
            "valid": valid,
            "value": ends_at_present_flag
        }

    @staticmethod
    def mime_type_check(mime_type, url_type, controlled_list):
        result = {
            "valid": True,
            "value": mime_type
        }

        if "USE SERVICE API" in url_type:
            if mime_type.strip():
                result = StringValidator.controlled_keywords_check(mime_type, controlled_list)
        
        return result
            

class UrlValidator(StringValidator):
    """
    Validator class for URLs
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def health_and_status_check(text_with_urls):
        """
        Checks the health and status of the URLs included in `text`

        Args:
           text_with_urls (str, required): The text that contains the URLs where the check needs to be performed

        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        results = []

        validity = True
        value = text_with_urls

        # extract URLs from text
        extractor = URLExtract()
        urls = extractor.find_urls(text_with_urls)

        # remove dots at the end (The URLExtract library catches URLs, but sometimes appends a '.' at the end)
        # remove duplicated urls
        urls = set(url[:-1] if url.endswith(".") else url for url in urls)

        # check that URL returns a valid response
        for url in urls:
            if not url.startswith('http'):
                url = f'http://{url}'
            try:
                response_code = requests.get(url).status_code
                if response_code == 200:
                    continue
                result = {"url": url, "status_code": response_code}
            except requests.ConnectionError as exception:
                result = {"url": url,
                          "error": "The URL does not exist on Internet."}
            except Exception as e:
                result = {"url": url, "error": "Some unknown error occurred."}
            results.append(result)

        if results:
            validity = False
            value = results

        return {"valid": validity, "value": value}

    @staticmethod
    def doi_check(doi):
        """
        Checks if the doi link given in the text is a valid doi link

        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        url = f"https://www.doi.org/{doi}"
        return UrlValidator.health_and_status_check(url)
