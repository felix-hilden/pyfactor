from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser(
    allow_abbrev=False, description='Script dependency visualiser.'
)

group_mode = parser.add_argument_group('Source and output')
group_mode.add_argument('source', nargs='?', help=(
    'source file name. If source was disabled by leaving it unspecified, '
    '--graph is used as direct input for rendering. Disabling two or more of '
    'SOURCE, --graph and --output will return with an error code 1.'
))
group_mode.add_argument('--graph', '-g', nargs='?', default='-', const=None, help=(
    'write or read intermediate graph file. Graph output is disabled by default. '
    'If a value is specified, it is used as the file name. '
    'The file name is inferred from SOURCE if no value is provided. '
    'See SOURCE for more information.'
))
group_mode.add_argument('--output', '-o', help=(
    'render file name. By default the name is inferred from --graph. '
    'If the name is a single hyphen, render output is disabled '
    'and a graph is written to --graph. See SOURCE for more information. '
    'NOTE: --format is appended to the name'
))
group_mode.add_argument('--format', '-f', default='svg', help=(
    'render file format, appended to all render file names (default: %(default)s) '
    'NOTE: displaying docstring tooltips is only available in svg and cmap formats'
))
group_mode.add_argument(
    '--legend', nargs='?', default=None, const='pyfactor-legend', help=(
        'render a legend, optionally specify a file name (default: %(const)s)'
    )
)

group_parse = parser.add_argument_group('Parsing options')
group_parse.add_argument(
    '--skip-imports', '-si', action='store_true', help='do not visualise imports'
)
group_parse.add_argument(
    '--exclude', '-e', action='append', help='exclude nodes in the source'
)
group_parse.add_argument(
    '--collapse-waypoints', '-cw', action='store_true', help=(
        'remove children of waypoint nodes and mark them as collapsed'
    )
)
group_parse.add_argument(
    '--collapse-exclude', '-ce', action='append', help=(
        'exclude waypoint nodes from being collapsed'
        'when --collapse-waypoints is set'
    )
)
group_parse.add_argument(
    '--root', '-r', default=None, help=(
        'only show root and its children in the graph '
        'NOTE: does not affect graph coloring'
    )
)

group_graph = parser.add_argument_group('Graph appearance')
group_graph.add_argument(
    '--stagger', type=int, default=2, help='max Graphviz unflatten stagger'
)
group_graph.add_argument(
    '--no-fanout', action='store_true', help='disable Graphviz unflatten fanout'
)
group_graph.add_argument(
    '--chain', type=int, default=1, help='max Graphviz unflatten chain'
)
group_graph.add_argument(
    '--graph-attr', '-ga', action='append', help=(
        'Graphviz graph attributes as colon-separated name-value pairs '
        '(e.g. -ga overlap:false) NOTE: overrided by Pyfactor'
    )
)
group_graph.add_argument(
    '--node-attr', '-na', action='append', help=(
        'Graphviz node attributes as colon-separated name-value pairs '
        '(e.g. -na style:filled,rounded) NOTE: overrided by Pyfactor'
    )
)
group_graph.add_argument(
    '--edge-attr', '-ea', action='append', help=(
        'Graphviz edge attributes as colon-separated name-value pairs '
        '(e.g. -ea arrowsize:2) NOTE: overrided by Pyfactor'
    )
)
group_graph.add_argument('--engine', help='Graphviz layout engine')

group_misc = parser.add_argument_group('Miscellaneous options')
group_misc.add_argument('--view', action='store_true', help=(
    'open result in default application after rendering'
))
group_misc.add_argument(
    '--renderer', help='Graphviz output renderer'
)
group_misc.add_argument(
    '--formatter', help='Graphviz output formatter'
)
group_misc.add_argument(
    '--version', '-v', action='store_true', help='display version number and exit'
)


class ArgumentError(RuntimeError):
    """Invalid command line arguments given."""


def parse_names(source, graph, output):
    """Parse file names from arguments."""
    if source is None and (graph is None or graph == '-'):
        raise ArgumentError('Pyfactor: no input specified!')
    if graph == '-' and output == '-':
        raise ArgumentError('Pyfactor: all output disabled!')
    if source is None and output == '-':
        raise ArgumentError('Pyfactor: only graph name specified!')

    if source is None:
        g = Path(graph)
        o = Path(output) if output else g.with_suffix('')
        return None, g, o

    s = Path(source)
    if graph == '-':
        o = Path(output) if output else s.with_suffix('')
        return s, None, o
    if output == '-':
        g = Path(graph) if graph else s.with_suffix('.gv')
        return s, g, None
    else:
        g = Path(graph) if graph else s.with_suffix('.gv')
        o = Path(output) if output else g.with_suffix('')
        return s, g, o
