
###############
Asset exporting
###############

.. attention::
	Please make sure you have read these guides before continuing here

	:Addon Configuration: 	:ref:`[Open] <guides-addon-configuration>`
	:Project Setup: 		:ref:`[Open] <guides-project-setup>`


Materials
=========

Once you are done editing your material(s), they can be exported as .material files. Usually, this
is done automatically by e.g. the model exporter, but you can also export materials independently.

.. important::

	Materials are exported to files with their names!

	E.g. a material with the name ``MySonicFur`` gets
	exported as ``MySonicFur.material``, so make sure that your materials are correctly named before
	exporting!

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


Texture images during export
----------------------------

Textures are exported using the
`Blender DDS Addon <https://github.com/matyalatte/Blender-DDS-Addon>`_ addon, so you need to have
that installed if you want to do so.

It should be noted that HE2 games often use BC6 or BC7 encoding, which can take very long to export
for large textures. If you did not edit any textures, it'd be best if you don't export them at all
by disabling image export and instead use the original files.

.. figure:: /images/guides_asset_exporting_materia_images_disable.png

	How to disable image exporting
