import re
import requests

from datetime import datetime

from urlextract import URLExtract


def _iso_datetime(datetime_string):
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


def _time_logic_check(earlier_datetime_string, later_datetime_string):
    # assume that iso check has already occurred
    earlier_datetime = _iso_datetime(earlier_datetime_string)
    later_datetime = _iso_datetime(later_datetime_string)

    return earlier_datetime <= later_datetime


def datetime_iso_format_check(datetime_string):
    """
        Parses through input_json and date time is in correct ISO format

        Arguments:
            input_json: data that is downloaded from the CMR, then converted to json
            path: path in the json in which to apply this function

        Return:
            True: if date/time is in correct ISO format
            False: if not
    """
    return {
        "valid": bool(_iso_datetime(datetime_string)),
        "instance": datetime_string
    }

def update_time_logic_check(value1, value2):
    return {
        "valid": _time_logic_check(value1, value2),
        "instance": {
            "InsertTime": value1,
            "LastUpdate": value2
        }
    }


def url_health_and_status_check(text):
    results = []

    # extract URLs from text
    extractor = URLExtract()
    urls = extractor.find_urls(text)

    # remove dots at the end
    # remove duplicated urls
    urls = set(url[:-1] if url.endswith(".") else url for url in urls)

    # check that URL returns a valid response
    for url in urls:
        try:
            response_code = requests.get(url).status_code
            if response_code != 200:
                results.append({"url": url, "status_code": response_code})
        except requests.ConnectionError as exception:
            result = {"url": url, "error": "The URL does not exist on Internet."}
        except Exception as e:
            result = {"url": url, "error": "Some unknown error occurred."}
        results.append(result)

    if len(results) == 0:
        return {"valid": True}

    return {"valid": False, "instance": results}


def collection_datatype_enumeration_check(text):
    KEYWORDS = ["SCIENCE_QUALITY", "NEAR_REAL_TIME", "OTHER"]

    return {"valid": text in KEYWORDS, "instance": text}


dispatcher = {
    "datetime_iso_format_check": datetime_iso_format_check,
    "update_time_logic_check": update_time_logic_check,
    "url_health_and_status_check": url_health_and_status_check,
    "collection_datatype_enumeration_check": collection_datatype_enumeration_check,
}
