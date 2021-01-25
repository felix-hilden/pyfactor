========
Pyfactor
========
Welcome to the documentation of *Pyfactor*
- a refactoring tool that visualises Python source files as a graph of
dependencies between Python constructs like variables, functions and classes.

.. code:: sh

    $ pyfactor --help
    $ pyfactor script.py
    $ pyfactor script.py --skip-imports --view

See our `PyPI`_ page for installation instructions and package information.
If you've found a bug or would like to propose a feature,
please submit an issue on `GitHub`_.

For a glimpse into what is possible, here's a graph of our parsing module:

.. image:: gallery/pyfactor.png
   :target: _images/pyfactor.png
   :alt: pyfactor visualisation

More examples can be found in our :ref:`gallery`.

*Pyfactor* is fundamentally a command line tool.
However, the functionality is also exposed for use in code.
See :ref:`reference` for more information.

Motivation
==========
*Pyfactor* exists to make refactoring long scripts easier
and understanding large code bases quicker.
Seeing a graph makes it possible to easily discover structure in the code
that is harder to grasp when simply reading the file,
especially for those that are not intimately familiar with the code.
For example, such a graph could reveal collections of definitions
or connection hubs that could be easily extracted to sub-modules,
or give insight into the code's complexity.

Still, simply moving definitions around into several files
is not the be-all end-all of refactoring and code style.
It is up to the user to make decisions,
but *Pyfactor* is here to help!

.. toctree::
   :hidden:
   :caption: Pyfactor

   release-notes
   reference
   gallery

.. _pypi: https://pypi.org/project/pyfactor
.. _github: https://github.com/felix-hilden/pyfactor
