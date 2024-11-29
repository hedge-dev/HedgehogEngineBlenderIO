
*********
Exporters
*********

.. note::

	Basically all exporters depend on the :ref:`target game <HEIO_Scene.target_game>` and will
	alter how the export is structured, so make sure to configure the correct target game before
	exporting anything!


.. tip::

	All exporters found under the :menuselection:`File --> Export` menu can be configured as
	collection exporters too!


.. _tools-export-common-properties:

Common Export Properties
========================

Most exporters collect a batch of data before exporting, which can be limited with a range of
properties, each reducing the objects to collect.


Selected Objects
	Ignore all unselected objects

Visible
	Ignore all hidden objects

Active Collection
	Ignore all objects outside of the active collection

Active scene
	Ignore all objects not part of the active scene


.. _bpy.ops.heio.export_material:

Material Export
===============

.. reference::

	:File:		:menuselection:`File --> Export --> HEIO Formats --> HE Material (*.material)`


Batch exports materials.

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
======================

.. reference::

	:Menu:		:menuselection:`Properties --> Material Properties --> Material Specials --> Export HE Material (*.material)`

Exports only the active material.

Export properties are the same as for the regular Material Export