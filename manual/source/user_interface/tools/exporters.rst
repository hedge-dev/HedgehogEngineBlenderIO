
*********
Exporters
*********

.. reference::

	:File:		:menuselection:`File --> Export --> HEIO Formats`
	:Panel:		:menuselection:`Properties --> Collection Properties --> Exporters`

.. important::

	All exporters depend on the :ref:`target game <HEIO_Scene.target_game>` and will
	alter how the export is structured, so make sure to configure the correct target game before
	exporting anything!


The addon currently supports exporting several different file formats:

- Material files ( ``*.material`` )
- Model files ( ``*.model`` )
- Terrain model files ( ``*.terrain-model`` )
- HE2 Collision mesh (or bullet mesh) files ( ``*.btmesh`` )
- HE2 Point cloud files ( ``*.pcmodel``, ``*.pccol`` )

Some exporters build on "previous" exporters, e.g. the ``.model`` exporters relies on the same
exporters logic as the ``.material`` exporters to export materials.


----

.. _tools-export-common-properties:

Common Export Properties
========================

Most exporters collect a batch of objects to export, which can be limited with a range of
properties, each reducing the objects to collect.


Selected Objects
	Ignore all unselected objects

Visible
	Ignore all hidden objects

Active Collection
	Ignore all objects outside of the active collection

Active scene
	Ignore all objects not part of the active scene


----

.. _bpy.ops.heio.export_material:

Material Export
===============

Automatic SCA parameters
	Add default SCA parameters to the material if missing (defined per target game).

	Not available for games released before Sonic Lost World.

Image export mode
	Lets you control how images are handled on export

	- ``Overwrite``: Export **all** images, even if they already exist in the output directory
	- ``Missing``: Export only images that dont already exist in the output directory
	- ``None``: Export no images at all

Invert Y channel of normal maps
	Inverts the Y (Green) channel on normal maps.

	- ``Automatic``: Inverts if the target game uses Hedgehog Engine 1
	- ``Invert``: Always inverts
	- ``Don't invert``: Does not invert


.. _bpy.ops.heio.export_material_active:

Active Material Export
----------------------

.. reference::

	:Menu:		:menuselection:`Properties --> Material Properties --> Material Specials --> Export HE Material (*.material)`

Exports only the active material.


----

Common Mesh Export Properties
=============================

Export options that apply to all model file formats.

Mesh Mode
	How to export the collected objects.

	- ``Separate``: Collected object trees get exported to individual files, like when exporting point clouds. File names are picked automatically.
	- ``Merge``: Export all collected objects to a single, specific file.

Apply modifiers
	Apply modifiers to objects before exporting.

Apply Poses
	Apply armature poses before exporting. Otherwise export with rest-poses.


----

Model / Terrain model export
============================

General
	Automatic SCA parameters
		Add default SCA parameters to the model if missing (defined per target game).

		Not available for games released before Sonic Lost World.

	Export Materials
		Whether to export materials and their images.

	Bone Orientation
		Different target games have different ways of orienting bones. HEIO corrects the bone
		orientation so that armatures can be properly posed with mirroring and more.

		For this purpose, the bone orientation can be specified on export:

		- ``Auto``: Determine the orientation based on the target game
		- ``X, Y``: Bones in the file should be X forward and Y up
		- ``X, Z``: Bones in the file should be X forward and Z up
		- ``Z, -X``: Bones in the file should be Z forward and negative X up

Advanced
	Use Triangle Strips
		Whether to export polygons using triangle strips instead of triangle lists.

		Files will be much smaller, but can cause a tiny bit of performance loss ingame.

		Only available for games released after Sonic Forces. Sonic Forces and older can only use
		triangle strips.

	Optimized Vertex Data
		Vertex data can be stored in different ways, often depending on the game. By default,
		data is stored with optimized / compressed formats, but doesn't have to.

		Not available for HE1 PC games.


----

Collision mesh export
=====================

No unique export options for collision mesh export.


----

Point cloud export
==================

Cloud type
	Type of point cloud to export.

	- ``Terrain``: Exports collected object trees as a .pcmodel file, as well as corresponding .terrain-model and .model files.
	- ``Collision``: Exports collected object trees as a .pccol file, as well as corresponding .btmesh files.

Write Resources
	Whether to evaluate and export resource files (like .terrain-model). Otherwise exports only the point cloud file.