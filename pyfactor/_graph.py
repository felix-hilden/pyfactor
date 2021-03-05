import ast

import networkx as nx
import graphviz as gv

from dataclasses import dataclass
from enum import Enum
from textwrap import dedent
from typing import List, Dict, Set, Optional
from ._visit import Line


class NodeType(Enum):
    """Shorthands for node types."""

    var = 'V'
    func = 'F'
    class_ = 'C'
    import_ = 'I'
    unknown = '?'
    multiple = '+'


def get_type(node: ast.AST) -> NodeType:
    """Determine general type of AST node."""
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return NodeType.var
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return NodeType.func
    elif isinstance(node, ast.ClassDef):
        return NodeType.class_
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        return NodeType.import_
    else:
        return NodeType.unknown


@dataclass
class GraphNode:
    name: str
    deps: Set[str]
    type: NodeType
    lineno_str: str
    docstring: Optional[str]


def merge_nodes(lines: List[Line]) -> List[GraphNode]:
    """Merge name definitions and references on lines to unique graph nodes."""
    nodes = {}
    for line in lines:
        for name in line.names:
            node = GraphNode(
                name.name,
                name.deps,
                get_type(line.ast_node),
                str(line.ast_node.lineno),
                line.docstring,
            )
            if node.name not in nodes:
                nodes[node.name] = [node, name.is_definition]
            else:
                merge = nodes[node.name][0]
                was_defined = nodes[node.name][1]

                merge.deps = merge.deps | node.deps
                merge.lineno_str += ',' + node.lineno_str
                if merge.type != node.type and name.is_definition and was_defined:
                    merge.type = NodeType.multiple
                if name.is_definition:
                    nodes[node.name][1] = True

    return [node for node, _ in nodes.values()]


class MiscColor(Enum):
    """Colors for miscellaneous attributes."""

    bridge = '#990000'


class ConnectivityColor(Enum):
    """Colors for node connectivity degrees."""

    default = '#FFFFFF'
    isolated = '#E5E5E5'
    root = '#BBEEFF'
    leaf = '#E4FFE4'
    waypoint = '#EFC4FF'


type_shape = {
    NodeType.var: 'box',
    NodeType.func: 'ellipse',
    NodeType.class_: 'parallelogram',
    NodeType.import_: 'note',
    NodeType.unknown: 'ellipse',
    NodeType.multiple: 'ellipse',
}
centrality_color = {
    0.997: '#FF3030',
    0.95: '#FFA0A0',
    0.68: '#FFE0E0',
}
node_prefix = 'pf-'


def create_legend() -> gv.Source:
    """Create legend source."""
    graph = gv.Digraph()

    with graph.subgraph(name='cluster1') as s:
        s.attr(label='Types')
        s.node_attr.update(style='filled', fillcolor='#FFFFFF')
        types = [
            ('variable', NodeType.var),
            ('function', NodeType.func),
            ('class', NodeType.class_),
            ('import', NodeType.import_),
            ('unknown', NodeType.unknown),
            ('multiple', NodeType.multiple),
        ]
        for name, t in types:
            s.node(f'{name} ({t.value})', shape=type_shape[t])

    with graph.subgraph(name='cluster2') as s:
        s.attr(label='Colours')
        s.node_attr.update(style='filled')
        for e in ConnectivityColor:
            s.node(e.name, fillcolor=e.value)
        for deg, col in centrality_color.items():
            s.node(f'Centrality {deg}', fillcolor=col)
        s.node('conn1', label=' ')
        s.node('conn2', label=' ')
        s.edge('conn1', 'conn2', label='dependency')
        s.node('bridge1', label=' ')
        s.node('bridge2', label=' ')
        s.edge('bridge1', 'bridge2', label='bridge', color=MiscColor.bridge.value)
        s.node(
            'collapsed', peripheries='2', fillcolor=ConnectivityColor.waypoint.value
        )

    return gv.Source(graph.source)


def append_color(node, color: str) -> None:
    """Append or replace default color."""
    if node['fillcolor'] != ConnectivityColor.default.value:
        node['fillcolor'] = node['fillcolor'] + ';0.5:' + color
        node['gradientangle'] = 305
    else:
        node['fillcolor'] = color


def create_graph(
    lines: List[Line],
    skip_imports: bool = False,
    exclude: List[str] = None,
    collapse_waypoints: bool = False,
    collapse_exclude: List[str] = None,
    graph_attrs: Dict[str, str] = None,
    node_attrs: Dict[str, str] = None,
    edge_attrs: Dict[str, str] = None,
) -> nx.DiGraph:
    """Create and populate a graph from references."""
    exclude = set(exclude or [])
    collapse_exclude = set(collapse_exclude or [])
    graph_attrs = graph_attrs or {}
    node_attrs = node_attrs or {}
    edge_attrs = edge_attrs or {}
    nodes = merge_nodes(lines)
    graph = nx.DiGraph(**graph_attrs)
    for node in nodes:
        name = node.name.center(12, " ")
        attrs = {
            'label': f'{name}\n{node.type.value}:{node.lineno_str}',
            'shape': type_shape[node.type],
            'style': 'filled',
            'tooltip': dedent(node.docstring or f'{node.name} - no docstring'),
        }
        node_attrs.update(attrs)
        graph.add_node(node_prefix + node.name, **node_attrs)
        graph.add_edges_from([
            (node_prefix + node.name, node_prefix + d) for d in node.deps
        ], **edge_attrs)

    for node in nodes:
        if skip_imports and node.type == NodeType.import_ or node.name in exclude:
            graph.remove_node(node_prefix + node.name)

    conn = {}
    for node in graph.nodes:
        in_deg = len([0 for u, v in graph.in_edges(node) if u != node])
        out_deg = len([0 for u, v in graph.out_edges(node) if v != node])
        conn[node] = (in_deg, out_deg)

        if in_deg == 0 and out_deg == 0:
            fill = ConnectivityColor.isolated
        elif in_deg == 0:
            fill = ConnectivityColor.root
        elif out_deg == 0:
            fill = ConnectivityColor.leaf
        else:
            fill = ConnectivityColor.default
        graph.nodes[node]['fillcolor'] = fill.value

    centralities = sorted(i + o for i, o in conn.values())

    for node in graph.nodes:
        c = conn[node][0] + conn[node][1]
        central = sum(c > ct for ct in centralities) / len(centralities)
        for level, color in centrality_color.items():
            if central > level:
                append_color(graph.nodes[node], color)
                break

    undirected = graph.to_undirected()
    bridge = MiscColor.bridge.value
    for from_, to in nx.bridges(undirected):
        if not graph.has_edge(from_, to):
            from_, to = to, from_
        graph.edges[from_, to]['color'] = bridge

    i = -1
    graph_nodes = list(graph.nodes)
    removed_nodes = set()
    while i + 1 < len(graph_nodes):
        i += 1
        node = graph_nodes[i]

        if node in removed_nodes or conn[node][0] == 0 or conn[node][1] == 0:
            continue

        undirected = graph.to_undirected()
        undirected.remove_node(node)
        components = list(nx.connected_components(undirected))

        in_nodes = {u for u, _ in graph.in_edges(node) if u != node}
        out_nodes = {v for _, v in graph.out_edges(node) if v != node}
        for comp in components:
            if len(comp & in_nodes) and len(comp & out_nodes):
                break
        else:
            append_color(graph.nodes[node], ConnectivityColor.waypoint.value)
            if collapse_waypoints and node[len(node_prefix):] not in collapse_exclude:
                graph.nodes[node]['peripheries'] = 2
                for comp in components:
                    if len(comp & out_nodes):
                        removed_nodes = removed_nodes | comp
                        graph.remove_nodes_from(comp)
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
