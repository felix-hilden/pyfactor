from ._util import refs_equal


class TestAssign:
    @refs_equal
    def test_assign_uses_none(self):
        source = 'a = 1'
        refs = [('a', set())]
        return source, refs

    @refs_equal
    def test_assign_uses_var(self):
        source = 'a = 1\nb = a'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_assign_uses_undeclared_var(self):
        source = 'b = a'
        refs = [('b', set())]
        return source, refs

    @refs_equal
    def test_multiple_assign_uses_var(self):
        source = 'c = 1\na = b = c'
        refs = [('c', set()), ('a', {'c'}), ('b', {'c'})]
        return source, refs

    @refs_equal
    def test_unpack_assign_uses_none(self):
        source = 'a, b = (1, 2)'
        refs = [('a', set()), ('b', set())]
        return source, refs

    @refs_equal
    def test_unpack_repack_assign_uses_none(self):
        source = 'a, *b = (1, 2)'
        refs = [('a', set()), ('b', set())]
        return source, refs

    @refs_equal
    def test_unpack_assign_uses_var(self):
        source = 'c = 1\na, b = (c, 2)'
        refs = [('c', set()), ('a', {'c'}), ('b', {'c'})]
        return source, refs

    @refs_equal
    def test_aug_assign_to_var(self):
        source = 'a = 1\na += 1'
        refs = [('a', set()), ('a', set())]
        return source, refs

    @refs_equal
    def test_aug_assign_uses_var(self):
        source = 'a = 1\nb = 1\nb += a'
        refs = [('a', set()), ('b', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_ann_assign_uses_var(self):
        source = 'a = 1\nb: int = a'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_ann_assign_hint_uses_var(self):
        source = 'a = int\nb: a = 1'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs

    @refs_equal
    def test_assign_to_attribute(self):
        source = 'a = 1\nb = 2\na.b = 2'
        refs = [('a', set()), ('b', set()), ('a', set())]
        return source, refs

    @refs_equal
    def test_assign_var_to_attribute(self):
        source = 'a = 1\nb = 2\na.attr = b'
        refs = [('a', set()), ('b', set()), ('a', {'b'})]
        return source, refs

    @refs_equal
    def test_assign_var_to_subscript(self):
        source = 'a = [0, 1]\nb = 1\na[0] = b'
        refs = [('a', set()), ('b', set()), ('a', {'b'})]
        return source, refs

    @refs_equal
    def test_assign_to_subscript_with_var(self):
        source = 'a = [0, 1]\nb = 1\na[b] = 1'
        refs = [('a', set()), ('b', set()), ('a', {'b'})]
        return source, refs

    @refs_equal
    def test_assign_to_subscript_attribute(self):
        source = 'a = 0\nb = 1\na[b].c = 1'
        refs = [('a', set()), ('b', set()), ('a', {'b'})]
        return source, refs

    @refs_equal
    def test_assign_to_attribute_subscript(self):
        source = 'a = 0\nb = 1\na.c[b] = 1'
        refs = [('a', set()), ('b', set()), ('a', {'b'})]
        return source, refs
