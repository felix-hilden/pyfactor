"""
Script dependency visualisation.

See Readme file on `GitHub <https://github.com/felix-hilden/pyfactor>`_.
"""
import os as _os
from pathlib import Path as _Path

_version_file = _Path(_os.path.realpath(__file__)).parent / 'VERSION'
__version__ = _version_file.read_text().strip()

from ._cli import parser
from ._graph import create_graph
from ._parse import parse_refs


def main(
    source: str,
    out_path: str = None,
    file_format: str = 'pdf',
    skip_imports: bool = False,
) -> None:
    """
    Render a dependency visualisation from source.

    Parameters
    ----------
    source
        source file path
    out_path
        output file path
    file_format
        output file format
    skip_imports
        do not visualise imports (can reduce clutter)
    """
    if out_path is None:
        out_path = source + '.gv'
    source = _Path(source).read_text(encoding='utf-8')
    references, formats = parse_refs(source, skip_imports)
    graph = create_graph(references, formats)
    graph.render(out_path, view=True, format=file_format)


def cli_main():
    """Command line interface to `main`."""
    args = parser.parse_args()
    main(args.source, args.out_path, args.file_format, args.skip_imports)
