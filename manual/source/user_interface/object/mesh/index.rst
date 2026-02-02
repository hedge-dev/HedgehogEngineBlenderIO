:og:description: The HEIO mesh properties user interface
:og:image: _images/index_user_interface.png

.. _bpy.ops.heio.mesh_info_initialize:
.. _bpy.ops.heio.mesh_info_delete:
.. _bpy.ops.heio.mesh_info_assign:
.. _bpy.ops.heio.collision_flag_remove:
.. _bpy.ops.heio.mesh_info_de_select.select:
.. _bpy.ops.heio.mesh_info_de_select:
.. _bpy.ops.heio.mesh_info_add:
.. _bpy.ops.heio.mesh_info_remove:
.. _bpy.ops.heio.mesh_info_move:

***************
Mesh Properties
***************

.. reference::

	:Panel:		:menuselection:`Properties --> Mesh Properties --> HEIO Mesh Properties`

Meshes can hold many different properties, some of which are only used for specific export types.

.. container:: global-index-toc

	.. toctree::
		:maxdepth: 1

		export_settings
		groups
		render_layers
		collision_flags
		collision_types
		collision_primitives

General properties
------------------

- :doc:`Export Settings <export_settings>`
- :doc:`Groups <groups>`

Visual model properties
-----------------------

Properties that affect .model and .terrain-model export

- :doc:`Render Layers <render_layers>`
- :doc:`LOD Info </user_interface/object/lod_info>`
- :doc:`SCA Parameters </user_interface/object/sca_parameters>`

Collision mesh properties
-------------------------

Properties that affect .btmesh export

- :doc:`Collision Types <collision_types>`
- :doc:`Collision Flags <collision_flags>`
- :doc:`Collision Primitives <collision_primitives>`