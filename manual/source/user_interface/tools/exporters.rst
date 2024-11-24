
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


Common Export Properties
========================

Most exporters collect a batch of data before exporting, which can be limited with a range of
properties, each reducing the objects to collect.


Selected Objects
	Ignore all unselected objects

Visible
	Ignore all hidden objects

Active Collection
	Ignore all objects outside active collection

Active scene
	Ignore all objects not part of the active scene


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


Active Material Export
======================

.. reference::

	:Menu:		:menuselection:`Properties --> Material Properties --> Material Specials -> Export HE Material (*.material)`

Exports only the active material.

Export properties are the same as for the regular Material Export