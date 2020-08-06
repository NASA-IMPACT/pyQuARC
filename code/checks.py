import requests

from datetime import datetime

from urlextract import URLExtract


def _iso_datetime(datetime_string):
    if datetime_string.endswith("Z"):
        datetime_string = datetime_string.replace("Z", "+00:00")

    try:
        value = datetime.fromisoformat(datetime_string)
    except ValueError:
        return False
    return value


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
        "validity": bool(_iso_datetime(datetime_string))
    }


def data_updatetime_logic_check(earlier_datetime_string, later_datetime_string):
    # assume that iso check has already occurred
    earlier_datetime = _iso_datetime(earlier_datetime_string)
    later_datetime = _iso_datetime(later_datetime_string)

    return {
        "validity": earlier_datetime < later_datetime
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
        response_code = requests.get(url).status_code
        if response_code != 200:
            results.append(
                {"url": url, "status_code": response_code}
            )

    if len(results) == 0:
        return True

    return {
        "validity" : False,
        "result" : results
    }


dispatcher = {
    "datetime_iso_format_check": datetime_iso_format_check,
    "data_updatetime_logic_check": data_updatetime_logic_check,
    "url_health_and_status_check": url_health_and_status_check
}
