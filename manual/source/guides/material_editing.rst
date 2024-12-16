
################
Material Editing
################

.. attention::
	Please make sure you have read these guides before continuing here

	:Addon Configuration: 	:ref:`[Open] <guides-addon-configuration>` - Required to import some textures
	:Project Setup: 		:ref:`[Open] <guides-project-setup>` - Required to correctly set up materials


HEIO allows for editing .material files which can be done either in the context of a model or in
isolation.


----


Importing
=========

Usually, materials are automatically imported as part of a model or similar, but if you just
want to edit one or multiple material files, you can do so by importing them directly.


.. dropdown:: Import to project
	:icon: download

	If you just want to import materials into your project without automatically adding them to
	any model open :ref:`the importer <bpy.ops.heio.import_material>`, select your
	file(s) to import, configure the import properties and then confirm.

	.. figure:: /images/guides_material_editing_import_1.png

		Where to find the importer


.. dropdown:: Import to project and add to model
	:icon: download

	To import materials to a specific object, first select the object that the materials should be
	imported to (must be a mesh), then open
	:ref:`the importer from the specials <bpy.ops.heio.import_material_active>`,
	select your file(s) to import, configure the import properties and then confirm.

	.. figure:: /images/guides_material_editing_import_2.png

		Where to find the importer


Texture images during import
----------------------------

Images used by materials can also be imported; If ``Import images`` has been disabled in the import
properties, or an image file was not found / could not be read, the addon creates a 16x16
placeholder texture in its place based on the connection of the template material.


----


Editing
=======

The addon does **not** attempt to get export-data from the materials node tree. Instead, HEIO does
it the other way around: All edits are done from within the
:doc:`HEIO Material Panel </user_interface/object/material>`.


.. figure:: /images/guides_material_editing_panel.png

	Where to find the HEIO Materia Panel


Whenever an HEIO Material property is edited the addon will (try to) update the materials node-tree
accordingly to allow for a realtime preview, but this can only occur if the used shader
has a properly set up material template, which is not the case for the majority of shaders. For
that reason, most shaders will use a generic fallback template and may end up looking inaccurate
to ingame.

.. seealso::

	| If you are interested in contributing missing material templates, go to [TODO].
	| Every bit of help is appreciated!


Setting up the shader
---------------------

The heart of every material is its shader: A shader is essentially a small program telling the GPU
how a model gets rendered. Materials tell the game which shader to use as well as passing over
options like parameters and textures to be used by the shader.

Every game has its own list of shaders. A full list of the usable shaders for each game can be
found :doc:`here </game_documentation/shaders/index>`.

If you created a new material, it will be set up to use a
:ref:`custom shader <HEIO_Material.custom_shader>` and have no shader set. Custom Shaders are only
useful if the shader you want to use is somehow not set up for the target game, or when you want
to use a custom shader.

In 99.9% of cases, you dont need to use the custom shader feature, and can disable it.
Upon doing so, the shader name textfield will be swapped out for a dropdown.

.. figure:: /images/guides_material_editing_shader.png

	Difference between a custom shader and a preset shader


By default, the list of shaders is (usually) a small selection of commonly used shaders from
the larger shader list. If the shader you want to use is not part of the selection, enable
:ref:`"Show all shaders" <HEIO_Scene.show_all_shaders>`.

If no shader is selected, the addon will show a warning sign in the property.
Always make sure to select a shader!


Shader variants
^^^^^^^^^^^^^^^

Hedgehog Engine 1 games made use of "shader variants", which are shaders with specific
technical features, like enabling bone deformations or vertex colors. Each character in a
variant name denotes one feature, e.g. ``b`` may enable ``bone deformation``.

If a shader has variants, you can select those via a second dropdown.

.. figure:: /images/guides_material_editing_shader_variants.png

	Available shader variants for the shader ``Common_de`` for Sonic Unleashed

Each target games shader features and their purposes are documented :doc:`here </game_documentation/shader_features>`.

.. _guides_material_editing_node_setup:

Node Setup
^^^^^^^^^^

After selecting the shader (and variant) that you want to use, its time to set up the nodes.
This is done entirely automatically by the addon, and you should never have to interact with
the nodes of an HEIO material.

To generate the nodes, simply click the
:ref:`Setup/Update nodes <bpy.ops.heio.material_setup_nodes>` button.

.. figure:: /images/guides_material_editing_setup_nodes.png


Additionally, whenever you change any of the HEIO Material properties, the addon will automatically
update the values and images inside the node tree!

.. note::
	This is done automatically on import!

	You only (and **always**) have to press it after changing the shader of a material yourself.


Material Properties
-------------------

Materials have 3 types of properties that change how the shader behaves:


General
^^^^^^^

These are direct material settings that are strictly part of every material.

*Clip Threshold* and `Backface Culling <https://docs.blender.org/manual/en/latest/render/eevee/material_settings.html#bpy-types-material-use-backface-culling>`_
are default blender material properties added here for convenience and have the same effect ingame
as they do here.

:ref:`Use additive blending <HEIO_Material.use_additive_blending>` does exactly as it says: Instead
of alpha blending, it makes the shader use `additive blending <https://www.learnopengles.com/tag/additive-blending/>`_.

Parameters
^^^^^^^^^^

These are values that get passed to the shader, like a diffuse color or similar.

Every shader can define their own custom parameters, of which the usage is fully up to
the shader itself and may need fiddling and/or reverse engineering to figure out how they work.

For more detailed information about parameters, read
:doc:`HEIO Material Parameters </user_interface/object/material_parameters>`

.. note::

	All shaders, **even those that dont actually use them**, have the following parameters:

	- diffuse
	- specular
	- ambient
	- emissive
	- power_gloss_level
	- opacity_reflection_refraction_spectype

	These are legacy hedgehog engine 1 parameters, and are part of ever shader to ensure compatibility
	with every engine and tool.

.. caution::

	**Changing the shader preset** will add new parameters with their default values
	and **remove old unused parameters**. Be aware of this when trying out a different shader
	or similar!


Textures
^^^^^^^^

Textures are very simple: You have slots with certain types, and these get used by the shader for
various purposes.

For more detailed information about textures, read

- :doc:`HEIO Material Textures </user_interface/object/material_textures>`
- :doc:`Texture systems in each engine </game_documentation/textures/index>`

.. important::

	Textures are exported using the `Blender DDS Addon <https://github.com/matyalatte/Blender-DDS-Addon>`_,
	which allows you to set the DDS encoding to use when exporting for each image.

	.. figure:: /images/guides_material_editing_dds_encoding.png

		Where to find the DDS encoding settings


SCA Parameters
--------------

SCA parameters are additional information that can be attached to a file in Sonic Lost World and games
released after.

For more detailed information about SCA parameters, read

- :doc:`HEIO SCA Parameters </user_interface/sca_parameters>`
- :doc:`Material SCA parameters </game_documentation/sca_parameters>`

----


Exporting
=========

Once you are done editing your material(s), they can be exported as .material files. Usually, this
is done automatically by e.g. the model exporter, but you can also export materials independently.

.. important::

	Materials are exported to files with their names!

	E.g. a material with the name ``MySonicFur`` gets
	exported as ``MySonicFur.material``, so make sure that your materials are correctly named before
	exporting!


.. warning::

	If you want to export images too, you need to have
	`Blender DDS Addon <https://github.com/matyalatte/Blender-DDS-Addon>`_ installed!


.. dropdown:: Batch export materials
	:icon: upload

	The standard way of exporting materials is to export all materials of specific objects. Which
	objects get picked depends on the :ref:`"limit to" export properties <tools-export-common-properties>`.

	To export materials of objects, open :ref:`the exporter <bpy.ops.heio.export_material>`,
	select a directory to export to, configure the export properties and confirm.

	.. figure:: /images/guides_material_editing_export_1.png

		Where to find the exporter


	.. tip::

		.. figure:: /images/guides_material_editing_export_collection.png
			:align: right

		You can set up a `collection exporter <https://docs.blender.org/manual/en/latest/scene_layout/collections/collections.html#exporters>`_ for this process!


.. dropdown:: Export a single material
	:icon: upload

	You can export a single material by selecting it, opening
	:ref:`the exporter in the material specials <bpy.ops.heio.export_material>`,
	select a directory to export to, configure the export properties and confirm.

	.. figure:: /images/guides_material_editing_export_2.png

		Where to find the exporter