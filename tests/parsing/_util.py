from functools import wraps
from pyfactor import parse_refs


def refs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, refs = func(self)
        parsed, _ = parse_refs(source)
        assert parsed == refs
    return wrapper
