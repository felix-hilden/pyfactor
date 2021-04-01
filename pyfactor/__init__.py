"""
Script dependency visualisation.

See online documentation on `RTD <https://pyfactor.rtfd.org>`_.
"""
import os as _os
from sys import stderr as _stderr
from typing import List as _List, Dict as _Dict
from pathlib import Path as _Path

_version_file = _Path(_os.path.realpath(__file__)).parent / 'VERSION'
__version__ = _version_file.read_text().strip()

from . import _cli, _visit, _graph, _io
from ._graph import create_legend
from ._gv import preprocess, render


def parse(
    source_paths: _List[str],
    graph_path: str,
    skip_external: bool = False,
    imports: str = 'interface',
    exclude: _List[str] = None,
    root: str = None,
    collapse_waypoints: bool = False,
    collapse_exclude: _List[str] = None,
    graph_attrs: _Dict[str, str] = None,
    node_attrs: _Dict[str, str] = None,
    edge_attrs: _Dict[str, str] = None,
) -> None:
    """
    Parse source and create graph file.

    Parameters
    ----------
    source_paths
        paths to Python source files to read
    graph_path
        path to graph file to write
    skip_external
        do not visualise imports to external modules (reducing clutter)
    imports
        import duplication/resolving mode
    exclude
        exclude nodes in the graph
    root
        only show root and its children in the graph
    collapse_waypoints
        collapse waypoint nodes
    collapse_exclude
        exclude nodes from being collapsed
    graph_attrs
        Graphviz graph attributes (overrided by Pyfactor)
    node_attrs
        Graphviz node attributes (overrided by Pyfactor)
    edge_attrs
        Graphviz edge attributes (overrided by Pyfactor)
    """
    sources = _io.resolve_sources(source_paths)
    for s in sources:
        s.content = _io.read_source(s.file)
    parsed = [_visit.parse_lines(s) for s in sources]
    graph = _graph.create_graph(
        list(zip(sources, parsed)),
        skip_external=skip_external,
        imports=imports,
        exclude=exclude,
        root=root,
        collapse_waypoints=collapse_waypoints,
        collapse_exclude=collapse_exclude,
        graph_attrs=graph_attrs,
        node_attrs=node_attrs,
        edge_attrs=edge_attrs,
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
    source_paths: _List[str] = None,
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
    source_paths
        Python source files
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
    source_paths = source_paths or []
    parse_kwargs = parse_kwargs or {}
    preprocess_kwargs = preprocess_kwargs or {}
    render_kwargs = render_kwargs or {}

    graph_temp = graph_path or str(_cli.infer_graph_from_sources(source_paths))

    if source_paths:
        parse(source_paths, graph_temp, **parse_kwargs)

    if render_path is not None:
        source = _io.read_graph(graph_temp)
        source = preprocess(source, **preprocess_kwargs)
        render(source, render_path, **render_kwargs)

        if graph_path is None:
            _Path(graph_temp).unlink()


def _attrs_to_dict(attrs: _List[str] = None) -> _Dict[str, str]:
    split = [attr.split(':', 1) for attr in attrs or []]
    return {n: v for n, v in split}


def main() -> None:
    """Pyfactor CLI endpoint."""
    args = _cli.parser.parse_args()

    if args.version:
        print(f'Pyfactor v.{__version__}', file=_stderr)
        exit(0)

    parse_kwargs = {
        'skip_external': args.skip_external,
        'imports': args.imports,
        'exclude': args.exclude,
        'collapse_waypoints': args.collapse_waypoints,
        'collapse_exclude': args.collapse_exclude,
        'root': args.root,
        'graph_attrs': _attrs_to_dict(args.graph_attr),
        'node_attrs': _attrs_to_dict(args.node_attr),
        'edge_attrs': _attrs_to_dict(args.edge_attr),
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
    if args.sources:
        try:
            source_paths, graph_path, render_path = _cli.parse_names(
                args.sources, args.graph, args.output
            )
        except _cli.ArgumentError as e:
            print(str(e), file=_stderr)
            exit(1)

        pyfactor(
            source_paths,
            graph_path,
            render_path,
            parse_kwargs,
            preprocess_kwargs,
            render_kwargs,
        )
    if not args.sources and not args.legend:
        _cli.parser.print_help(_stderr)
        exit(1)
