from functools import wraps
from pyfactor._parse import parse_refs


def refs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        parsed = parse_refs(source)
        for e, p in zip(expected, parsed):
            assert p.defines == e[0], 'Mismatch in defines!'
            assert p.depends_on == e[1], 'Mismatch in depends!'
    return wrapper
