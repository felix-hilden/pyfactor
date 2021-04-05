.. _guide:

Guide
=====
Here are some tips and tricks to using *Pyfactor*.

Many configuration parameters are dedicated to managing
the amount of information in the graph.
While sometimes having extra information is useful,
particularly with lengthy files, nested modules and many imports
the graph structure can become messy.

Controlling imports
-------------------
Skipping external imports with ``--skip-external`` is likely the first useful
reduction of detail that can greatly simplify the visualisation.
Often tracking imports to external modules is not essential.

With lots of references to only a few import targets,
duplicating imports with ``--imports duplicate`` might consolidate imports
before referencing the original sources, which reduces inter-module edges.
Conversely if there are less references per import, resolving the nodes
with ``--imports resolve`` can reduce the number of redundant nodes.

Affecting specific nodes
------------------------
Sometimes very busy nodes can be a distraction to the overall graph.
They can be manually excluded from the visualisation with ``--exclude``.
If instead a part of the graph is particularly interesting,
a node can be set as the graph root with ``--root``.
