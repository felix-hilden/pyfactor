import ast

from enum import Enum
from dataclasses import dataclass
from typing import Set, List, Tuple, Iterable, Optional


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


class NodeType(Enum):
    """Shorthands for node types."""

    var = 'V'
    func = 'F'
    class_ = 'C'
    import_ = 'I'
    unknown = '?'


@dataclass
class Node:
    """Source node information."""

    name: str
    depends_on: set = None
    type: NodeType = None
    lineno: int = None

    def __post_init__(self):
        """Ensure depends_on is a set."""
        self.depends_on = self.depends_on or set()


def target_component_names(node: ast.AST) -> Optional[Node]:
    """Generate name for an assign target component."""
    if isinstance(node, ast.Name):
        return Node(node.id)
    elif isinstance(node, ast.Starred):
        if isinstance(node.value, ast.Name):
            return Node(node.value.id)


def targets_names(targets: List[ast.AST]) -> List[Node]:
    """Generate names for assign targets."""
    target_list = []
    for t in targets:
        if isinstance(t, (ast.List, ast.Tuple)):
            target_list.extend(t.elts)
        else:
            target_list.append(t)

    comps = [target_component_names(t) for t in target_list]
    return [n for n in comps if n is not None]


def node_names(node: ast.AST) -> List[Node]:
    """Generate names of a node and their extra dependencies."""
    if isinstance(node, ast.Assign):
        return targets_names(node.targets)
    elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return targets_names([node.target])
    elif isinstance(node, _func_types + (ast.ClassDef,)):
        return [Node(node.name)]
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        names = [n.name if n.asname is None else n.asname for n in node.names]
        return [Node(n) for n in names]
    else:
        return []


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
        node_assigns = {d.name for d in node_names(n)}
        assigned.update(node_assigns - used)
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


def get_type(node: ast.AST) -> NodeType:
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


def parse_nodes(root: ast.AST) -> List[Node]:
    """Generate nodes and information under root."""
    nodes = []
    for node in ast.iter_child_nodes(root):
        new_nodes = node_names(node)
        deps = depends_on(node)
        n_type = get_type(node)
        for n in new_nodes:
            n.depends_on.update(deps)
            n.type = n_type
            n.lineno = node.lineno
        nodes.extend(new_nodes)
    return nodes


def parse_refs(
    source: str,
) -> List[Node]:
    """Parse a reference array from source."""
    tree = ast.parse(source)
    nodes = parse_nodes(tree)
    defined_names = {n.name for n in nodes}
    for node in nodes:
        node.depends_on = node.depends_on.intersection(defined_names)
    return nodes
