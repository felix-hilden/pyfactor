from ._util import refs_equal


class TestAssign:
    @refs_equal
    def test_assign_uses_none(self):
        source = 'a = 1'
        refs = [({'a'}, set())]
        return source, refs

    @refs_equal
    def test_assign_uses_var(self):
        source = 'a = 1\nb = a'
        refs = [({'a'}, set()), ({'b'}, {'a'})]
        return source, refs

    @refs_equal
    def test_assign_uses_undeclared_var(self):
        source = 'b = a'
        refs = [({'b'}, set())]
        return source, refs

    @refs_equal
    def test_multiple_assign_uses_var(self):
        source = 'c = 1\na = b = c'
        refs = [({'c'}, set()), ({'a', 'b'}, {'c'})]
        return source, refs

    @refs_equal
    def test_unpack_assign_uses_none(self):
        source = 'a, b = (1, 2)'
        refs = [({'a', 'b'}, set())]
        return source, refs

    @refs_equal
    def test_unpack_repack_assign_uses_none(self):
        source = 'a, *b = (1, 2)'
        refs = [({'a', 'b'}, set())]
        return source, refs

    @refs_equal
    def test_unpack_assign_uses_var(self):
        source = 'c = 1\na, b = (c, 2)'
        refs = [({'c'}, set()), ({'a', 'b'}, {'c'})]
        return source, refs
