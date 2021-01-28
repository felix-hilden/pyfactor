import networkx as nx
import graphviz as gv

from enum import Enum
from typing import List
from ._parse import NodeInfo, NodeType


class ConnectivityColor(Enum):
    """Colors for node connectivity degrees."""

    default = '#FFFFFF'
    isolated = '#E5E5E5'
    root = '#BBEEFF'
    leaf = '#E4FFE4'


type_shape = {
    NodeType.var: 'box',
    NodeType.func: 'ellipse',
    NodeType.class_: 'parallelogram',
    NodeType.import_: 'note',
    NodeType.unknown: 'ellipse',
}
centrality_color = {
    0.997: '#FF3030',
    0.95: '#FFA0A0',
    0.68: '#FFE0E0',
}


def create_legend() -> gv.Source:
    """Create legend source."""
    graph = gv.Digraph()

    with graph.subgraph(name='cluster1') as s:
        s.attr(label='Types')
        s.node_attr.update(style='filled', fillcolor='#FFFFFF')
        s.node('variable', shape=type_shape[NodeType.var])
        s.node('function', shape=type_shape[NodeType.func])
        s.node('class', shape=type_shape[NodeType.class_])
        s.node('import', shape=type_shape[NodeType.import_])

    with graph.subgraph(name='cluster2') as s:
        s.attr(label='Colours')
        s.node_attr.update(style='filled')
        for e in ConnectivityColor:
            s.node(e.name, fillcolor=e.value)
        for deg, col in centrality_color.items():
            s.node(f'Centrality {deg}', fillcolor=col)

    return gv.Source(graph.source)


def create_graph(
    nodes: List[NodeInfo],
    skip_imports: bool = False,
    exclude: List[str] = None,
) -> nx.DiGraph:
    """Create and populate a graph from references."""
    exclude = set(exclude or [])
    graph = nx.DiGraph()
    for node in nodes:
        for name in node.defines:
            graph.add_node(
                name,
                label=f'{name.center(12, " ")}\n{node.type.value}:{node.lineno}',
                shape=type_shape[node.type],
                style='filled',
                fillcolor='#FFFFFF'
            )
            graph.add_edges_from([
                (name, d) for d in node.depends_on
            ])

    for node in nodes:
        if skip_imports and node.type == NodeType.import_:
            graph.remove_nodes_from(node.defines)
        for name in node.defines:
            if name in exclude:
                graph.remove_node(name)

    in_degs = []
    out_degs = []
    for node in graph.nodes:
        in_deg = graph.in_degree(node)
        out_deg = graph.out_degree(node)
        in_degs.append(in_deg)
        out_degs.append(out_deg)

        if in_deg == 0 and out_deg == 0:
            fill = ConnectivityColor.isolated
        elif in_deg == 0:
            fill = ConnectivityColor.root
        elif out_deg == 0:
            fill = ConnectivityColor.leaf
        else:
            fill = ConnectivityColor.default
        graph.nodes[node]['fillcolor'] = fill.value

    centralities = sorted(i + o for i, o in zip(in_degs, out_degs))

    for node in graph.nodes:
        c = graph.in_degree(node) + graph.out_degree(node)
        central = sum(c > ct for ct in centralities) / len(centralities)
        for level, color in centrality_color.items():
            if central > level:
                graph.nodes[node]['fillcolor'] = color
                break

    return graph


def preprocess(
    source: gv.Source,
    stagger: int = None,
    fanout: bool = False,
    chain: int = None,
) -> gv.Source:
    """
    Preprocess source for rendering.

    Parameters
    ----------
    source
        Graphviz source to preprocess
    stagger
        maximum Graphviz unflatten stagger
    fanout
        enable Graphviz unflatten fanout
    chain
        maximum Graphviz unflatten chain
    """
    return source.unflatten(stagger=stagger, fanout=fanout, chain=chain)


def render(
    source: gv.Source,
    out_path: str,
    format: str = None,
    engine: str = None,
    renderer: str = None,
    formatter: str = None,
    view: bool = False,
) -> None:
    """
    Render source with Graphviz.

    Parameters
    ----------
    source
        Graphviz source to render
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
    if engine is not None:
        source.engine = engine
    source.render(
        out_path,
        format=format,
        renderer=renderer,
        formatter=formatter,
        view=view,
        cleanup=True,
    )
