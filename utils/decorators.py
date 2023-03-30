from typing import Callable
from types import GeneratorType
from functools import wraps


def listify(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        r = func(*args, **kwargs)
        if isinstance(r, GeneratorType):
            return list(r)
        else:
            return r

    return new_func
