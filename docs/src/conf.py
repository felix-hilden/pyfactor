import os
import sys
from pathlib import Path

_root = Path(os.path.realpath(__file__)).parent.parent.parent
sys.path.insert(0, _root)

project = 'pyfactor'
author = 'Felix Hildén'
copyright = '2020, Felix Hildén'
release = Path(_root, 'pyfactor', 'VERSION').read_text().strip()

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx_rtd_theme',
]

master_doc = 'index'
exclude_patterns = ['build']
autosummary_generate = True
html_theme = 'sphinx_rtd_theme'
