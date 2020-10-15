import csv
import json
import re
import requests

from datetime import datetime
from urlextract import URLExtract

from .constants import SCHEMA_PATHS


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

        regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
        match_iso8601 = re.compile(regex).match
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


class StringValidator(BaseValidator):
    """
    Validator class for string values
    """
    all_keywords = []
    with open(SCHEMA_PATHS["science_keywords"]) as csvfile:
        reader = csv.reader(csvfile)
        all_keywords = [row for row in reader]

    def __init__(self):
        super().__init__()

    @staticmethod
    def length_check(string, maximum_length=100):
        """
        Checks if the length of the string is less than or equal to maximum length

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        length = len(string)
        return {
            "valid": length <= maximum_length,
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
    def processing_level_id_check(processing_level_id):
        """
        Checks if the processing level id is one of the valid ids

        Args:
            processing_level_id (int/str): The processing level id
        
        Returns:
            (dict) An object with the validity of the check and the instance
        """
        vocabulary = ['0', '1A', '1B', '2', '3', '4']
        return {
            "valid": BaseValidator.compare(str(processing_level_id), vocabulary, "is_in"),
            "value": processing_level_id
        }

    @staticmethod
    def eosdis_doi_authority_check(input_url):
        """
        Checks if the DOI Authority is valid
        """
        url = "https://doi.org"
        vocabulary = [url, f"{url}/"]
        return {
            "valid": BaseValidator.compare(input_url, vocabulary, "is_in"),
            "value": input_url
        }

    @staticmethod
    def gcmd_keywords_check(*args):
        """
        Checks if the GCMD keyword hierarchy is correct

        Args:
            args (list): List of the keywords based listed in order of hierarchy
                [Category, Topic, Term, VariableLevel1, VariableLevel2, VariableLevel3, DetailedVariable]

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        combined_keywords = {}
        for row in StringValidator.all_keywords:
            keyword = '/'.join([keyword.lower().strip() for keyword in row[:-1]])
            keyword = keyword.strip('/')
            combined_keywords[keyword] = True

        keywords_lists_unordered = [arg for arg in args if arg is not None]
        ordered_keyword_list = list(zip(*keywords_lists_unordered))
        received_keywords = []
        for keywords in ordered_keyword_list:
            received_keywords.append(
                '/'.join([keyword.lower().strip() for keyword in keywords if keyword != None])
            )

        valid = True
        value = received_keywords

        for keyword in received_keywords:
            if keyword not in combined_keywords:
                valid = False
                value = keyword
        
        return {
            "valid": valid,
            "value": value
        }


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
