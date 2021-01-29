from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser(
    allow_abbrev=False, description='Script dependency visualiser.'
)

group_mode = parser.add_argument_group('Source and output')
group_mode.add_argument('names', nargs='?', default=None, help=(
    'a colon-delimited sequence of file names source:graph:render. '
    'Hyphens (-) DISABLE input/output (e.g. do not write a graph: s:-:r). '
    'If source is disabled, graph is used as the only input instead. '
    'Disabling two or more components will return with an error code 1. '
    'Empty graph and render names (e.g. s::) are INFERRED from source and graph, '
    'respectively. Source must never be empty. '
    'Several SHORTCUTS are possible by omitting components: '
    's = s:-:, s:r = s:-:r, -:g = -:g:, s:- = s::-'
))
group_mode.add_argument('--format', '-f', default='pdf', help=(
    'render file format, appended to all render file names (default: %(default)s)'
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
        '(e.g. -ga overlap:false) NOTE: overrides attributes set by Pyfactor'
    )
)
group_graph.add_argument(
    '--node-attr', '-na', action='append', help=(
        'Graphviz node attributes as colon-separated name-value pairs '
        '(e.g. -na style:filled,rounded) NOTE: overrides attributes set by Pyfactor'
    )
)
group_graph.add_argument(
    '--edge-attr', '-ea', action='append', help=(
        'Graphviz edge attributes as colon-separated name-value pairs '
        '(e.g. -ea arrowsize:2) NOTE: overrides attributes set by Pyfactor'
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


def parse_names(names):
    """Parse file names from arguments."""
    split = names.split(':')

    if sum(s == '-' for s in split) > 1:
        raise ArgumentError(f'Pyfactor: too many disabled names in `{names}`!')
    if split[0] == '' or (split[0] == '-' and split[1] == ''):
        raise ArgumentError(f'Pyfactor: cannot infer names from `{names}`!')
    if len(split) > 3:
        raise ArgumentError(f'Pyfactor: too many names in `{names}`!')

    # Expand to three components
    if len(split) == 1:
        split += ['-', '']
    if len(split) == 2:
        if split[0] == '-':
            split += ['']
        elif split[1] == '-':
            split.insert(1, '')
        else:
            split.insert(1, '-')

    # Parse components
    if split[0] == '-':
        g = Path(split[1])
        r = Path(split[2]) if split[2] else g.with_suffix('')
        return None, g, r
    elif split[1] == '-':
        s = Path(split[0])
        r = Path(split[2]) if split[2] else s.with_suffix('')
        return s, None, r
    elif split[2] == '-':
        s = Path(split[0])
        g = Path(split[1]) if split[1] else s.with_suffix('.gv')
        return s, g, None
    else:
        s = Path(split[0])
        g = Path(split[1]) if split[1] else s.with_suffix('.gv')
        r = Path(split[2]) if split[2] else g.with_suffix('')
        return s, g, r
