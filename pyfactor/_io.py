import graphviz as gv
import networkx as nx

from dataclasses import dataclass
from typing import List
from pathlib import Path
from importlib.util import find_spec

from ._cli import ArgumentError, make_absolute


@dataclass
class Source:
    file: Path
    name: str


def resolve_sources(paths: List[str]) -> List[Source]:
    """Resolve sources from paths and importable modules."""
    singles = []
    packages = []
    importable = []
    for path in paths:
        p = make_absolute(Path(path).resolve())
        if p.is_dir():
            packages.append(p)
        elif p.exists():
            singles.append(p)
        elif find_spec(str(path)):
            importable.append(path)
        else:
            msg = (
                f'Pyfactor: could not find `{path}`! '
                'Expected a file, a directory or an importable package.'
            )
            raise ArgumentError(msg)

    if len(singles) == 0 and len(packages) == 1:
        if not (packages[0] / '__init__.py').exists():
            folder = packages[0]
            singles = list(folder.glob('*.py'))
            packages = [path.parent for path in folder.glob('*/__init__.py')]

    local_sources = singles + packages
    if not all(p.parent == local_sources[0].parent for p in local_sources[1:]):
        raise ArgumentError('Pyfactor: sources are in different directories!')

    packages.extend([find_spec(i).submodule_search_locations for i in importable])
    sources = [Source(s, s.stem) for s in singles]
    for package in packages:
        for path in package.glob('**/*.py'):
            if not path.with_name('__init__.py').exists():
                continue
            rel = path.relative_to(package.parent)
            if path.stem == '__init__':
                name = '.'.join(rel.parent.parts)
            else:
                name = '.'.join(rel.with_suffix('').parts)
            sources.append(Source(path, name))
    return sources


def read_source(path: Path) -> str:
    """Read Python source code with 'utf-8' encoding."""
    return path.read_text(encoding='utf-8')


def write_graph(graph: nx.DiGraph, path: str) -> None:
    """Write NetworkX graph to Graphviz graph file."""
    nx.nx_pydot.write_dot(graph, path)


def read_graph(path: str) -> gv.Source:
    """
    Read graph file.

    Parameters
    ----------
    path
        path to graph file to read
    """
    return gv.Source.from_file(path)
