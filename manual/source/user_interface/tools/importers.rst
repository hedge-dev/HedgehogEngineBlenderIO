
*********
Importers
*********

.. note::

	Basically all importers depend on the :ref:`target game <HEIO_Scene.target_game>` and will
	alter how the import is interpreted, so make sure to configure the correct target game before
	importing anything!


Material Import
===============

.. reference::

	:File:		:menuselection:`File --> Import --> HEIO Formats --> HE Material (*.material)`

Imports HE Material files, including their textures, and sets up the materials shader nodes for an in-blender preview.

.. note::

	The materials do not get assigned to any object, and will be lost when closing the file.


Create undefined parameters/textures
	If the shader used by the material is defined by the target game, all parameters and textures
	not defined by the target game for the shader will be ignored and lost after importing.

	Enabling this option will import all parameters and textures, even if they are not defined.
	If that happens :ref:`custom shader <HEIO_Material.custom_shader>` will be enabled.


Import images
	Will attempt to load the images of a material into blender.

	.. note::
		If this is disabled, or the addon fails to load the specified image, then a 16x16 image
		with a solid color will be generated in its place.


Use existing images
	If enabled, the importer will check if blender already has an image loaded with the exact name
	and use that instead. If no image exists, the regular logic applies


Active Material Import
======================

.. reference::

	:Menu:		:menuselection:`Properties --> Material Properties --> Material Specials -> Import HE Material (*.material)`

Same as the regular Material Import, but assigns the materials to the active mesh after importing.