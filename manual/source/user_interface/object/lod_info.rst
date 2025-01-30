
.. _bpy.types.HEIO_LODInfo:
.. _bpy.types.HEIO_LODInfoLevel:
.. _bpy.types.HEIO_Armature:

.. _bpy.ops.heio.lod_info_initialize:
.. _bpy.ops.heio.lod_info_delete:
.. _bpy.ops.heio.lod_info_add:
.. _bpy.ops.heio.lod_info_remove:
.. _bpy.ops.heio.lod_info_move:

********
LoD Info
********

.. reference::

	:Armature:		:menuselection:`Properties --> Armature Properties --> HEIO Armature --> LoD Info`
	:Mesh:			:menuselection:`Properties --> Mesh Properties --> HEIO Mesh --> LoD Info`

HE2 games can store multiple models in a single .model or .terrain-model file, which are displayed
at varying distances from the camera to reduce the time needed to display the model.

These models are referred to as "Level of detail" models, or short LoD, and are a common method
of optimization in modern games.

LoD Info item
=============

.. _bpy.types.HEIO_LODInfoLevel.target:

Target
	The root of the object tree to export for the LoD level.

	The first item in the LoD info list is reserved for the object on which the LoD info is defined.


.. _bpy.types.HEIO_LODInfoLevel.cascade:

Cascade
	Distance cascade until which to display the model. Ranges from 0 to 31.


.. _bpy.types.HEIO_LODInfoLevel.unknown:

Unknown
	Always found to be -1. Unknown what it does.
