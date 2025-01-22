
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

Root mesh copy
	Create a copy of the mesh before splitting. Otherwise, the original mesh will be cleared from
	the split geometry.

Origins to bounding box centers
	Place the origins of the split objects at the center of the geometry, instead of remaining where
	it originall was.

Remove empty splits
	Remove splits that ended up empty

Split collision primitives
	Split each collision primitive on the mesh into its own mesh (can make editing their position
	and rotation easier)


.. _bpy.ops.heio.merge_submeshes:

Merge meshes as groups
----------------------

Merge a meshes child mesh objects into itself while retaining
:doc:`mesh groups </user_interface/object/mesh/groups>`,
:doc:`render layers </user_interface/object/mesh/render_layers>` and other HEIO mesh info.

Root mesh copy
	Create a copy of the mesh before merging its children into it. Otherwise, the original mesh
	will be overwritten.


Collision primitives to geometry
--------------------------------

Convert collision primitives into polygonal geometry on the mesh they are stored on.

Root mesh copy
	Create a copy of the mesh before converting the primitives. Otherwise, the original mesh
	will be overwritten.

Resolution
	Polygon resolution level of round primitives.


----

.. _bpy.ops.heio.material_setup_nodes:

Setup/Update Nodes
------------------

Set up the nodes of multiple materials based on their shader.

More information about setting up nodes can be found :ref:`in the guides <guides_material_editing_node_setup>`


----

Reimport missing images
-----------------------

Attempt to reimport images that failed to import before.