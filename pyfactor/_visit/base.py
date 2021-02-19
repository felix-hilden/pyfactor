import ast

from dataclasses import dataclass
from typing import List, Set


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
        """
        Dependencies to propagate forward to child nodes.

        Forward dependencies do not apply to the parsed names of the node.
        This method is used only in the outermost scope,
        functionality should be mirrored in :meth:`update_scope`.
        """
        return set()

    @staticmethod
    def parse_names() -> List[Name]:
        """
        Parse names from this node.

        Names from child nodes should not be parsed,
        but instead returned in :meth:`children`.
        """
        return []

    def children(self) -> List[ast.AST]:
        """Child nodes to be inspected next."""
        return []

    @property
    def breaks_scope(self) -> bool:
        """
        Node breaks scope.

        Inner definitions should not be added to the current scope.
        """
        return False

    @staticmethod
    def create_scope() -> Scope:
        """Create and populate a new inner scope."""
        return Scope()

    def update_scope(self, scope: Scope) -> None:
        """
        Update scope of an inner scope.

        For statements that neither break scope nor define names.
        """

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
