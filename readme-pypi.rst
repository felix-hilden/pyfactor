========
Pyfactor
========
|python|

Welcome to the GitHub repository of *Pyfactor* - a refactoring tool
that `visualises <rtd-gallery_>`_ Python source files as a graph of
dependencies between Python constructs like variables, functions and classes.

.. code:: sh

    $ pyfactor --help
    $ pyfactor script.py
    $ pyfactor script.py --skip-imports --view

Visit our online documentation on `Read The Docs`_
for reference documentation, examples and release notes.
If you've found a bug or would like to propose a feature,
please submit an issue on `GitHub`_.

Installation
============
*Pyfactor* can be installed from the Package Index via ``pip``.

.. code:: sh

    $ pip install pyfactor

**Additionally**, *Pyfactor* depends on a free graph visualisation software
`Graphviz <https://graphviz.org/>`_, available for Linux, Windows and Mac.
See also the documentation of the `Graphviz Python package
<https://graphviz.readthedocs.io/en/stable/#installation>`_ for more help.

Release notes
=============
Release notes can be found on our
`Read The Docs site <https://pyfactor.rtfd.org/page/release-notes.html>`_.

.. |python| image:: https://img.shields.io/pypi/pyversions/pyfactor
   :alt: python version

.. _read the docs: https://pyfactor.rtfd.org
.. _rtd-gallery: https://pyfactor.rtfd.org/en/stable/gallery.html
.. _github: https://github.com/felix-hilden/pyfactor
