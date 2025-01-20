
********************
Collision Primitives
********************

.. reference::

	:Panel:		:menuselection:`Properties --> Mesh Properties --> HEIO Mesh Properties --> Collision Primitives`

Alongside mesh shapes, ``.btmesh`` files also store "collision primitives", a set of simple,
non-polygonal shapes that can be used when performance is key, or when polygonal collision
is overkill.

The easiest way to edit a collision primitives position, rotation and scale is via the
Collision primitive edit tools.

Collision primitive properties
------------------------------

Shape type
	The type of primitive shape. There are 4 different shapes:

	- Sphere
	- Box
	- Cylinder
	- Capsule

Position
	Position of the primitive in object space

Rotation
	Rotation of the primitive in object space

Dimensions
	Dimensions of the primitive in object space.

	Utilized different depending on the shape type used.

Collision Layer
	The collision layer to use for the primitive.

	See :doc:`Collision Layer <groups>` for more info.

Collision Type
	The collision type to use for the primitive.

	See :doc:`Collision Types <collision_types>` for more info.

Collision Flags
	A list of collision flags to use on the primitive.

	See :doc:`Collision Flags <collision_flags>` for more info.