from ._util import refs_equal


class TestFlow:
    @refs_equal
    def test_if_test_comprehension_shadows(self):
        source = 'a = 1\nif {a for a in range(2)}:\n  b = 2'
        refs = [('a', set()), ('b', set())]
        return source, refs

    @refs_equal
    def test_if_test_comprehension_uses(self):
        source = 'a = 1\nif {a for i in range(2)}:\n  b = 2'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_if_test_propagated_to_body(self):
        source = 'a = 1\nif a:\n  b = 2'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_if_test_propagated_to_else(self):
        source = 'a = 1\nif a:\n  pass\nelse:\n  b = 2'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_elif_test_propagated_to_body(self):
        source = """
a = 1
b = 2
if a:
  pass
elif b:
  c = 3
"""
        refs = [('a', set()), ('b', set()), ('c', {'a', 'b'})]
        return source, refs

    @refs_equal
    def test_elif_test_propagated_to_else(self):
        source = """
a = 1
b = 2
if a:
  pass
elif b:
  pass
else:
  c = 3
"""
        refs = [('a', set()), ('b', set()), ('c', {'a', 'b'})]
        return source, refs

    @refs_equal
    def test_with_const(self):
        source = 'with 1:\n  pass'
        refs = []
        return source, refs

    @refs_equal
    def test_with_assigns_name(self):
        source = 'with 1 as a:\n  pass'
        refs = [('a', set())]
        return source, refs

    @refs_equal
    def test_with_assigns_names(self):
        source = 'with 1 as a, 2 as b:\n  pass'
        refs = [('a', set()), ('b', set())]
        return source, refs

    @refs_equal
    def test_with_assigns_name_using_var(self):
        source = 'a = 1\nwith a as b:\n  pass'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_with_assigns_nested_names(self):
        source = 'with 1 as (a, (b, c)):\n  pass'
        refs = [('a', set()), ('b', set()), ('c', set())]
        return source, refs

    @refs_equal
    def test_with_name_not_propagated_forward(self):
        source = 'with 1 as a:\n  b = 1'
        refs = [('a', set()), ('b', set())]
        return source, refs
