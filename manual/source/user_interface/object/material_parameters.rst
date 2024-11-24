
.. _bpy.ops.heio.material_parameters_add:
.. _bpy.ops.heio.material_parameters_remove:
.. _bpy.ops.heio.material_parameters_move:

*******************
Material Parameters
*******************

.. reference::

	:Panel:		:menuselection:`Properties --> Material Properties --> HEIO Material --> Parameters`

A list of parameters that either get used the shader for rendering, or that alter certain
properties of the shader.

When the material uses a :ref:`custom shader <HEIO_Material.custom_shader>`, the parameters can
be freely added, edited and removed. Otherwise they are set up based on the selected shader.


Parameter Properties
====================


.. _HEIO_MaterialParameter.name:

Name
	Name of the parameter. Cannot be empty.

	Cannot be edited when material is not using a custom shader.


.. _HEIO_MaterialParameter.value_type:

Type
	Type of the parameter

	- ``Float``: A 4-component floating point vector
	- ``Color``: ``Float`` but as a color
	- ``Boolean``: A checkbox

	.. note::
		``Color`` parameters are actually just ``Float`` parameters with a color editor. Editing
		the color will change the internal float value and vice versa.


.. _HEIO_MaterialParameter.float_value:
.. _HEIO_MaterialParameter.color_value:
.. _HEIO_MaterialParameter.boolean_type:

Value
	Value of the parameter. Depends on the type.