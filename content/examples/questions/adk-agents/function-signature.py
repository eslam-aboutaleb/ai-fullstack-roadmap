import inspect
from functools import wraps
def instrument(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapped
@instrument
def read_policy(document_id: str) -> str:
    return document_id
print(inspect.signature(read_policy), read_policy('P1'))
