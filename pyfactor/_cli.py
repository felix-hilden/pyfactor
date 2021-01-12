from argparse import ArgumentParser, RawDescriptionHelpFormatter

parser = ArgumentParser(
    allow_abbrev=False,
    formatter_class=RawDescriptionHelpFormatter,
    description=(
        'Script dependency visualiser.\n\n'
        'Use cases:\n'
        '- pyfactor SOURCE      Read source file and render graph\n'
        '- pyfactor -g SOURCE   Read graph file and render\n'
        '- pyfactor SOURCE -go  Read source file, generate graph file and render\n'
        '- pyfactor SOURCE -no  Read source file, only generating graph file\n'
    ),
)

group_mode = parser.add_argument_group('Source and output')
group_mode.add_argument('source', nargs='?', default=None, help=(
    'Python source or graph file (note: use --graph-source with graphs)'
))
group_mode.add_argument('--graph-source', '-g', action='store_true', help=(
    'SOURCE is interpreted as a graph file'
))
group_mode.add_argument('--output', '-o', help=(
    'render output file name (default: generated from source file, '
    'note: --format is appended to the file name)'
))
group_mode.add_argument('--format', '-f', default='pdf', help=(
    'render file format (default: %(default)s)'
))
group_mode.add_argument(
    '--graph-output', '-go', nargs='?', default=None, const=True, help=(
        'also write intermediate graph file '
        '(note: if no value is given, name is generated from source file)'
    )
)
group_mode.add_argument('--no-output', '-no', action='store_true', help=(
    'do not generate render output (note: writes a graph file, checking '
    '--graph-output for a potential file name)'
))
group_mode.add_argument(
    '--legend', '-l', nargs='?', default=None, const='pyfactor-legend', help=(
        'render a legend (default: %(const)s)'
    )
)

group_graph = parser.add_argument_group('Graph appearance')
group_graph.add_argument(
    '--skip-imports', '-si', action='store_true', help='do not visualise imports'
)
group_graph.add_argument('--engine', '-ge', help='Graphviz layout engine')
group_graph.add_argument('--renderer', '-gr', help='Graphviz output renderer')
group_graph.add_argument('--formatter', '-gf', help='Graphviz output formatter')

group_misc = parser.add_argument_group('Miscellaneous options')
group_misc.add_argument('--open', action='store_true', help=(
    'open result in default application after rendering'
))
group_misc.add_argument(
    '--version', '-v', action='store_true', help='display version number and exit'
)
