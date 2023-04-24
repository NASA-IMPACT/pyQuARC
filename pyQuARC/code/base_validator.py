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
    def contains(list_of_values, value):
        return value in list_of_values

    @staticmethod
    def compare(first, second, relation):
        if relation.startswith("not_"):
            return not (BaseValidator.compare(first, second, relation[4:]))
        func = getattr(BaseValidator, relation)
        return func(first, second)
