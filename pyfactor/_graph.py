from typing import List, Tuple, Set
from graphviz import Digraph


def create_graph(
    references: List[Tuple[Set[str], Set[str]]],
    display_formats: List[str],
) -> Digraph:
    """Create and populate a graph from references."""
    graph = Digraph()
    for (names, refs), fmt in zip(references, display_formats):
        for name in names:
            graph.node(name, label=fmt.format(name))
            graph.edges([
                (name, ref) for ref in refs
            ])
    return graph
