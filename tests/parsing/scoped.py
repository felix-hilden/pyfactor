from ._util import refs_equal


class TestScoped:
    @refs_equal
    def test_function_uses_none(self):
        source = 'def a():\n    pass'
        refs = [({'a'}, set())]
        return source, refs

    @refs_equal
    def test_function_uses_undeclared_var(self):
        source = 'def a():\n    return b'
        refs = [({'a'}, set())]
        return source, refs

    @refs_equal
    def test_function_uses_var(self):
        source = 'b = 1\ndef a():\n    return b'
        refs = [({'b'}, set()), ({'a'}, {'b'})]
        return source, refs

    @refs_equal
    def test_class_uses_undeclared_var(self):
        source = 'class A:\n    b = 1'
        refs = [({'A'}, set())]
        return source, refs

    @refs_equal
    def test_class_uses_var(self):
        source = 'b = 1\nclass A:\n    b'
        refs = [({'b'}, set()), ({'A'}, {'b'})]
        return source, refs
