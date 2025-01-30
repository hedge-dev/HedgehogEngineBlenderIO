
.. _bpy.types.HEIO_SCA_Parameter:
.. _bpy.types.HEIO_Node:
.. _bpy.ops.heio.sca_parameters_add:
.. _bpy.ops.heio.sca_parameters_remove:
.. _bpy.ops.heio.sca_parameters_move:
.. _bpy.ops.heio.sca_parameters_newfrompreset:
.. _bpy.ops.heio.sca_parameters_newfrompreset.preset:

**************
SCA Parameters
**************

.. reference::

	:Bone:			:menuselection:`Properties --> Bone Properties --> HEIO Node Properties --> SCA Parameters`
	:Mesh:			:menuselection:`Properties --> Mesh Properties --> HEIO Mesh --> SCA Parameters`
	:Material:		:menuselection:`Properties --> Material Properties --> HEIO Material --> SCA Parameters`

Some games make use of ``Sample Chunk Attribute`` parameters to pass additional per-file
information to the game.

SCA Parameter Properties
========================


.. _bpy.types.HEIO_SCA_Parameter.name:

Name
	Name of the parameter. Has a size limit of 8 characters


.. _bpy.types.HEIO_SCA_Parameter.value_type:

Type
	Value type of the parameter.

	.. note::

		When exported, SCA parameters do not specify their type. Instead, when importing,
		the addon looks up if the parameter is defined by the
		:ref:`target game <bpy.types.HEIO_Scene.target_game>` and will assign the type appropriately.


.. _bpy.types.HEIO_SCA_Parameter.value:
.. _bpy.types.HEIO_SCA_Parameter.float_value:
.. _bpy.types.HEIO_SCA_Parameter.boolean_value:

Value
	Value of the parameter. All value types share the same internal value.