
.. _bpy.types.HEIO_RenderLayer:

******************
Mesh Render Layers
******************

.. reference::

	:Panel:		:menuselection:`Properties --> Mesh Properties --> HEIO Mesh Properties --> Render Layers`


``.model`` and ``.terrain-model`` files not only divide a model into sub-mesh by materials, but
also by render layers. Usually render layers and materials line up and can be specified via a
materials :ref:`render layer <HEIO_Material.render_layer>` property, but sometimes more control
is desired.

In those cases, HEIO lets you specify the render layer per polygon, just like materials, using
these render layer lists.

Each render layer list has at least 3 layers:

- ``Opaque``
- ``Transparent``
- ``Punch-Through``

These are the default render layers, and are used 99% of the time. However, some games make use of
custom "special" layers, that are specified by a name. These can be used by adding a layer and
naming it to the according layer, like "Water".