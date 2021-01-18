import ast

from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Set, List, Tuple, Generator, Iterable


def read_source(path: str) -> str:
    """Read Python source code with 'utf-8' encoding."""
    return Path(path).read_text(encoding='utf-8')


def _multi_union(sets: Iterable[Set]) -> Set:
    """Union of multiple sets."""
    return set().union(*sets)


def _collect_names(node: ast.AST) -> Set[str]:
    """Naively collect all names that a node has as children."""
    names = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            names.add(n.id)
    return names


_func_types = (ast.FunctionDef, ast.AsyncFunctionDef)


def _node_names(node: ast.AST) -> Set[str]:
    """Generate names that a node is referred to with."""
    if isinstance(node, ast.Assign):
        return _multi_union(_collect_names(t) for t in node.targets)
    elif isinstance(node, _func_types + (ast.ClassDef,)):
        return {node.name}
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        return {n.name if n.asname is None else n.asname for n in node.names}
    else:
        return set()


def _collect_args(args: ast.arguments):
    """Collect function arguments."""
    all_args = args.args + args.kwonlyargs
    all_args += [args.vararg, args.kwarg]
    return [arg for arg in all_args if arg is not None]


def _node_refs_recursive(node: ast.AST) -> Tuple[Set[str], Set[str]]:
    """Generate names of children as (potential globals, sure globals)."""
    used = set()
    assigned = set()
    globaled = set()
    nonlocaled = set()

    i = 0
    iterate = []
    recurse = []

    if isinstance(node, ast.Assign):
        successors = [node.value]
    elif isinstance(node, ast.Lambda):
        all_args = _collect_args(node.args)
        assigned.update(a.arg for a in all_args)
        successors = [node.body]
    elif isinstance(node, _func_types):
        all_args = _collect_args(node.args)
        assigned.update(a.arg for a in all_args)
        annotation_names = (
            _collect_names(a.annotation)
            for a in all_args if a.annotation is not None
        )
        globaled.update(_multi_union(annotation_names))
        fdef_sources = node.args.kw_defaults + node.args.defaults
        fdef_sources += node.decorator_list + [node.returns]
        fdef_names = (_collect_names(d) for d in fdef_sources if d is not None)
        globaled.update(_multi_union(fdef_names))
        successors = node.body
    elif isinstance(node, ast.ClassDef):
        cdef_sources = node.bases + node.keywords
        cdef_sources += node.decorator_list
        cdef_names = (_collect_names(b) for b in cdef_sources)
        globaled.update(_multi_union(cdef_names))
        successors = node.body
    else:
        successors = list(ast.iter_child_nodes(node))

    iterate.extend(successors)

    while i < len(iterate):
        n = iterate[i]
        assigned.update(_node_names(n) - used)
        if isinstance(n, ast.Name):
            used.add(n.id)
        elif isinstance(n, ast.Global):
            globaled.update(n.names)
        elif isinstance(n, ast.Nonlocal):
            nonlocaled.update(n.names)
        elif isinstance(n, _func_types + (ast.Lambda, ast.ClassDef)):
            recurse.append(n)
        else:
            iterate[i+1:i+1] = list(ast.iter_child_nodes(n))
        i += 1

    inner_potential = set()
    inner_globaled = set()

    for n in recurse:
        potential_, globaled_ = _node_refs_recursive(n)
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


def _node_refs(node: ast.AST) -> Set[str]:
    """Generate all names that a node refers to."""
    return _multi_union(_node_refs_recursive(node))


class NodeType(Enum):
    var = 'V'
    func = 'F'
    class_ = 'C'
    import_ = 'I'
    unknown = '?'


@dataclass
class NodeInfo:
    type: NodeType
    lineno: int


def _node_info(node: ast.AST) -> NodeInfo:
    """Return format string for displaying a node."""
    if isinstance(node, ast.Assign):
        t = NodeType.var
    elif isinstance(node, _func_types):
        t = NodeType.func
    elif isinstance(node, ast.ClassDef):
        t = NodeType.class_
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        t = NodeType.import_
    else:
        t = NodeType.unknown

    return NodeInfo(t, node.lineno)


def _top_nodes(
    node: ast.AST,
    skip_imports: bool = False
) -> Generator[ast.AST, None, None]:
    for n in ast.iter_child_nodes(node):
        if skip_imports and isinstance(n, (ast.Import, ast.ImportFrom)):
            continue
        yield n


def parse_refs(
    source: str,
    skip_imports: bool = False,
) -> Tuple[List[Tuple[Set[str], Set[str]]], List[NodeInfo]]:
    """Parse a reference array from source."""
    tree = ast.parse(source)
    refs = [
        (_node_names(node), _node_refs(node), _node_info(node))
        for node in _top_nodes(tree, skip_imports)
    ]
    refable_names = _multi_union(i[0] for i in refs)
    ref_array = [
        (ref[0], ref[1].intersection(refable_names))
        for ref in refs
    ]
    disp_formats = [ref[2] for ref in refs]
    return ref_array, disp_formats
