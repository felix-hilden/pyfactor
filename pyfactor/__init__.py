"""
Script dependency visualisation.

See Readme file on `GitHub <https://github.com/felix-hilden/pyfactor>`_.
"""
import os as _os
from sys import stderr as _stderr
from pathlib import Path as _Path

_version_file = _Path(_os.path.realpath(__file__)).parent / 'VERSION'
__version__ = _version_file.read_text().strip()

from ._cli import parser as _parser
from ._graph import create_graph, write_graph, render
from ._parse import read_source, parse_refs


def parse(
    source_path: str,
    graph_path: str,
    skip_imports: bool = False,
) -> None:
    """
    Parse source and create graph file.

    Parameters
    ----------
    source_path
        path to Python source file to read
    graph_path
        path to graph file to write
    skip_imports
        do not visualise imports (reducing clutter)
    """
    source = read_source(source_path)
    references, formats = parse_refs(source, skip_imports)
    graph = create_graph(references, formats)
    write_graph(graph, graph_path)


def main() -> None:
    """Pyfactor CLI endpoint."""
    args = _parser.parse_args()

    if args.version:
        print(f'Pyfactor v.{__version__}', file=_stderr)
        exit(0)

    if args.source is None:
        _parser.print_help(_stderr)
        exit(1)

    if not args.graph_source:
        if isinstance(args.graph_output, str):
            graph_path = args.graph_source
        else:
            graph_path = str(_Path(args.source).with_suffix('.gv'))
        parse(args.source, graph_path, skip_imports=args.skip_imports)
    else:
        graph_path = args.source

    if not args.no_output:
        if args.output is None:
            out_path = str(_Path(args.source).with_suffix(''))
        else:
            out_path = args.output

        render(graph_path, out_path, view=args.open, format=args.format)

        if not args.graph_output:
            try:
                _Path(graph_path).unlink()
            except FileNotFoundError:
                pass
