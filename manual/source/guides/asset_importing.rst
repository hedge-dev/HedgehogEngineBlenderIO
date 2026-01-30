:og:description: Importing assets from files
:og:image: _images/index_asset_importing.png

###############
Asset importing
###############

.. attention::
	Please make sure you have read these guides before continuing here

	:Addon Configuration: 	:ref:`[Open] <guides-addon-configuration>`
	:Project Setup: 		:ref:`[Open] <guides-project-setup>`


.. tip::

	All importers print a progress bar to the console, which can help estimate how long the import
	is going to take until completion!


Materials
=========

Materials are stored in .material files, and accompanied by .texset and .texture files in
Hedgehog engine 1 games.

Usually, materials are automatically imported as part of a model or similar, but if you just
want to edit one or multiple material files, you can do so by importing them directly.

.. dropdown:: How to import .material files
	:icon: download

	If you just want to import materials into your project without automatically adding them to
	any model open :ref:`the importer <bpy.ops.heio.import_material>`, select your
	file(s) to import, configure the import properties and then confirm.

	.. figure:: images/asset_importing_material_1.png

		Where to find the importer


.. dropdown:: How to import .material files and add to a model
	:icon: download

	To import materials to a specific object, first select the object that the materials should be
	imported to (must be a mesh), then open
	:ref:`the importer from the specials <bpy.ops.heio.import_material_active>`,
	select your file(s) to import, configure the import properties and then confirm.

	.. figure:: images/asset_importing_material_2.png

		Where to find the importer


Texture images during import
----------------------------

Images are stored as .dds files.

Those used by materials can also be imported; If ``Import images`` has been disabled in the import
properties, or an image file was not found / could not be read, the addon creates a 16x16
placeholder texture in its place based on the connection of the template material.


Models
======

Models are stored in ``.model`` files, and are imported as armatures with one or more meshes. Models
consist of mesh units, each of which references a material by name. HEIO will try to import those
automatically when importing models.

Usually models are imported standalone, but can also be part of a ``.pcmodel`` file.

.. dropdown:: How to import .model files
	:icon: download

	Open :ref:`the importer <bpy.ops.heio.import_model>`, select your
	file(s) to import, configure the import properties and then confirm.

	.. figure:: images/asset_importing_model.png

		Where to find the importer


Terrain models
--------------

Terrain models, stored in ``.terrain-model`` files, are nearly identical to models, with only 3 differences:

- They have no armature, and thus no weights
- They have no morph models
- They have an internal resource name and special flags

While they too can be imported standalone, they are usually part of ``.pcmodel`` files (HE2) or
referenced by ``.terrain-instanceinfo`` files (HE1) (not yet supported)

They are imported the same way that ``.model`` files are.


Collision meshes
================

Collision meshes, specifically HE2 bullet meshes, are stored in ``.btmesh`` files.

Collision meshes usually part of a ``.pcmodel`` file, but can also be imported standalone.

.. dropdown:: How to import .btmesh files
	:icon: download

	Open :ref:`the importer <bpy.ops.heio.import_collision_mesh>`, select your
	file(s) to import, configure the import properties and then confirm.

	.. figure:: images/asset_importing_bulletmesh.png

		Where to find the importer


Point Clouds
============

Point clouds are responsible for

- Placing stage geometry (``*.pcmodel``)
- Placing stage collisions (``*.pccol``)
- Placing stage light (``*.pclt``) (not yet supported)

When imported, HEIO will also attempt to import the referenced resource files, such as

- ``*.pcmodel``: ``*.terrain-model``, ``*.model``
- ``*.pccol``: ``*.btmesh``
- ``*.pclt``: ``*.light`` (not yet supported)

.. dropdown:: How to import .pcmodel / .pccol files
	:icon: download

	Open :ref:`the importer <bpy.ops.heio.import_point_cloud>`, select your
	file(s) to import, configure the import properties and then confirm.

	.. figure:: images/asset_importing_pointcloud.png

		Where to find the importer