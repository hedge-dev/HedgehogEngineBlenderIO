:og:description: The general HEIO viewport tools
:og:image: _images/index_user_interface.png

==============
General Tools
==============

.. reference::

	:Viewport:	:menuselection:`Sidebar --> HEIO Tools --> General Tools`

Various tools that are useful for editing.


----

.. _bpy.ops.heio.split_meshgroups:

Split mesh by groups
--------------------

Split a mesh into multiple mesh objects by its :doc:`mesh groups </user_interface/object/mesh/groups>`.


.. _bpy.ops.heio.split_meshgroups.root_mesh_copy:

Root mesh copy
	Create a copy of the mesh before splitting. Otherwise, the original mesh will be cleared from
	the split geometry.


.. _bpy.ops.heio.split_meshgroups.origins_to_bounding_box_centers:

Origins to bounding box centers
	Place the origins of the split objects at the center of the geometry, instead of remaining where
	it originall was.


.. _bpy.ops.heio.split_meshgroups.remove_empty_splits:

Remove empty splits
	Remove splits that ended up empty


.. _bpy.ops.heio.split_meshgroups.remove_empty_info:

Remove empty info
	Leave mesh info (groups, render layers, etc.) on the split uninitialized if it ends up empty either way.


.. _bpy.ops.heio.split_meshgroups.split_collision_primitives:

Split collision primitives
	Split each collision primitive on the mesh into its own mesh (can make editing their position
	and rotation easier)


.. _bpy.ops.heio.merge_submeshes:

Merge meshes as groups
----------------------

Merge a meshes child mesh objects into itself while retaining
:doc:`mesh groups </user_interface/object/mesh/groups>`,
:doc:`render layers </user_interface/object/mesh/render_layers>` and other HEIO mesh info.

.. _bpy.ops.heio.merge_submeshes.root_mesh_copy:

Root mesh copy
	Create a copy of the mesh before merging its children into it. Otherwise, the original mesh
	will be overwritten.


.. _bpy.ops.heio.collision_primitives_to_geometry:

Collision primitives to geometry
--------------------------------

Convert collision primitives into polygonal geometry on the mesh they are stored on.


.. _bpy.ops.heio.collision_primitives_to_geometry.mesh_copy:

Root mesh copy
	Create a copy of the mesh before converting the primitives. Otherwise, the original mesh
	will be overwritten.


.. _bpy.ops.heio.collision_primitives_to_geometry.resolution:

Resolution
	Polygon resolution level of round primitives.

----

.. _bpy.ops.heio.reimport_images:

Reimport missing images
-----------------------

Attempt to reimport images that failed to import before.