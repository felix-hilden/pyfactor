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
    """Collect all names that a node has as children."""
    names = []
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            names.append(n.id)
    return set(names)


def _node_names(node: ast.AST) -> Set[str]:
    """Generate names that a node is referred to with."""
    if isinstance(node, ast.Assign):
        return _multi_union(_collect_names(t) for t in node.targets)
    elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        return {node.name}
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        return {n.name if n.asname is None else n.asname for n in node.names}
    else:
        return set()


def _node_refs(node: ast.AST) -> Set[str]:
    """Generate all names that a node refers to."""
    if isinstance(node, ast.Assign):
        node = node.value
    return _collect_names(node)


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
    elif isinstance(node, ast.FunctionDef):
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
