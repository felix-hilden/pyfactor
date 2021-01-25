import graphviz as gv
import networkx as nx

from pathlib import Path


def read_source(path: str) -> str:
    """Read Python source code with 'utf-8' encoding."""
    return Path(path).read_text(encoding='utf-8')


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
