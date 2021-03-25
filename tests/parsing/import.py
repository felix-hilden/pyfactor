from ._util import refs_equal


class TestImport:
    @refs_equal
    def test_import_module(self):
        source = 'import a'
        refs = [('a', set())]
        return source, refs

    @refs_equal
    def test_import_modules(self):
        source = 'import a, b'
        refs = [('a', set()), ('b', set())]
        return source, refs

    @refs_equal
    def test_import_module_as(self):
        source = 'import a as b'
        refs = [('b', set())]
        return source, refs

    @refs_equal
    def test_import_modules_as(self):
        source = 'import a as b, c as d'
        refs = [('b', set()), ('d', set())]
        return source, refs

    @refs_equal
    def test_import_submodule(self):
        source = 'import a.b'
        refs = [('a', set())]
        return source, refs

    @refs_equal
    def test_import_submodule_as(self):
        source = 'import a.b as c'
        refs = [('c', set())]
        return source, refs

    @refs_equal
    def test_from_import_module(self):
        source = 'from a import b'
        refs = [('b', set())]
        return source, refs

    @refs_equal
    def test_from_import_module_as(self):
        source = 'from a import b as c'
        refs = [('c', set())]
        return source, refs

    @refs_equal
    def test_import_modules_mixed(self):
        source = 'import a as b, c'
        refs = [('b', set()), ('c', set())]
        return source, refs

    @refs_equal
    def test_use_import_in_var(self):
        source = 'import a\nb = a'
        refs = [('a', set()), ('b', {'a'})]
        return source, refs
