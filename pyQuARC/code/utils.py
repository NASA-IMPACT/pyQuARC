import os
import requests
import urllib
from datetime import datetime

from functools import wraps

from .constants import CMR_URL, DATE_FORMATS


def if_arg(func):
    @wraps(func)
    def run_function_only_if_arg(*args):
        if args[0]:
            return func(*args)
        else:
            return {"valid": None, "value": None}

    return run_function_only_if_arg


def get_headers():
    token = os.environ.get("AUTH_TOKEN")
    headers = None
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    return headers


def _add_protocol(url):
    if not url.startswith("http"):
        url = f"https://{url}"
    return url


def is_valid_cmr_url(url):
    url = _add_protocol(url)
    valid = False
    headers = get_headers()
    try:  # some invalid url throw an exception
        response = requests.get(
            url, headers=headers, timeout=5
        )  # some invalid urls freeze
        valid = response.status_code == 200 and response.headers.get("CMR-Request-Id")
    except:
        valid = False
    return valid


def get_cmr_url():
    cmr_url = os.environ.get("CMR_URL", CMR_URL)
    return _add_protocol(cmr_url)


def set_cmr_prms(params, format="json", type="collections"):
    base_url = f"{type}.{format}?"
    params = {key: value for key, value in params.items() if value}
    return f"{base_url}{urllib.parse.urlencode(params)}"


def cmr_request(cmr_prms):
    headers = get_headers()
    return requests.get(f"{get_cmr_url()}/search/{cmr_prms}", headers=headers).json()


def collection_in_cmr(cmr_prms):
    return cmr_request(cmr_prms).get("hits", 0) > 0


def get_date_time(dt_str):
    """
    Convert a date and time string to a datetime object using predefined formats.
    This function attempts to parse a date and time string (`dt_str`) into a `datetime` object.
    It iterates over a list of possible date and time formats (`DATE_FORMATS`). The first successful
    parse using one of these formats will result in returning the corresponding `datetime` object.
    If none of the formats match, the function returns `None`.
    """
    for fmt in DATE_FORMATS:
        try:
            date_time = datetime.strptime(dt_str, fmt)
            return date_time
        except ValueError:
            continue
    return None

def read_json_schema_from_url(url):
    """
    Downloads and returns a JSON schema from a given URL.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_concept_type(concept_id):
    """
    Extract the concept type from a given concept ID.
    This is useful for determining the type of concept (e.g., 'collection', 'granule') from its ID.
    """
    return concept_id.startswith("C") and "collection" or "granule"
