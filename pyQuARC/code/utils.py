import os
import requests

from functools import wraps

from .constants import CMR_URL


def if_arg(func):
    @wraps(func)
    def run_function_only_if_arg(*args):
        if args[0]:
            return func(*args)
        else:
            return {
                "valid": None,
                "value": None
            }
    return run_function_only_if_arg

def _add_protocol(url):
    if not url.startswith("http"):
        url = f"https://{url}"
    return url

def is_valid_cmr_url(url):
    url = _add_protocol(url)
    valid = False
    try: # some invalid url throw an exception
        response = requests.get(url, timeout=5) # some invalid urls freeze
        if response.status_code == 200 and response.headers.get("CMR-Request-Id"):
            valid = True
        else:
            valid = False
    except:
        valid = False
    return valid

def get_cmr_url():
    cmr_url = os.environ.get("CMR_URL", CMR_URL)
    return _add_protocol(cmr_url)
