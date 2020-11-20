import argparse

parser = argparse.ArgumentParser(
    description='Dependency visualiser refactoring tool.'
)
parser.add_argument('source', help='source file to analyse')
parser.add_argument('--out-path', '-o', help='output file name')
parser.add_argument('--file-format', '-f', default='pdf', help='output file format')
parser.add_argument(
    '--skip-imports', '-s', help='do not visualise imports', action='store_true'
)
