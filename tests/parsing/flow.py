from ._util import refs_equal, refs_in


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

    @refs_equal
    def test_try(self):
        source = """
try:
    a = 1
except:
    b = 2
else:
    c = 3
finally:
    d = 4
"""
        refs = [('a', set()), ('b', set()), ('c', set()), ('d', set())]
        return source, refs

    @refs_equal
    def test_try_handler_propagated_forward(self):
        source = 'a = 1\ntry:\n  pass\nexcept a:\n  b = 1'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_try_handler_as_tuple(self):
        source = 'a = 1\ntry:\n  pass\nexcept (a, ValueError):\n  b = 1'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_while(self):
        source = 'while True:\n  a = 1'
        refs = [('a', set())]
        return source, refs

    @refs_equal
    def test_while_test_propagated_forward(self):
        source = 'a = 1\nwhile a:\n  b = 2\nelse:\n  c = 3'
        refs = [('a', set()), ('b', {'a'}), ('c', {'a'})]
        return source, refs

    @refs_equal
    def test_for_assigns(self):
        source = 'for a in range(3):\n  pass'
        refs = [('a', set())]
        return source, refs

    @refs_equal
    def test_for_iter_uses_var(self):
        source = 'a = 1\nfor b in range(a):\n  pass'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_in
    def test_for_nested_assign(self):
        source = 'for a, (b, c) in range(3):\n  pass'
        refs = [('a', set()), ('b', set()), ('c', set())]
        return source, refs

    @refs_equal
    def test_for_iter_propagated_forward(self):
        source = 'a = 1\nfor b in range(a):\n  c = 3\nelse:  d = 4'
        refs = [('a', set()), ('b', {'a'}), ('c', {'a'}), ('d', {'a'})]
        return source, refs
