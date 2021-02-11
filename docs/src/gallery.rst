.. _gallery:

Gallery
=======
This gallery contains example visualisations from various public libraries.
Note that because the examples refer to specific commits, they may be outdated.

.. toctree::
   :caption: Contents
   :glob:

   gallery/*

Legend
------
Legend information is available in the image below (click to enlarge).

.. image:: gallery/legend.png
   :target: _images/legend.png
   :alt: legend visualisation

Types
*****
- Unknown: node type unknown for some reason
- Multiple: there are multiple definitions with different types for a name

Colours
*******
- Dependency: the node from which the arrow starts depends on the node
  that the arrow points to
- Bridge: a dependency that when removed, would break the graph into pieces
- Centrality: the number of connections that a given node has,
  deeper red indicates an increased centrality
- Leaf: has no child nodes
- Root: has no parent nodes
- Isolated: has no dependencies
