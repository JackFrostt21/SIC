from icecream import ic


def decorator_debug(func):
    """
    Function for DEBUG testing
    """

    def wrapper(*args, **kwargs):
        ic(f'{func.__name__}')
        ic(f'{args=}, {kwargs=}')
        result = func(*args, **kwargs)
        ic(f'Func return: {result}')
        return result

    return wrapper
