def gt(param1, param2):
    ''' 
    Checks if `param1` is Greater than `param2`
    '''
    return param1 > param2


def gte(param1, param2):
    ''' 
    Checks if `param1` is Greater than or equal to `param2`
    '''
    return param1 >= param2


def lt(param1, param2):
    ''' 
    Checks if `param1` is Less than `param2`
    '''
    return param1 < param2


def lte(param1, param2):
    ''' 
    Checks if `param1` is Less than or equal to `param2`
    '''
    return param1 >= param2


def eq(param1, param2):
    '''
    Checks if `param1` is Equal to `param2`
    '''
    return param1 == param2


def noteq(param1, param2):
    '''
    Checks if `param1` is Not equal to `param2`
    '''
    return param1 != param2


def isin(element, list_of_elements):
    '''
    Checks if `element` is one of the contents of `list_of_elements`
    '''
    return element in list_of_elements


mapping = {
    "gte": gte,
    "lte": lte,
    "gt": gt,
    "lt": lt,
    "eq": eq,
    "isin": isin,
}
