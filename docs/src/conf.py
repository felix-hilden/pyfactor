import os
import sys
import textwrap
import subprocess

import requests
import pyfactor
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
    'sphinxarg.ext',
]

master_doc = 'index'
exclude_patterns = ['build']
autosummary_generate = True
html_theme = 'sphinx_rtd_theme'

# ----- Generate gallery entries -----
gallery_path = _root / 'docs' / 'src' / 'gallery'
gallery_examples = [
    'felix-hilden/pyfactor/522f3ee5/pyfactor/_parse.py',
    'pydot/pydot/5c9b2ce7/pydot.py',
    'PyCQA/flake8/6de8252c/src/flake8/style_guide.py',
    'psf/black/692c0f50/src/black/__init__.py',
    'agronholm/sphinx-autodoc-typehints/2fac99f4/sphinx_autodoc_typehints.py',
    'pytest-dev/pytest/d5df8f99/src/_pytest/python.py',
]


def gallery_doc(name: str, url: str) -> str:
    """Generate gallery docs from template."""
    summary = f'This example was generated from `{name} source <{url}>`_'
    summary = '\n'.join(textwrap.wrap(summary, width=79))
    return f""".. _gallery-{name}:

{name}
{'=' * len(name)}
{summary}
with :code:`pyfactor source.py --format png --skip-imports`.
Click the image to enlarge.

.. image:: {name}.png
   :target: ../_images/{name}.png
   :alt: {name} visualisation
"""


# Hack for RTD: install Graphviz
if os.environ.get('PYFACTOR_RTD_BUILD', False):
    install_proc = subprocess.run(['apt', 'install', 'graphviz'])
    setup_proc = subprocess.run(['dot', '-c'])

# Generate legend
legend_path = gallery_path / 'legend'
pyfactor.legend(str(legend_path), {'chain': 1}, {'format': 'png'})

# Generate examples
gallery_path.mkdir(exist_ok=True)
for example in gallery_examples:
    print('Generating gallery example:', example)
    raw_url = 'https://raw.githubusercontent.com/' + example
    url_parts = example.split('/')
    url_parts.insert(2, 'blob')
    ui_url = 'https://github.com/' + '/'.join(url_parts)
    repository_name = url_parts[1]

    source_text = requests.get(raw_url).text
    doc_text = gallery_doc(repository_name, ui_url)

    source_path = gallery_path / (repository_name + '.py')
    doc_path = source_path.with_suffix('.rst')
    image_path = source_path.with_suffix('')

    source_path.write_text(source_text, encoding='utf-8')
    doc_path.write_text(doc_text, encoding='utf-8')

    pyfactor.pyfactor(
        str(source_path), None, str(image_path),
        parse_kwargs={'skip_imports': True},
        preprocess_kwargs={'stagger': 10, 'fanout': True, 'chain': 5},
        render_kwargs={'format': 'png'},
    )
