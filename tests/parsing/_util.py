from functools import wraps
from pyfactor._parse import parse_refs


def refs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        parsed = parse_refs(source)
        assert len(parsed) == len(expected), 'Wrong number of nodes!'
        for p, e in zip(parsed, expected):
            assert p.name == e[0], f'Wrong name! Expected\n{e}\ngot\n{p}'
            assert p.depends_on == e[1], f'Wrong deps! Expected\n{e}\ngot\n{p}'
    return wrapper
