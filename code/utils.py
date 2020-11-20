from functools import wraps


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