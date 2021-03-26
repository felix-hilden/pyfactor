from ._util import refs_equal, import_equal


class TestImport:
    @import_equal
    def test_import_module(self):
        source = 'import a'
        refs = [('a', 'a')]
        return source, refs

    @import_equal
    def test_import_modules(self):
        source = 'import a, b'
        refs = [('a', 'a'), ('b', 'b')]
        return source, refs

    @import_equal
    def test_import_module_as(self):
        source = 'import a as b'
        refs = [('b', 'a')]
        return source, refs

    @import_equal
    def test_import_modules_as(self):
        source = 'import a as b, c as d'
        refs = [('b', 'a'), ('d', 'c')]
        return source, refs

    @import_equal
    def test_import_submodule(self):
        source = 'import a.b'
        refs = [('a', 'a')]
        return source, refs

    @import_equal
    def test_import_submodule_as(self):
        source = 'import a.b as c'
        refs = [('c', 'a.b')]
        return source, refs

    @import_equal
    def test_from_import_module(self):
        source = 'from a import b'
        refs = [('b', 'a.b')]
        return source, refs

    @import_equal
    def test_from_import_module_as(self):
        source = 'from a import b as c'
        refs = [('c', 'a.b')]
        return source, refs

    @import_equal
    def test_from_import_modules(self):
        source = 'from a import b, c'
        refs = [('b', 'a.b'), ('c', 'a.c')]
        return source, refs

    @import_equal
    def test_import_modules_mixed(self):
        source = 'import a as b, c'
        refs = [('b', 'a'), ('c', 'c')]
        return source, refs

    @refs_equal
    def test_use_import_in_var(self):
        source = 'import a\nb = a'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs
