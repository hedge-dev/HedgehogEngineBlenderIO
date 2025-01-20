
***********
Mesh Groups
***********

.. reference::

	:Panel:		:menuselection:`Properties --> Mesh Properties --> HEIO Mesh Properties --> Groups`

Groups are used to divide a mesh into several units. HEIO does this by assign each polygon which group
to use, like a material.

Each group is only identified by a group name.


In models
---------

In ``.model`` and ``.terrain-model`` files, they are often used hide specific parts of a model when
not needed.


In collision meshes
-------------------

In ``.btmesh`` files, they are used to divide parts of a collision mesh into "shapes". The group
name does not get exported here.

Mesh groups have several properties specific to collision meshes

Collision Layer
	Determines how entities interact with the collision shape

Is Convex Collision
	Whether the shape is convex (has no "indents" or holes). This strips the shape of all polygons
	information on export, but takes less CPU power to collide with.

	Without polygons, convex shapes can only have one set of polygon specific info:

	Convex collision type
		The collision type to use on the entire convex shape.

		See :doc:`Collision Types <collision_types>` for more info.

	Convex collision flags
		A list of collision flags to use on the entire convex shape.

		See :doc:`Collision Flags <collision_flags>` for more info.
