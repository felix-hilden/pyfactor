.. _reference:

Reference
=========
This document contains the command line help and public API of *Pyfactor*.

Command line interface
----------------------
.. argparse::
   :ref: pyfactor._parser
   :prog: pyfactor

High-level Python API
---------------------
.. autofunction:: pyfactor.parse
.. autofunction:: pyfactor.render
.. autofunction:: pyfactor.create_legend

Low-level Python API
--------------------
.. autofunction:: pyfactor.read_source
.. autofunction:: pyfactor.parse_refs
.. autofunction:: pyfactor.create_graph
.. autofunction:: pyfactor.write_graph
.. autofunction:: pyfactor.read_graph
