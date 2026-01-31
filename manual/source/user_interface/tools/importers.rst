:og:description: The HEIO importers
:og:image: _images/index_user_interface.png

*********
Importers
*********

.. reference::

	:File:		:menuselection:`File --> Import --> HEIO Formats`


.. important::

	All importers depend on the :ref:`target game <bpy.types.HEIO_Scene.target_game>` and will
	alter how the import is interpreted, so make sure to configure the correct target game before
	importing anything!

The addon currently supports importing several different file formats:

- Material files ( ``*.material`` )
- Model files ( ``*.model`` )
- Terrain model files ( ``*.terrain-model`` )
- HE2 Collision mesh (or bullet mesh) files ( ``*.btmesh`` )
- HE2 Point cloud files ( ``*.pcmodel``, ``*.pccol`` )

Some importers build on "previous" importers, e.g. the ``.model`` importer relies on the same
import logic as the ``.material`` importer to import materials.

.. tip::

	All importers print a progress bar to the console, which can help estimate how long the import
	is going to take until completion!


----

.. _bpy.ops.heio.import_material:

Material Import
===============

Create undefined parameters/textures
	If the shader used by the material is defined by the target game, all parameters and textures
	not defined by the target game for the shader will be ignored and lost after importing.

	Enabling this option will import all parameters and textures, even if they are not defined.
	If that happens :ref:`custom shader <bpy.types.HEIO_Material.custom_shader>` will be enabled.


Import images
	Will attempt to load the images of a material into blender.

	.. note::
		If this is disabled, or the addon fails to load the specified image, then a 16x16 image
		with a solid color will be generated in its place.

Invert Y channel of normal maps
	Inverts the Y (Green) channel on normal maps.

	- ``Automatic``: Inverts if the target game uses Hedgehog Engine 1
	- ``Invert``: Always inverts
	- ``Don't invert``: Does not invert

Use existing images
	If enabled, the importer will check if blender already has an image loaded with the exact name
	and use that instead. If no image exists, the regular logic applies


.. _bpy.ops.heio.import_material_active:

Active Material Import
----------------------

The standalone material import creates the materials but does not add them to any object.

That is why a second material import is called, which allows you to import a material directly to
an object:

.. reference::

	:Menu:		:menuselection:`Properties --> Material Properties --> Material Specials --> Import HE Material (*.material)`


----

.. _bpy.ops.heio.import_model:

Model / Terrain model import
============================

Vertex merge mode
	How to merge vertices of the imported model.

	- ``None``: Don't merge any vertices
	- ``Per Submesh``: Merge vertices per submesh (material+render-layer)
	- ``Per Group``: Merge vertices per mesh group
	- ``All``: Merge vertices across the entire model

	Merge distance
		Distance beyond which two vertices should not be merged

	Merge split edges
		Whether to merge vertices that would result in a split edge (may mess up normals)


Additional properties
	Create render layer attributes
		Import render layers as HEIO mesh properties, instead of relying on materials.

		See :doc:`Render Layers </user_interface/object/mesh/render_layers>` for more info.


	Import LoD models
		Import Level-of-detail models if the imported file contains any.

		See :doc:`LoD Info </user_interface/object/lod_info>` for more info.

Armature
	Bone Orientation
		Different target games have different ways of orienting bones. HEIO corrects the bone
		orientation so that armatures can be properly posed with mirroring and more.

		For this purpose, the bone orientation can be specified on import:

		- ``Auto``: Determine the orientation based on the target game
		- ``X, Y``: Bones in the file are X forward and Y up
		- ``X, Z``: Bones in the file are X forward and Z up
		- ``Z, -X``: Bones in the file are Z forward and negative X up

	Bone Length Mode
		Files do not store a "Length" for bones, so HEIO has to calculate a length based on the
		distance to a bones children. This mode changes how the length gets picked.

		- ``Closest``: Use distance to closest child for length
		- ``Furthest``: Use distance to farthest child for length
		- ``Most Children``: Use distance to the child with most children itself for length
		- ``First``: Use distance to the first child for length

		If a bone has no children, the parent bones length will be used.

	Minimum bone length
		Minimum length a bone should have

	Maximum leaf bone length
		Maximum lenght a bone without children should have


----

.. _bpy.ops.heio.import_collisionmesh:

Collision mesh import
=====================

Merge vertices
	Whether to merge vertices.

	Merge distance
		Distance beyond which two vertices should not be merged.

Remove unused vertices
	Remove vertices that did not get used by any polygons on import.


----


.. _bpy.ops.heio.import_pointcloud:

Point cloud import
==================

Models as instance collections
	If an instance in a ``.pcmodel`` point cloud references a ``.model`` file, then that model will
	be imported and used as an instance collection. Otherwise, each instance in the point cloud
	will have its own armature object and mesh children.