import ast

from dataclasses import dataclass
from typing import List, Set, Iterable


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


def collect_args(args: ast.arguments):
    """Collect function arguments."""
    all_args = args.args + args.kwonlyargs
    all_args += [args.vararg, args.kwarg]
    return [arg for arg in all_args if arg is not None]


@dataclass
class Name:
    """Name dependencies."""

    name: str
    deps: Set[str]
    is_definition: bool


@dataclass
class Line:
    """Line of multiple names."""

    ast_node: ast.AST
    names: List[Name]


@dataclass
class Scope:
    """Scope state."""

    used: Set[str] = None
    assigned: Set[str] = None
    globaled: Set[str] = None
    nonlocaled: Set[str] = None
    inner_potential: Set[str] = None
    inner_globaled: Set[str] = None

    def __post_init__(self):
        """Ensure members are sets."""
        self.used = self.used or set()
        self.assigned = self.assigned or set()
        self.globaled = self.globaled or set()
        self.nonlocaled = self.nonlocaled or set()
        self.inner_potential = self.inner_potential or set()
        self.inner_globaled = self.inner_globaled or set()


@dataclass
class Visitor:
    """AST node visitor base."""

    node: ast.AST

    @staticmethod
    def forward_deps() -> Set[str]:
        """Dependencies to propagate forward to child nodes (note: not self)."""
        return set()

    @staticmethod
    def parse_names() -> List[Name]:
        """Parse self (no children), return appropriate names."""
        return []

    def children(self) -> List[ast.AST]:
        """Child nodes to be inspected next depending on ``breaks_scope``."""
        return []

    @property
    def breaks_scope(self) -> bool:
        """Node breaks scope and inner ones shouldn't be added to the current."""
        return False

    @staticmethod
    def create_scope() -> Scope:
        """Create new inner scope and populate from self."""
        return Scope()

    def update_scope(self, scope: Scope) -> None:
        """Update scope if in an inner scope (for global and nonlocal statements)."""

    @staticmethod
    def merge_scopes(outer: Scope, inner: Scope) -> None:
        """Merge inner scope to outer when moving back up in the ast tree."""
        # Nonlocaled can be considered "from this scope" because they require
        # an inner function scope, so we don't care about them in the outermost one
        from_this_scope = (inner.assigned | inner.nonlocaled) - inner.globaled
        outer.inner_potential.update(
            (inner.used | inner.inner_potential) - from_this_scope - inner.globaled
        )
        outer.inner_globaled.update(
            inner.globaled | inner.inner_globaled
        )


class DefaultVisitor(Visitor):
    def children(self) -> List[ast.AST]:
        return list(ast.iter_child_nodes(self.node))


class NameVisitor(Visitor):
    def update_scope(self, scope: Scope) -> None:
        scope.used.add(self.node.id)


class ScopedVisitor(Visitor):
    @property
    def breaks_scope(self) -> bool:
        return True


def assign_target_name(node) -> Name:
    """Generate name for an assign target component."""
    if isinstance(node, ast.Starred):
        node = node.value

    if isinstance(node, ast.Name):
        return Name(node.id, deps=set(), is_definition=True)
    elif isinstance(node, ast.Subscript):
        name = assign_target_name(node.value)
        deps = collect_names(node.slice)
        name.deps = name.deps | deps
        name.is_definition = False
        return name
    elif isinstance(node, ast.Attribute):
        name = assign_target_name(node.value)
        name.is_definition = False
        return name
    else:
        raise ValueError(
            f'Parsing error on line {node.lineno}: unknown assignment type!'
        )


def flatten_assign_targets(targets: List[ast.AST]) -> List[ast.AST]:
    """Extract assign targets from nested structures."""
    unresolved = targets
    resolved = []

    i = 0
    while i < len(unresolved):
        target = unresolved[i]
        if isinstance(target, (ast.List, ast.Tuple)):
            unresolved.extend(target.elts)
        else:
            resolved.append(target)
        i += 1
    return resolved


class AssignVisitor(ScopedVisitor):
    """Fake scoped to handle possible inner scoped nodes."""

    def children(self) -> List[ast.AST]:
        return [self.node.value]

    @property
    def _assign_targets(self) -> List[ast.AST]:
        return self.node.targets

    def parse_names(self) -> List[Name]:
        targets = flatten_assign_targets(self._assign_targets)
        return [assign_target_name(t) for t in targets]


class AugAssignVisitor(AssignVisitor):
    @property
    def _assign_targets(self) -> List[ast.AST]:
        return [self.node.target]


class AnnAssignVisitor(AssignVisitor):
    def children(self) -> List[ast.AST]:
        return [self.node.annotation, self.node.value]

    @property
    def _assign_targets(self) -> List[ast.AST]:
        return [self.node.target]


class ImportVisitor(Visitor):
    def parse_names(self) -> List[Name]:
        names = [n.name if n.asname is None else n.asname for n in self.node.names]
        return [Name(n, deps=set(), is_definition=True) for n in names]


class IfVisitor(Visitor):
    def forward_deps(self) -> Set[str]:
        return collect_names(self.node.test)

    def children(self) -> List[ast.AST]:
        return self.node.body + self.node.orelse


class WithVisitor(Visitor):
    def parse_names(self) -> List[Name]:
        names = []
        for item in self.node.items:
            if item.optional_vars is None:
                continue
            targets = flatten_assign_targets([item.optional_vars])
            i_names = [assign_target_name(t) for t in targets]
            i_deps = collect_names(item.context_expr)
            for name in i_names:
                name.deps = name.deps | i_deps
            names.extend(i_names)
        return names

    def children(self) -> List[ast.AST]:
        return self.node.body


class FunctionVisitor(ScopedVisitor):
    def parse_names(self) -> List[Name]:
        return [Name(self.node.name, deps=set(), is_definition=True)]

    def children(self) -> List[ast.AST]:
        return self.node.body

    def create_scope(self) -> Scope:
        scope = Scope()
        all_args = collect_args(self.node.args)
        scope.assigned.update(a.arg for a in all_args)
        annotation_names = (
            collect_names(a.annotation)
            for a in all_args if a.annotation is not None
        )
        scope.globaled.update(multi_union(annotation_names))
        fdef_sources = self.node.args.kw_defaults + self.node.args.defaults
        fdef_sources += self.node.decorator_list + [self.node.returns]
        fdef_names = (collect_names(d) for d in fdef_sources if d is not None)
        scope.globaled.update(multi_union(fdef_names))
        return scope


class LambdaVisitor(ScopedVisitor):
    def children(self) -> List[ast.AST]:
        return [self.node.body]

    def create_scope(self) -> Scope:
        scope = Scope()
        all_args = collect_args(self.node.args)
        scope.assigned.update(a.arg for a in all_args)
        return scope


class ClassVisitor(ScopedVisitor):
    def parse_names(self) -> List[Name]:
        return [Name(self.node.name, deps=set(), is_definition=True)]

    def children(self) -> List[ast.AST]:
        return self.node.body

    def create_scope(self) -> Scope:
        scope = Scope()
        cdef_sources = self.node.bases + self.node.keywords
        cdef_sources += self.node.decorator_list
        cdef_names = (collect_names(b) for b in cdef_sources)
        scope.globaled.update(multi_union(cdef_names))
        return scope

    @staticmethod
    def merge_scopes(outer: Scope, inner: Scope) -> None:
        from_this_scope = (inner.assigned | inner.nonlocaled) - inner.globaled
        outer.inner_potential.update(
            (inner.used - from_this_scope - inner.globaled) | inner.inner_potential
        )
        outer.inner_globaled.update(
            inner.globaled | inner.inner_globaled
        )


class ComprehensionVisitor(ScopedVisitor):
    def children(self) -> List[ast.AST]:
        return [self.node.elt]

    def create_scope(self) -> Scope:
        scope = Scope()
        for gen in self.node.generators:
            iters = collect_names(gen.iter)
            targets = collect_names(gen.target)
            ifs = multi_union(collect_names(f) for f in gen.ifs)

            scope.globaled.update(iters - scope.assigned)
            scope.assigned.update(targets)
            scope.globaled.update(ifs - scope.assigned)
        return scope


class DictCompVisitor(ComprehensionVisitor):
    def children(self) -> List[ast.AST]:
        return [self.node.key, self.node.value]


class GlobalVisitor(Visitor):
    def update_scope(self, scope: Scope) -> None:
        scope.globaled.update(self.node.names)


class NonlocalVisitor(Visitor):
    def update_scope(self, scope: Scope) -> None:
        scope.nonlocaled.update(self.node.names)


def cast(node: ast.AST) -> Visitor:
    """Cast node to a visitor."""
    if isinstance(node, ast.Name):
        return NameVisitor(node)

    # Assign visitors
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        return ImportVisitor(node)
    elif isinstance(node, ast.Assign):
        return AssignVisitor(node)
    elif isinstance(node, ast.AugAssign):
        return AugAssignVisitor(node)
    elif isinstance(node, ast.AnnAssign):
        return AnnAssignVisitor(node)

    # Flow control visitors
    elif isinstance(node, ast.If):
        return IfVisitor(node)
    elif isinstance(node, (ast.With, ast.AsyncWith)):
        return WithVisitor(node)

    # Scoped visitors
    elif isinstance(node, ast.ClassDef):
        return ClassVisitor(node)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return FunctionVisitor(node)
    elif isinstance(node, ast.Lambda):
        return LambdaVisitor(node)
    elif isinstance(node, ast.DictComp):
        return DictCompVisitor(node)
    elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        return ComprehensionVisitor(node)

    # Miscellaneous visitors
    elif isinstance(node, ast.Global):
        return GlobalVisitor(node)
    elif isinstance(node, ast.Nonlocal):
        return NonlocalVisitor(node)

    # Default to DefaultVisitor
    elif isinstance(node, ast.AST):
        return DefaultVisitor(node)


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
        uses = multi_union(n.deps for n in c_names) | child.forward_deps()
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
