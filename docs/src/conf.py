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
    'sphinx.ext.extlinks',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx_rtd_theme',
    'sphinxarg.ext',
]

master_doc = 'index'
exclude_patterns = ['build']
autosummary_generate = True
html_theme = 'sphinx_rtd_theme'

extlinks = {
    'issue': ('https://github.com/felix-hilden/pyfactor/issues/%s', '#'),
}

# ----- Generate gallery entries -----
gallery_path = _root / 'docs' / 'src' / 'gallery'
public_examples = [
    'felix-hilden/pyfactor/522f3ee5/pyfactor/_parse.py',
    'pydot/pydot/5c9b2ce7/pydot.py',
    'PyCQA/flake8/e0116d8e/src/flake8/style_guide.py',
    'psf/black/c702588d/src/black/__init__.py',
    'agronholm/sphinx-autodoc-typehints/49face65/sphinx_autodoc_typehints.py',
    'pytest-dev/pytest/0061ec55/src/_pytest/python.py',
]
builtin_examples = ['concurrent', 'json', 'importlib']


def public_doc(name: str, url: str) -> str:
    """Generate public module gallery docs from template."""
    summary = f'This example was generated from `{name} source <{url}>`_'
    summary = '\n'.join(textwrap.wrap(summary, width=79))
    return f""".. _gallery-{name}:

{name}
{'=' * len(name)}
{summary}
with :code:`pyfactor source.py --skip-external`.
Click the image to enlarge.

.. image:: {name}.svg
   :target: ../_images/{name}.svg
   :alt: {name} visualisation
"""


def builtin_doc(name: str) -> str:
    """Generate builtin module gallery docs from template."""
    summary = f'This example was generated from the builtin ``{name}`` module'
    summary = '\n'.join(textwrap.wrap(summary, width=79))
    return f""".. _gallery-{name}:

{name}
{'=' * len(name)}
{summary}
with :code:`pyfactor {name} --skip-external`.
Click the image to enlarge.

.. image:: {name}.svg
   :target: ../_images/{name}.svg
   :alt: {name} visualisation
"""


# Hack for RTD: install Graphviz
if os.environ.get('PYFACTOR_RTD_BUILD', False):
    install_proc = subprocess.run(['apt', 'install', 'graphviz'])
    setup_proc = subprocess.run(['dot', '-c'])

# Generate legend
legend_path = gallery_path / 'legend'
pyfactor.legend(str(legend_path), {'chain': 2}, {'format': 'svg'})

# Generate examples
gallery_path.mkdir(exist_ok=True)
parse_kwargs = {'skip_external': True}
preprocess_kwargs = {'stagger': 10, 'fanout': True, 'chain': 5}
render_kwargs = {'format': 'svg'}

for example in public_examples:
    print('Generating gallery example:', example)
    raw_url = 'https://raw.githubusercontent.com/' + example
    url_parts = example.split('/')
    url_parts.insert(2, 'blob')
    ui_url = 'https://github.com/' + '/'.join(url_parts)
    repository_name = url_parts[1]

    source_text = requests.get(raw_url).text
    doc_text = public_doc(repository_name, ui_url)

    source_path = gallery_path / (repository_name + '.py')
    doc_path = source_path.with_suffix('.rst')
    image_path = source_path.with_suffix('')
    source_path = source_path.with_name(repository_name + '_example.py')

    source_path.write_text(source_text, encoding='utf-8')
    doc_path.write_text(doc_text, encoding='utf-8')

    pyfactor.pyfactor(
        [str(source_path)], None, str(image_path),
        parse_kwargs=parse_kwargs,
        preprocess_kwargs=preprocess_kwargs,
        render_kwargs=render_kwargs,
    )

for example in builtin_examples:
    print('Generating gallery example:', example)
    doc_text = builtin_doc(example)
    image_path = gallery_path / example
    doc_path = image_path.with_suffix('.rst')
    doc_path.write_text(doc_text, encoding='utf-8')

    pyfactor.pyfactor(
        [example], None, str(image_path),
        parse_kwargs=parse_kwargs,
        preprocess_kwargs=preprocess_kwargs,
        render_kwargs=render_kwargs,
    )
