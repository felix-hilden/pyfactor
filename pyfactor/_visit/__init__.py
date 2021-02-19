import ast

from typing import List
from .base import Visitor, Scope, Name, Line
from .visitors import cast, multi_union


def parse_scoped(visitor: Visitor, scope: Scope) -> List[Name]:
    """Parse nodes in a scope with shortcuts."""
    for child in visitor.children():
        child = cast(child)
        if child is None:
            continue

        if child.breaks_scope:
            new_scope = child.create_scope()
            c_names = parse_scoped(child, new_scope)
            child.merge_scopes(scope, new_scope)
        else:
            c_names = parse_scoped(child, scope)

        child.update_scope(scope)

        assigns = {n.name for n in c_names}
        uses = multi_union(n.deps for n in c_names)
        scope.assigned.update(assigns - scope.used)
        scope.used.update(uses)

    return visitor.parse_names()


def parse_no_scope(visitor: Visitor) -> List[Line]:
    """Fully parse nodes as in outermost scope."""
    forward = visitor.forward_deps()
    lines = []

    for child in visitor.children():
        child = cast(child)
        if child is None:
            continue

        if child.breaks_scope:
            scope = child.create_scope()
            c_names = parse_scoped(child, scope)
            merged = Scope()
            child.merge_scopes(merged, scope)
            deps = merged.inner_globaled | merged.inner_potential
            for name in c_names:
                name.deps = name.deps | deps
            lines.append(Line(child.node, c_names))
        else:
            lines.extend(parse_no_scope(child))

    for line in lines:
        for name in line.names:
            name.deps = name.deps | forward

    self_line = Line(visitor.node, visitor.parse_names())
    return [self_line] + lines


def parse_lines(source: str) -> List[Line]:
    """Parse name definitions and references on lines from source."""
    tree = ast.parse(source)
    lines = parse_no_scope(cast(tree))
    defined_names = {n.name for line in lines for n in line.names}

    for line in lines:
        for name in line.names:
            name.deps = name.deps.intersection(defined_names)

    return lines
