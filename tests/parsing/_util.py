from functools import wraps
from pathlib import Path
from pyfactor._visit import parse_lines
from pyfactor._io import Source


def parse(source: str):
    lines = parse_lines(Source(Path('./nonfile'), '', source))
    return [name for line in lines for name in line.names]


def refs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        nodes = parse(source)
        assert len(nodes) == len(expected), 'Wrong number of nodes!'
        for n, e in zip(nodes, expected):
            assert n.name == e[0], f'Wrong name! Expected\n{e}\ngot\n{n}'
            assert n.deps == e[1], f'Wrong deps! Expected\n{e}\ngot\n{n}'
    return wrapper


def refs_in(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        nodes = parse(source)
        assert len(nodes) == len(expected), 'Wrong number of nodes!'
        for n in nodes:
            if (n.name, n.deps) not in expected:
                raise AssertionError(
                    f'Missing node! Parsed\n{n.name} with deps: {n.deps}'
                )
    return wrapper


def docs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        lines = parse_lines(Source(Path('./nonfile'), '', source))
        docs = [line.docstring for line in lines]
        assert len(docs) == len(expected), (
            f'Wrong number of docs! Expected\n{expected}\ngot\n{docs}'
        )
        for d, e in zip(docs, expected):
            err = f'Wrong doc! Expected\n{e}\ngot\n{d}'
            assert d == e or d is None and e is None, err
    return wrapper


def import_equal(func):
    @wraps(func)
    def wrapper(self):
        source, expected = func(self)
        nodes = parse(source)
        assert len(nodes) == len(expected), 'Wrong number of nodes!'
        for n, e in zip(nodes, expected):
            assert n.name == e[0], f'Wrong name! Expected\n{e}\ngot\n{n}'
            assert n.source == e[1], f'Wrong source! Expected\n{e}\ngot\n{n}'
    return wrapper
