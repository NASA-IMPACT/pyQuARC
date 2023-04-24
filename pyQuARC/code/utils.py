import os
import requests
import urllib

from functools import wraps

from .constants import CMR_URL


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
