import ast

import networkx as nx
import graphviz as gv

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from textwrap import dedent
from warnings import warn
from typing import List, Dict, Set, Optional, Tuple
from ._visit import Line
from ._io import Source
from ._cli import ArgumentError


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
    import_sources: Set[str]


def resolve_import(import_: str, location: str, file: Path) -> str:
    """Resolve potentially relative import inside a package."""
    if not import_.startswith('.'):
        return import_

    import_parts = import_.split('.')
    up_levels = len([p for p in import_parts if p == ''])
    import_down = import_parts[up_levels:]

    if file.stem == '__init__':
        up_levels -= 1
    location_parts = location.split('.')

    # up_levels can be 0
    location_parts = location_parts[:-up_levels or None]
    return '.'.join(location_parts + import_down)


def merge_nodes(location: str, file: Path, lines: List[Line]) -> List[GraphNode]:
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
                set(),
            )
            if name.source:
                node.import_sources.add(
                    resolve_import(name.source, location, file)
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
                merge.import_sources = merge.import_sources | node.import_sources

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


def create_legend() -> gv.Source:
    """Create legend source."""
    graph = gv.Digraph()

    with graph.subgraph(name='cluster1') as s:
        s.attr(label='Node shapes')
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
        s.attr(label='Node colours')
        s.node_attr.update(style='filled')
        for e in ConnectivityColor:
            s.node(e.name, fillcolor=e.value)
        for deg, col in centrality_color.items():
            s.node(f'Centrality {deg}', fillcolor=col)
        s.node(
            'collapsed', peripheries='2', fillcolor=ConnectivityColor.waypoint.value
        )

    with graph.subgraph(name='cluster3') as s:
        s.node_attr.update(style='filled')
        s.attr(label='Edge styles')
        s.node('conn1', label=' ')
        s.node('conn2', label=' ')
        s.edge('conn1', 'conn2', label='  default')
        s.node('bridge1', label=' ')
        s.node('bridge2', label=' ')
        s.edge('bridge1', 'bridge2', label='  bridge', color=MiscColor.bridge.value)
        s.node('imp1', label=' ')
        s.node('imp2', label=' ')
        s.edge('imp1', 'imp2', label='  import', style='dashed')

    return gv.Source(graph.source)


def append_color(node, color: str) -> None:
    """Append or replace default color."""
    if node['fillcolor'] != ConnectivityColor.default.value:
        node['fillcolor'] = node['fillcolor'] + ';0.5:' + color
        node['gradientangle'] = '305'
    else:
        node['fillcolor'] = color


class MissingNode(RuntimeWarning):
    """Node could not be found."""


class AmbiguousNode(RuntimeWarning):
    """Node could not be determined unambiguously."""


def guess_node(graph: nx.Graph, ref: str) -> Optional[str]:
    """Determine an unambiguous node that ref refers to, or return None."""
    potential = {node for node in graph.nodes if node.endswith(ref)}
    if len(potential) == 1:
        return potential.pop()
    elif len(potential) == 0:
        msg = f'Node `{ref}` could not be found!'
        cls = MissingNode
    else:
        msg = f'Reference to `{ref}` is ambiguous!'
        cls = AmbiguousNode
    warn(msg, cls, stacklevel=4)


cluster_invis_node = 'cluster-invis-node'


def gen_cluster_nodes(graph: nx.DiGraph, levels: str) -> None:
    """Generate invis cluster nodes."""
    parts = levels.split()
    for i in range(len(parts)):
        level = '.'.join(parts[:i + 1])
        node = level + '.' + cluster_invis_node
        if not graph.has_node(node):
            graph.add_node(node, shape='point', style='invis')


def create_graph(
    sources: List[Tuple[Source, List[Line]]],
    skip_external: bool = False,
    imports: str = 'interface',
    exclude: List[str] = None,
    root: str = None,
    collapse_waypoints: bool = False,
    collapse_exclude: List[str] = None,
    graph_attrs: Dict[str, str] = None,
    node_attrs: Dict[str, str] = None,
    edge_attrs: Dict[str, str] = None,
) -> gv.Digraph:
    """Create and populate a graph from references."""
    exclude = set(exclude or [])
    collapse_exclude = set(collapse_exclude or [])
    graph_attrs = graph_attrs or {}
    node_attrs = node_attrs or {}
    edge_attrs = edge_attrs or {}
    graph_attrs.update({
        'compound': 'true',
        'newrank': 'true',
        'mclimit': '10.0',
        'searchsize': '300',
    })

    graph = nx.DiGraph()
    prefix_nodes = {
        s.name + '.': merge_nodes(s.name, s.file, ln) for s, ln in sources
    }
    for prefix, nodes in prefix_nodes.items():
        for node in nodes:
            name = node.name.center(12, ' ')
            doc = node.docstring or f'{node.name} - no docstring'
            doc = dedent(doc).replace('\n', '\\n')
            attrs = {
                'label': f'{name}\\n{node.type.value}:{node.lineno_str}',
                'shape': type_shape[node.type],
                'style': 'filled',
                'tooltip': doc,
            }
            n_attrs = node_attrs.copy()
            n_attrs.update(attrs)
            graph.add_node(prefix + node.name, **n_attrs)
            graph.add_edges_from([
                (prefix + node.name, prefix + d) for d in node.deps
            ], **edge_attrs)
        gen_cluster_nodes(graph, prefix[:-1])

    import_sources = set()
    for _, nodes in prefix_nodes.items():
        for node in nodes:
            import_sources.update(node.import_sources)
    for source in import_sources:
        if '.' in source:
            source = '.'.join(source.split('.')[:-1])
        gen_cluster_nodes(graph, source)

    for prefix, nodes in prefix_nodes.items():
        for node in nodes:
            if not node.import_sources:
                continue
            for s in node.import_sources:
                e_attrs = edge_attrs.copy()
                e_attrs['style'] = 'dashed'
                if graph.has_node(s + '.' + cluster_invis_node):
                    e_attrs.update({'lhead': 'cluster_' + s})
                    graph.add_edge(
                        prefix + node.name, s + '.' + cluster_invis_node, **e_attrs
                    )
                    continue

                if not graph.has_node(s):
                    graph.add_node(
                        s, label=s.split('.')[-1], shape=type_shape[NodeType.import_]
                    )
                graph.add_edge(prefix + node.name, s, **e_attrs)

    for name in exclude:
        resolved = guess_node(graph, name)
        if resolved:
            graph.remove_node(resolved)

    if skip_external:
        internal = {p.split('.')[0] for p in prefix_nodes.keys()}
        removed = set()
        for node, data in graph.nodes.items():
            if not data['shape'] == type_shape[NodeType.import_]:
                continue
            if all(v.split('.')[0] not in internal for _, v in graph.out_edges(node)):
                removed.add(node)
        graph.remove_nodes_from(removed)

        removed = set()
        for node in graph.nodes:
            if node.split('.')[0] not in internal:
                removed.add(node)
        graph.remove_nodes_from(removed)

    if imports == 'duplicate':
        pass
    elif imports in ('resolve', 'interface'):
        removed = set()
        for node, data in graph.nodes.items():
            if not data['shape'] == type_shape[NodeType.import_]:
                continue

            out_edges = [(v, d) for _, v, d in graph.out_edges(node, data=True)]
            if len(out_edges) != 1:
                continue
            out_edge, data = out_edges[0]

            if imports == 'interface':
                location = '.'.join(node.split('.')[:-1])
                target = out_edge.replace('.' + cluster_invis_node, '')
                if location in out_edge and node != target:
                    continue

            in_edges = [(u, d) for u, _, d in graph.in_edges(node, data=True)]
            for in_edge, d in in_edges:
                attrs = d.copy()
                attrs.update(**data)
                graph.add_edge(in_edge, out_edge, **attrs)
            removed.add(node)
        graph.remove_nodes_from(removed)
    else:
        raise ArgumentError(f'Pyfactor: invalid imports mode `{imports}`!')

    conn = {}
    for node in graph.nodes:
        in_deg = len([0 for u, v in graph.in_edges(node) if u != node])
        out_deg = len([0 for u, v in graph.out_edges(node) if v != node])
        conn[node] = (in_deg, out_deg)

    centralities = sorted(i + o for i, o in conn.values())

    for node in graph.nodes:
        in_deg, out_deg = conn[node]

        if in_deg == 0 and out_deg == 0:
            fill = ConnectivityColor.isolated
        elif in_deg == 0:
            fill = ConnectivityColor.root
        elif out_deg == 0:
            fill = ConnectivityColor.leaf
        else:
            fill = ConnectivityColor.default
        graph.nodes[node]['fillcolor'] = fill.value

        c = in_deg + out_deg
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
    collapse_exclude = {guess_node(graph, n) for n in collapse_exclude}
    collapse_exclude = {n for n in collapse_exclude if n is not None}
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
            if collapse_waypoints and node not in collapse_exclude:
                graph.nodes[node]['peripheries'] = 2
                for comp in components:
                    if len(comp & out_nodes):
                        removed_nodes = removed_nodes | comp
                        graph.remove_nodes_from(comp)

    if root:
        root_ref = guess_node(graph, root)
        if root_ref:
            done = set()
            potential = {root_ref}
            while potential:
                n = potential.pop()
                done.add(n)
                succ = graph.successors(n)
                potential.update({s for s in succ if s not in done})
            graph = graph.subgraph(done)

    # Construct module hierarchy
    hierarchy = Level({}, {})
    for node, data in graph.nodes.items():
        parts = node.split('.')
        tmp = hierarchy
        for part in parts[:-1]:
            if part not in tmp.sub:
                tmp.sub[part] = Level({}, {})
            tmp = tmp.sub[part]
        tmp.names[parts[-1]] = data

    gv_graph = gv.Digraph()
    gv_graph.attr(**graph_attrs)
    make_subgraphs(gv_graph, hierarchy, [])
    for from_, to, data in graph.edges.data():
        gv_graph.edge(from_, to, **data)
    return gv_graph


@dataclass
class Level:
    """Subgraph level."""

    sub: Dict[str, 'Level']
    names: Dict[str, Dict]


def make_subgraphs(
    graph: gv.Digraph, hierarchy: Level, location: List
) -> None:
    """Recursively construct subgraph hierarchy."""
    for name, data in hierarchy.names.items():
        graph.node('.'.join(location + [name]), **data)

    for name, sub in hierarchy.sub.items():
        new_loc = location + [name]
        loc_str = '.'.join(new_loc)
        name = 'cluster_' + loc_str
        attrs = {
            'label': loc_str.center(12, ' '), 'fontsize': '22.0', 'penwidth': '2.5'
        }
        with graph.subgraph(name=name, graph_attr=attrs) as subgraph:
            make_subgraphs(subgraph, sub, new_loc)


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
    image_bytes = gv.pipe(
        engine or source.engine,
        format,
        str(source).encode(),
        renderer=renderer,
        formatter=formatter,
    )
    out_path = Path(out_path).with_suffix('.' + format)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)
    if view:
        gv.view(str(out_path))
