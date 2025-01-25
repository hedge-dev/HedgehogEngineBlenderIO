
===========
Mesh Layers
===========

In hedgehog engine games, each sub-mesh has a layer assigned that can enable or disable
certain shader features for rendering, as well as change when it gets rendered.


.. _shaders.common.mesh_layers.opaque:

Opaque
------

The default mesh layer, which completely ignores any transparency of a material.

In hedgehog Engine 2 games, this layer will attempt to use
:doc:`deferred rendering </game_documentation/shaders/common/deferred_rendering>`.


.. _shaders.common.mesh_layers.transparent:

Transparent
-----------

Will render meshes with transparency blending. Makes use of the "use additive blending" feature.


.. _shaders.common.mesh_layers.punchthrough:

Punch-through
-------------

When rendering a mesh, each rendered pixel will check if the sampled transparency is below the
materials "clip threshold". If it is, the pixel is discarded.

In hedgehog Engine 2 games, this layer will attempt to use
:doc:`deferred rendering </game_documentation/shaders/common/deferred_rendering>`.

.. figure:: /game_documentation/images/shaders_mesh_layers_punchthrough.png

	An example transparency mask (left), the mask used with transparency blending (middle) and te mask used with transparency clipping (right)