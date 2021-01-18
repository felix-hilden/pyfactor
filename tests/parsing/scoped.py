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
    def test_async_function_uses_var(self):
        source = 'b = 1\nasync def a():\n    return b'
        refs = [({'b'}, set()), ({'a'}, {'b'})]
        return source, refs

    @refs_equal
    def test_var_in_func_shadows(self):
        source = 'a = 1\ndef foo():\n  a = 2'
        refs = [({'a'}, set()), ({'foo'}, set())]
        return source, refs

    @refs_equal
    def test_func_parameter_shadows(self):
        source = 'a = 1\ndef foo(a):\n  return a'
        refs = [({'a'}, set()), ({'foo'}, set())]
        return source, refs

    @refs_equal
    def test_func_parameter_default_uses_var(self):
        source = 'a = 1\ndef foo(p=a):\n  return p'
        refs = [({'a'}, set()), ({'foo'}, {'a'})]
        return source, refs

    @refs_equal
    def test_func_parameter_annotation_uses_var(self):
        source = 'a = 1\ndef foo(p: a):\n  return p'
        refs = [({'a'}, set()), ({'foo'}, {'a'})]
        return source, refs

    @refs_equal
    def test_func_return_annotation_uses_var(self):
        source = 'a = 1\ndef foo() -> a:\n  pass'
        refs = [({'a'}, set()), ({'foo'}, {'a'})]
        return source, refs

    @refs_equal
    def test_func_decorator_uses_var(self):
        source = 'a = 1\n@a\ndef foo():\n  pass'
        refs = [({'a'}, set()), ({'foo'}, {'a'})]
        return source, refs

    @refs_equal
    def test_var_in_func_double_shadows(self):
        source = """
a = 1
def foo():
    a = 2
    def bar():
        a = 3
"""
        refs = [({'a'}, set()), ({'foo'}, set())]
        return source, refs

    @refs_equal
    def test_inner_func_uses_var(self):
        source = """
a = 1
def foo():
    def bar():
        b = a
"""
        refs = [({'a'}, set()), ({'foo'}, {'a'})]
        return source, refs

    @refs_equal
    def test_inner_func_uses_nonlocal(self):
        source = """
a = 1
def foo():
    a = 2
    def bar():
        b = a
"""
        refs = [({'a'}, set()), ({'foo'}, set())]
        return source, refs

    @refs_equal
    def test_inner_func_uses_global(self):
        source = """
a = 1
def foo():
    a = 2
    def bar():
        global a
        b = a
"""
        refs = [({'a'}, set()), ({'foo'}, {'a'})]
        return source, refs

    @refs_equal
    def test_inner_func_name_shadows(self):
        source = """
a = 1
def foo():
    def a():
        pass
    b = a
"""
        refs = [({'a'}, set()), ({'foo'}, set())]
        return source, refs

    @refs_equal
    def test_func_called(self):
        source = 'def foo():\n    return\na = foo()'
        refs = [({'foo'}, set()), ({'a'}, {'foo'})]
        return source, refs

    @refs_equal
    def test_class_body_uses_undeclared_var(self):
        source = 'class A:\n    b = 1'
        refs = [({'A'}, set())]
        return source, refs

    @refs_equal
    def test_class_body_uses_var(self):
        source = 'b = 1\nclass A:\n    b'
        refs = [({'b'}, set()), ({'A'}, {'b'})]
        return source, refs

    @refs_equal
    def test_var_in_class_shadows(self):
        source = 'a = 1\nclass A:\n  a = 2'
        refs = [({'a'}, set()), ({'A'}, set())]
        return source, refs

    @refs_equal
    def test_var_in_class_uses_then_shadows(self):
        source = 'a = 1\nclass A:\n  b = a\n  a = 2'
        refs = [({'a'}, set()), ({'A'}, {'a'})]
        return source, refs

    @refs_equal
    def test_class_bases_uses_var(self):
        source = 'a = 1\nclass A(a):\n    pass'
        refs = [({'a'}, set()), ({'A'}, {'a'})]
        return source, refs

    @refs_equal
    def test_class_meta_uses_var(self):
        source = 'a = 1\nclass A(metaclass=a):\n    pass'
        refs = [({'a'}, set()), ({'A'}, {'a'})]
        return source, refs

    @refs_equal
    def test_class_decorator_uses_var(self):
        source = 'a = 1\n@a\nclass A:\n    pass'
        refs = [({'a'}, set()), ({'A'}, {'a'})]
        return source, refs

    @refs_equal
    def test_instance_var_in_class_shadows(self):
        source = 'a = 1\nclass A:\n  def __init__(self):\n    self.a = 2'
        refs = [({'a'}, set()), ({'A'}, set())]
        return source, refs

    @refs_equal
    def test_instance_var_in_class_uses_then_shadows(self):
        source = 'a = 1\nclass A:\n  def __init__(self):\n    self.a = a'
        refs = [({'a'}, set()), ({'A'}, {'a'})]
        return source, refs

    @refs_equal
    def test_instance_var_in_class_as_param(self):
        source = 'a = 1\nclass A:\n  def __init__(self, a):\n    self.a = a'
        refs = [({'a'}, set()), ({'A'}, set())]
        return source, refs

    @refs_equal
    def test_class_body_scope_not_propagated_to_methods(self):
        source = """
a = 1
class A:
    a = 2
    def __init__(self):
        self.a = a
"""
        refs = [({'a'}, set()), ({'A'}, {'a'})]
        return source, refs

    @refs_equal
    def test_class_instantiated(self):
        source = 'class A:\n  pass\na = A()'
        refs = [({'A'}, set()), ({'a'}, {'A'})]
        return source, refs

    @refs_equal
    def test_classmethod_used(self):
        source = 'class A:\n  pass\na = A.meth()'
        refs = [({'A'}, set()), ({'a'}, {'A'})]
        return source, refs

    @refs_equal
    def test_lambda_uses_var(self):
        source = "a = 1\nb = lambda x: a"
        refs = [({'a'}, set()), ({'b'}, {'a'})]
        return source, refs

    @refs_equal
    def test_lambda_argument_shadows(self):
        source = "a = 1\nb = lambda a: a"
        refs = [({'a'}, set()), ({'b'}, set())]
        return source, refs

    @refs_equal
    def test_lambda_in_call_shadows(self):
        source = "a = 1\nb = foo(lambda a: a)"
        refs = [({'a'}, set()), ({'b'}, set())]
        return source, refs

    @refs_equal
    def test_lambda_in_scope_shadows(self):
        source = """
a = 1
def foo():
    return lambda a: a
"""
        refs = [({'a'}, set()), ({'foo'}, set())]
        return source, refs
