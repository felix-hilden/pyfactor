.. _gallery:

Gallery
=======
This gallery contains example visualisations
of builtin modules and public libraries.
Note that because the public library examples refer to specific Git commits,
they may be outdated.

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

Nodes represent different types of source objects.
Edges represent dependencies.
The node from which the arrow starts
depends on the node that the arrow head points to.

In addition to type and connectivity information the nodes contain
a line number indicating the location of the definition.
Multiple line numbers are given if the name has multiple definitions.
A single node can also be colored with two colors,
indicating for example a central leaf node.

Nodes are divided into subgraphs separated with bounding rectangles
according to their source module.

.. note::

    Docstrings are provided as tooltips: hover over nodes of the SVG image
    to view the tooltip.

Node shapes
***********
- Unknown: node type unknown for some reason
- Multiple: there are multiple definitions with different types for a name

Node colours
************
- Centrality: the number of connections that a given node has,
  deeper red indicates an increased centrality
- Waypoint: a node whose children can only be reached from its parents
  via that node
- Collapsed: waypoint with its child nodes collapsed (see CLI options)
- Leaf: has no child nodes
- Root: has no parent nodes
- Isolated: has no dependencies

Edge styles
***********
- Bridge: a dependency that when removed, would break the graph into pieces
- Import: import referencing a node in a different module
