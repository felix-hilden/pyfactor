import ast

from enum import Enum
from dataclasses import dataclass
from typing import Set, List, Tuple, Generator, Iterable


def multi_union(sets: Iterable[Set]) -> Set:
    """Union of multiple sets."""
    return set().union(*sets)


def collect_names(node: ast.AST) -> Set[str]:
    """Naively collect all names that a node has as children."""
    names = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            names.add(n.id)
    return names


_func_types = (ast.FunctionDef, ast.AsyncFunctionDef)


def node_names(node: ast.AST) -> Set[str]:
    """Generate names that a node is referred to with."""
    if isinstance(node, ast.Assign):
        return multi_union(collect_names(t) for t in node.targets)
    elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return collect_names(node.target)
    elif isinstance(node, _func_types + (ast.ClassDef,)):
        return {node.name}
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        return {n.name if n.asname is None else n.asname for n in node.names}
    else:
        return set()


def collect_args(args: ast.arguments):
    """Collect function arguments."""
    all_args = args.args + args.kwonlyargs
    all_args += [args.vararg, args.kwarg]
    return [arg for arg in all_args if arg is not None]


def _depends_on_recursive(node: ast.AST) -> Tuple[Set[str], Set[str]]:
    """Generate names of children as (potential globals, sure globals)."""
    used = set()
    assigned = set()
    globaled = set()
    nonlocaled = set()

    i = 0
    iterate = []
    recurse = []

    if isinstance(node, (ast.Assign, ast.AugAssign)):
        successors = [node.value]
    elif isinstance(node, ast.AnnAssign):
        successors = [node.annotation, node.value]
    elif isinstance(node, ast.Lambda):
        all_args = collect_args(node.args)
        assigned.update(a.arg for a in all_args)
        successors = [node.body]
    elif isinstance(node, _func_types):
        all_args = collect_args(node.args)
        assigned.update(a.arg for a in all_args)
        annotation_names = (
            collect_names(a.annotation)
            for a in all_args if a.annotation is not None
        )
        globaled.update(multi_union(annotation_names))
        fdef_sources = node.args.kw_defaults + node.args.defaults
        fdef_sources += node.decorator_list + [node.returns]
        fdef_names = (collect_names(d) for d in fdef_sources if d is not None)
        globaled.update(multi_union(fdef_names))
        successors = node.body
    elif isinstance(node, ast.ClassDef):
        cdef_sources = node.bases + node.keywords
        cdef_sources += node.decorator_list
        cdef_names = (collect_names(b) for b in cdef_sources)
        globaled.update(multi_union(cdef_names))
        successors = node.body
    else:
        successors = list(ast.iter_child_nodes(node))

    iterate.extend(successors)

    while i < len(iterate):
        n = iterate[i]
        assigned.update(node_names(n) - used)
        if isinstance(n, ast.Name):
            used.add(n.id)
        elif isinstance(n, ast.Global):
            globaled.update(n.names)
        elif isinstance(n, ast.Nonlocal):
            nonlocaled.update(n.names)
        elif isinstance(n, _func_types + (ast.Lambda, ast.ClassDef)):
            recurse.append(n)
        else:
            iterate[i + 1:i + 1] = list(ast.iter_child_nodes(n))
        i += 1

    inner_potential = set()
    inner_globaled = set()

    for n in recurse:
        potential_, globaled_ = _depends_on_recursive(n)
        inner_potential.update(potential_)
        inner_globaled.update(globaled_)

    # Nonlocaled can be considered "from this scope" because they require
    # an inner function scope, so we don't care about them here
    from_this_scope = (assigned | nonlocaled) - globaled
    if isinstance(node, ast.ClassDef):
        from_outer_scopes = (used - from_this_scope - globaled) | inner_potential
    else:
        from_outer_scopes = (used | inner_potential) - from_this_scope - globaled

    return from_outer_scopes, globaled | inner_globaled


def depends_on(node: ast.AST) -> Set[str]:
    """Generate all names that a node refers to."""
    return multi_union(_depends_on_recursive(node))


class NodeType(Enum):
    """Shorthands for node types."""

    var = 'V'
    func = 'F'
    class_ = 'C'
    import_ = 'I'
    unknown = '?'


@dataclass
class NodeInfo:
    """Source node information."""

    defines: Set[str]
    depends_on: Set[str]
    type: NodeType
    lineno: int


def _get_type(node: ast.AST) -> NodeType:
    """Return format string for displaying a node."""
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return NodeType.var
    elif isinstance(node, _func_types):
        return NodeType.func
    elif isinstance(node, ast.ClassDef):
        return NodeType.class_
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        return NodeType.import_
    else:
        return NodeType.unknown


def _top_nodes(node: ast.AST) -> Generator[ast.AST, None, None]:
    for n in ast.iter_child_nodes(node):
        yield n


def parse_refs(
    source: str,
) -> List[NodeInfo]:
    """Parse a reference array from source."""
    tree = ast.parse(source)
    nodes = [
        NodeInfo(node_names(node), depends_on(node), _get_type(node), node.lineno)
        for node in _top_nodes(tree)
    ]
    defined_names = multi_union(n.defines for n in nodes)
    for node in nodes:
        node.depends_on = node.depends_on.intersection(defined_names)
    return nodes
