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

.. image:: gallery/legend.svg
   :target: _images/legend.svg
   :alt: legend visualisation

In addition to type and connectivity information the nodes contain
a line number indicating the location of the definition.
Multiple line numbers are given if the name has multiple definitions.
A single node can also be colored with two colors,
indicating for example a central leaf node.

.. note::

    Docstrings are provided as tooltips: hover over nodes of the SVG image
    to view the tooltip.

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
- Waypoint: a node whose children can only be reached from its parents
  via that node
- Collapsed: waypoint with its child nodes collapsed (see CLI options)
- Leaf: has no child nodes
- Root: has no parent nodes
- Isolated: has no dependencies
