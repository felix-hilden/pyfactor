"""
Script dependency visualisation.

See online documentation on `RTD <https://pyfactor.rtfd.org>`_.
"""
import os as _os
from sys import stderr as _stderr
from typing import List as _List
from pathlib import Path as _Path

_version_file = _Path(_os.path.realpath(__file__)).parent / 'VERSION'
__version__ = _version_file.read_text().strip()

from . import _cli, _parse, _graph, _io
from ._graph import create_legend, preprocess, render


def parse(
    source_path: str,
    graph_path: str,
    skip_imports: bool = False,
    exclude: _List[str] = None,
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
    exclude
        exclude nodes in the graph
    """
    source = _io.read_source(source_path)
    nodes = _parse.parse_refs(source)
    graph = _graph.create_graph(
        nodes,
        skip_imports=skip_imports,
        exclude=exclude,
    )
    _io.write_graph(graph, graph_path)


def legend(path: str, preprocess_kwargs: dict, render_kwargs: dict) -> None:
    """
    Create and render a legend.

    Parameters
    ----------
    path
        legend image file
    preprocess_kwargs
        keyword arguments for :func:`preprocess`
    render_kwargs
        keyword arguments for :func:`render`
    """
    source = create_legend()
    source = preprocess(source, **preprocess_kwargs)
    render(source, path, **render_kwargs)


def pyfactor(
    source_path: str = None,
    graph_path: str = None,
    render_path: str = None,
    parse_kwargs: dict = None,
    preprocess_kwargs: dict = None,
    render_kwargs: dict = None,
) -> None:
    """
    Pyfactor Python endpoint.

    See the command line help for more information.

    Parameters
    ----------
    source_path
        Python source file
    graph_path
        graph definition file
    render_path
        image file
    parse_kwargs
        keyword arguments for :func:`parse`
    preprocess_kwargs
        keyword arguments for :func:`preprocess`
    render_kwargs
        keyword arguments for :func:`render`
    """
    parse_kwargs = parse_kwargs or {}
    preprocess_kwargs = preprocess_kwargs or {}
    render_kwargs = render_kwargs or {}

    graph_temp = graph_path or str(_Path(source_path).with_suffix('.gv'))

    if source_path is not None:
        parse(source_path, graph_temp, **parse_kwargs)

    if render_path is not None:
        source = _io.read_graph(graph_temp)
        source = preprocess(source, **preprocess_kwargs)
        render(source, render_path, **render_kwargs)

        if graph_path is None:
            _Path(graph_temp).unlink()


def main() -> None:
    """Pyfactor CLI endpoint."""
    args = _cli.parser.parse_args()

    if args.version:
        print(f'Pyfactor v.{__version__}', file=_stderr)
        exit(0)

    if args.names is None:
        if args.legend is None:
            _cli.parser.print_help(_stderr)
        exit(1)

    try:
        source_path, graph_path, render_path = _cli.parse_names(args.names)
    except _cli.ArgumentError as e:
        print(str(e), file=_stderr)
        exit(1)

    parse_kwargs = {
        'skip_imports': args.skip_imports,
        'exclude': args.exclude,
    }
    preprocess_kwargs = {
        'stagger': args.stagger,
        'fanout': not args.no_fanout,
        'chain': args.chain,
    }
    render_kwargs = {
        'view': args.view,
        'format': args.format,
        'renderer': args.renderer,
        'formatter': args.formatter,
    }

    if args.legend:
        legend(args.legend, preprocess_kwargs, render_kwargs)

    pyfactor(
        source_path,
        graph_path,
        render_path,
        parse_kwargs,
        preprocess_kwargs,
        render_kwargs,
    )
