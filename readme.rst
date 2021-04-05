========
Pyfactor
========
|build| |documentation|

Welcome to the GitHub repository of *Pyfactor*
- a refactoring tool that `visualises <rtd-gallery_>`_
Python source files, modules and importable packages as a graph of dependencies
between Python constructs like variables, functions and classes.

.. code:: sh

    $ pyfactor --help
    $ pyfactor script.py
    $ pyfactor script.py --skip-external --view

See our `PyPI`_ page for installation instructions and package information.
Visit our online documentation on `Read The Docs`_
for reference documentation, examples and release notes.

Contributing
============
New contributors are always welcome!
If you've found a bug or would like to propose a feature,
please submit an `issue <https://github.com/felix-hilden/pyfactor/issues>`_.
If you'd like to get
`more involved <https://opensource.guide/how-to-contribute/>`_,
you can start by cloning the most recent version from GitHub
and installing it as an editable package with development dependencies.

.. code:: sh

   $ git clone https://github.com/felix-hilden/pyfactor
   $ cd pyfactor
   $ pip install -e .[dev]

For specialised uses, sets of extras can be installed separately.
``tests`` installs dependencies related to executing tests,
``docs`` is for building documentation locally,
and ``checks`` contains ``tox`` and tools for static checking.
The install can be verified by running all essential tasks with tox.

.. code:: sh

    $ tox

Now tests have been run and documentation has been built.
A list of all individual tasks can be viewed with their descriptions.

.. code:: sh

    $ tox -a -v

Please have a look at the following sections for additional information
regarding specific tasks and configuration.

Documentation
-------------
Documentation can be built locally with Sphinx.

.. code:: sh

    $ cd docs
    $ make html

The main page ``index.html`` can be found in ``build/html``.
If tox is installed, this is equivalent to running ``tox -e docs``.

Code style
----------
A set of code style rules is followed.
To check for violations, run ``flake8``.

.. code:: sh

    $ flake8 pyfactor

Style checks for docstrings and documentation files are also available.
To run all style checks use ``tox -e lint``.

Running tests
-------------
The repository contains a suite of test cases
which can be studied and run to ensure the package works as intended.

.. code:: sh

    $ pytest

For tox, this is the default command when running e.g. ``tox -e py``.
To measure test coverage and view uncovered lines or branches run ``coverage``.

.. code:: sh

    $ coverage run
    $ coverage report

This can be achieved with tox by running ``tox -e coverage``.

.. |build| image:: https://github.com/felix-hilden/pyfactor/workflows/CI/badge.svg
   :target: https://github.com/felix-hilden/pyfactor/actions
   :alt: build status

.. |documentation| image:: https://rtfd.org/projects/pyfactor/badge/?version=latest
   :target: https://pyfactor.rtfd.org/en/latest
   :alt: documentation status

.. _pypi: https://pypi.org/project/pyfactor
.. _read the docs: https://pyfactor.rtfd.org
.. _rtd-gallery: https://pyfactor.rtfd.org/en/stable/gallery.html
