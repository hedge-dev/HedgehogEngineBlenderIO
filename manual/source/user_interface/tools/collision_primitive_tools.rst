:og:description: The HEIO tools for editing collision primitives
:og:image: _images/index_user_interface.png

.. _bpy.ops.heio.collision_primitive_gizmo_clicked:
.. _bpy.ops.heio.collision_primitive_move:
.. _bpy.ops.heio.collision_primitive_rotate:
.. _bpy.ops.heio.collision_primitive_viewrotate:
.. _bpy.ops.heio.collision_primitive_scale:

*************************
Collision primitive tools
*************************

.. hint::
	A proper guide for editing collision primitives can be found in the
	:doc:`collision mesh editing guide </guides/collision_mesh_editing>`.

Workspace tools
===============

To make working with collision primitives possible, HEIO adds two new workspace tools:

Select collision primitives
---------------------------

Allows you to select primitives on the active object by clicking them


Transform collision primitives
------------------------------

An extension to the tool above, but lets you transform the primitive using gizmos for

- Translation
- Rotation
- Scaling


Snapping
--------

When using a collision primitive tool, two new operators will be added to the snap menu:


.. _bpy.ops.heio.snap_active_collision_primitive_to_cursor:

Active collision primitive to cursor
	Places the active collision primitive at the cursor


.. _bpy.ops.heio.snap_cursor_to_active_collision_primitive:

Cursor to active collision primitive
	Places the cursor at the active collision primitive