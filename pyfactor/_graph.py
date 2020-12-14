import networkx as nx
import graphviz as gv

from typing import List, Tuple, Set
from ._parse import NodeInfo, NodeType

type_shape = {
    NodeType.var: 'box',
    NodeType.func: 'ellipse',
    NodeType.class_: 'parallelogram',
    NodeType.import_: 'note',
    NodeType.unknown: 'ellipse',
}
centrality_level = {
    0.997: '#FF3030',
    0.95: '#FFA0A0',
    0.68: '#FFE0E0',
}


def create_graph(
    references: List[Tuple[Set[str], Set[str]]],
    infos: List[NodeInfo],
) -> nx.DiGraph:
    """Create and populate a graph from references."""
    graph = nx.DiGraph()
    for (names, refs), info in zip(references, infos):
        for name in names:
            graph.add_node(
                name,
                label=f'{name}\n{info.type.value}:{info.lineno}',
                shape=type_shape[info.type],
                style='filled',
                fillcolor='#FFFFFF'
            )
            graph.add_edges_from([
                (name, ref) for ref in refs
            ])
    in_degs = []
    out_degs = []
    for node in graph.nodes:
        in_deg = graph.in_degree(node)
        out_deg = graph.out_degree(node)
        in_degs.append(in_deg)
        out_degs.append(out_deg)

        if in_deg == 0 and out_deg == 0:
            fill = '#E5E5E5'
        elif in_deg == 0:
            fill = '#BBEEFF'
        elif out_deg == 0:
            fill = '#E4FFE4'
        else:
            continue
        graph.nodes[node]['fillcolor'] = fill

    centralities = sorted(i + o for i, o in zip(in_degs, out_degs))

    for node in graph.nodes:
        c = graph.in_degree(node) + graph.out_degree(node)
        central = sum(c > ct for ct in centralities) / len(centralities)
        for level, color in centrality_level.items():
            if central > level:
                graph.nodes[node]['fillcolor'] = color
                break

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
