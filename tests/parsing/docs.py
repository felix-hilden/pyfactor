from ._util import docs_equal


class TestAssign:
    @docs_equal
    def test_module_doc_attached(self):
        source = '"doc"'
        docs = ['doc']
        return source, docs

    @docs_equal
    def test_module_non_str_const_not_attached(self):
        source = '1'
        docs = []
        return source, docs

    @docs_equal
    def test_assignment_doc_attached(self):
        source = 'a = 1\n"doc"'
        docs = ['doc']
        return source, docs

    @docs_equal
    def test_assignment_non_str_const_not_attached(self):
        source = 'a = 1\n2'
        docs = [None]
        return source, docs

    @docs_equal
    def test_func_doc_attached(self):
        source = 'def foo():\n  """doc"""'
        docs = ['doc']
        return source, docs

    @docs_equal
    def test_func_non_str_const_not_attached(self):
        source = 'def foo():\n  1'
        docs = [None]
        return source, docs

    @docs_equal
    def test_class_doc_attached(self):
        source = 'class A:\n  """doc"""'
        docs = ['doc']
        return source, docs

    @docs_equal
    def test_class_non_str_const_not_attached(self):
        source = 'class A:\n  1'
        docs = [None]
        return source, docs

    @docs_equal
    def test_const_in_comprehension_not_interpreted_as_doc(self):
        source = '{1 for _ in range(1)}'
        docs = []
        return source, docs
