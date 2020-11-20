from functools import wraps
from pyfactor import parse_refs


def refs_equal(func):
    @wraps(func)
    def wrapper(self):
        source, refs = func(self)
        parsed, _ = parse_refs(source)
        assert parsed == refs
    return wrapper


class TestParsing:
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

    @refs_equal
    def test_import_module(self):
        source = 'import a'
        refs = [({'a'}, set())]
        return source, refs

    @refs_equal
    def test_import_modules(self):
        source = 'import a, b'
        refs = [({'a', 'b'}, set())]
        return source, refs

    @refs_equal
    def test_import_module_as(self):
        source = 'import a as b'
        refs = [({'b'}, set())]
        return source, refs

    @refs_equal
    def test_import_modules_as(self):
        source = 'import a as b, c as d'
        refs = [({'b', 'd'}, set())]
        return source, refs

    @refs_equal
    def test_from_import_module(self):
        source = 'from a import b'
        refs = [({'b'}, set())]
        return source, refs

    @refs_equal
    def test_from_import_module_as(self):
        source = 'from a import b as c'
        refs = [({'c'}, set())]
        return source, refs

    @refs_equal
    def test_import_modules_mixed(self):
        source = 'import a as b, c'
        refs = [({'b', 'c'}, set())]
        return source, refs

    @refs_equal
    def test_use_import_in_var(self):
        source = 'import a\nb = a'
        refs = [({'a'}, set()), ({'b'}, {'a'})]
        return source, refs
