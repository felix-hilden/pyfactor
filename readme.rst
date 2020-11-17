python-package
==============
A package template for Python.

Assumed tooling
---------------
- Hosted on GitHub with a Wiki
- Pytest and Coverage for testing
- Tox and linters for static analysis
- Numpy-style ``.rst`` documentation with Sphinx (see ``docs/src/conf.py``)

Considerations
--------------
- Move documentation to ReadTheDocs:
  make a ``404.rst`` file under ``docs/src`` and
  require specific doc package versions in ``docs/requirements.txt``
- Use continuous integration like GitHub Actions or Travis
- Set up issue and pull request templates
