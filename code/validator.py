import re
import requests

from datetime import datetime
from urlextract import URLExtract


class BaseValidator:
    def __init__(self):
        pass

    @staticmethod
    def eq(*args):
        return args[0] == args[1]

    @staticmethod
    def lt(*args):
        return args[0] < args[1]

    @staticmethod
    def lte(*args):
        return args[0] <= args[1]

    @staticmethod
    def gt(*args):
        return args[0] > args[1]

    @staticmethod
    def gte(*args):
        return args[0] >= args[1]

    @staticmethod
    def is_in(*args):
        return args[0] in args[1]

    @staticmethod
    def compare(*args):
        func = getattr(BaseValidator, args[-1])
        return func(*args[:-1])

class DatetimeValidator(BaseValidator):
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
    def iso_format_check(*args):
        """
        Performs the Date/DateTime ISO Format Check - checks if the datetime
        is valid ISO formatted datetime string

        Args:
            datetime_string (str): The datetime string
            data (dict): The data associated with/required by the rule. May be empty.
                            The format is: "data": {
                                            other fields as required by the rule (here, nothing)
                                        }

        Returns:
            (dict) An object with the validity of the check and the instance
        """
        datetime_string = args[0]
        return {
            "valid": bool(DatetimeValidator._iso_datetime(datetime_string)),
            "value": datetime_string
        }

    @staticmethod
    def compare(*args):
        values = [DatetimeValidator._iso_datetime(time) for time in args[:-1]]
        result = BaseValidator.compare(*values, args[-1])
        return {
            "valid": result,
            "value": (args[0], args[1])
        }

    @staticmethod
    def temporal_extent_requirement_check(*args):
        return {
            "valid": False,
            "value": None
        }


class StringValidator(BaseValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
    def length_check(*args):
        length = len(args[0])
        return {
            "valid": length <= 100,
            "value": length
        }
    
    @staticmethod
    def controlled_keywords_check(*args):
        return
    
    @staticmethod
    def compare(*args):
        return {
            "valid": BaseValidator.compare(*args[:-1], args[-1]),
            "value": (args[0], args[1])
        }

    @staticmethod
    def processing_level_id_check(*args):
        vocabulary = ['0', '1A', '1B', '2', '3', '4']
        return {
            "valid": BaseValidator.compare(str(args[0]), vocabulary, "is_in"),
            "value": args[0]
        }


class UrlValidator(StringValidator):
    def __init__(self):
        super().__init__()

    @staticmethod
    def health_and_status_check(*args):
        """
        Checks the health and status of the URLs included in `text`

        Args:
            text (str): The text that contains the URLs where the check needs to be performed
            data (dict): The data associated with/required by the rule. May be empty.
                            The format is: "data": {
                                            // fields as required by the rule (here, nothing)
                                        }

        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        text = args[0]
        results = []

        # extract URLs from text
        extractor = URLExtract()
        urls = extractor.find_urls(text)

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

        if not results:
            return {"valid": True, "value": args[0]}

        return {"valid": False, "value": results}

    @staticmethod
    def doi_check(*args):
        url = f"https://www.doi.org/{args[0]}"
        return UrlValidator.health_and_status_check(url)