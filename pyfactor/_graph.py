import networkx as nx
import graphviz as gv

from typing import List, Tuple, Set


def create_graph(
    references: List[Tuple[Set[str], Set[str]]],
    display_formats: List[str],
) -> nx.DiGraph:
    """Create and populate a graph from references."""
    graph = nx.DiGraph()
    for (names, refs), fmt in zip(references, display_formats):
        for name in names:
            graph.add_node(name, label=fmt.format(name))
            graph.add_edges_from([
                (name, ref) for ref in refs
            ])
    return graph


def write_graph(graph: nx.DiGraph, path: str) -> None:
    """Write NetworkX graph to Graphviz graph file."""
    nx.nx_pydot.write_dot(graph, path)


def render(
    graph_path: str,
    out_path: str,
    format: str = None,
    engine: str = None,
    renderer: str = None,
    formatter: str = None,
    view: bool = False,
) -> None:
    """
    Read graph file and render with Graphviz.

    Parameters
    ----------
    graph_path
        path to graph file to read
    out_path
        path to visualisation file to write
    format
        Graphviz render file format
    engine
        Graphviz layout engine
    renderer
        Graphviz output renderer
    formatter
        Graphviz output formatter
    view
        after rendering, display with the default application
    """
    source = gv.Source.from_file(graph_path, engine=engine, format=format)
    source.render(
        out_path, renderer=renderer, formatter=formatter, view=view, cleanup=True
    )
