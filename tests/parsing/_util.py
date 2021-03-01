from functools import wraps
from pyfactor._visit import parse_lines


def refs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        lines = parse_lines(source)
        nodes = [name for line in lines for name in line.names]
        assert len(nodes) == len(expected), 'Wrong number of nodes!'
        for n, e in zip(nodes, expected):
            assert n.name == e[0], f'Wrong name! Expected\n{e}\ngot\n{n}'
            assert n.deps == e[1], f'Wrong deps! Expected\n{e}\ngot\n{n}'
    return wrapper


def refs_in(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        lines = parse_lines(source)
        nodes = [name for line in lines for name in line.names]
        assert len(nodes) == len(expected), 'Wrong number of nodes!'
        for n in nodes:
            if (n.name, n.deps) not in expected:
                raise AssertionError(
                    f'Missing node! Parsed\n{n.name} with deps: {n.deps}'
                )
    return wrapper
