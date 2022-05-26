import requests

from .constants import CMR_URL


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
        return first != second

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

    @staticmethod
    def cmr_request(cmr_prms):
        return requests.get(f'{CMR_URL}/search/{cmr_prms}')
    
