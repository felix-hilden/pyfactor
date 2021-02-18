from ._util import refs_equal


class TestFlow:
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
