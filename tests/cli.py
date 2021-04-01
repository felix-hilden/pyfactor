import pytest
from pyfactor._cli import parse_names, ArgumentError


class TestCLI:
    def test_all_specified(self):
        s, g, o = parse_names(['s'], 'g', 'o')
        assert (s, g, o) == (['s'], 'g', 'o')

    def test_source_disabled(self):
        s, g, o = parse_names([], 'g', 'o')
        assert s is None
        assert (g, o) == ('g', 'o')

    def test_graph_disabled(self):
        s, g, o = parse_names(['s'], '-', 'o')
        assert g is None
        assert (s, o) == (['s'], 'o')

    def test_output_disabled(self):
        s, g, o = parse_names(['s'], 'g', '-')
        assert o is None
        assert (s, g) == (['s'], 'g')

    def test_source_graph_disabled(self):
        with pytest.raises(ArgumentError):
            parse_names([], '-', 'o')

    def test_source_output_disabled(self):
        with pytest.raises(ArgumentError):
            parse_names([], 'g', '-')

    def test_graph_output_disabled(self):
        with pytest.raises(ArgumentError):
            parse_names(['s'], '-', '-')

    def test_all_disabled(self):
        with pytest.raises(ArgumentError):
            parse_names([], '-', '-')

    def test_infer_graph(self):
        s, g, o = parse_names(['s'], None, 'o')
        assert (s, g, o) == (['s'], 's.gv', 'o')

    def test_infer_output(self):
        s, g, o = parse_names(['s'], 'g', None)
        assert (s, g, o) == (['s'], 'g', 'g')

    def test_infer_graph_output(self):
        s, g, o = parse_names(['s'], None, None)
        assert (s, g, o) == (['s'], 's.gv', 's')

    def test_disabled_source_infer_graph(self):
        with pytest.raises(ArgumentError):
            parse_names([], None, 'o')

    def test_disabled_source_infer_output(self):
        s, g, o = parse_names([], 'g', None)
        assert s is None
        assert (g, o) == ('g', 'g')

    def test_disabled_graph_infer_output(self):
        s, g, o = parse_names(['s'], '-', None)
        assert g is None
        assert (s, o) == (['s'], 's')

    def test_infer_graph_disabled_output(self):
        s, g, o = parse_names(['s'], None, '-')
        assert o is None
        assert (s, g) == (['s'], 's.gv')

    def test_disabled_source_infer_graph_source(self):
        with pytest.raises(ArgumentError):
            parse_names([], None, None)

    def test_disabled_source_graph_infer_source(self):
        with pytest.raises(ArgumentError):
            parse_names([], '-', None)

    def test_disabled_source_output_infer_graph(self):
        with pytest.raises(ArgumentError):
            parse_names([], None, '-')
