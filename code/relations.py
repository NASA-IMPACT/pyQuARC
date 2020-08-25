def gt(param1, param2):
    return param1 > param2


def gte(param1, param2):
    return param1 >= param2


def lte(param1, param2):
    return param1 >= param2


def lt(param1, param2):
    return param1 < param2


def eq(param1, param2):
    return param1 == param2


def noteq(param1, param2):
    return param1 != param2


def isin(element, list_of_elements):
    return element in list_of_elements


mapping = {
    "gte": gte,
    "lte": lte,
    "gt": gt,
    "lt": lt,
    "eq": eq,
    "isin": isin,
}
