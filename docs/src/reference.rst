.. _reference:

Reference
=========
This document contains the command line help and public API of *Pyfactor*.

Command line interface
----------------------
.. argparse::
   :ref: pyfactor._cli.parser
   :prog: pyfactor

High-level Python API
---------------------
.. autofunction:: pyfactor.pyfactor
.. autofunction:: pyfactor.legend

Low-level Python API
--------------------
.. autofunction:: pyfactor.parse
.. autofunction:: pyfactor.preprocess
.. autofunction:: pyfactor.render
.. autofunction:: pyfactor.create_legend
