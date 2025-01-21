
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

Object
	The root of the object tree to export for the LoD level.

	The first item in the LoD info list is reserved for the object on which the LoD info is defined.

Cascade
	Distance cascade until which to display the model(?). Ranges from 0 to 31.

Unknown
	Always found to be -1. Unknown what it does.
