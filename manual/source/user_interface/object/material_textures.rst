:og:description: The HEIO Material textures user interface
:og:image: _images/index_user_interface.png

.. _bpy.ops.heio.material_textures_add:
.. _bpy.ops.heio.material_textures_remove:
.. _bpy.ops.heio.material_textures_move:
.. _bpy.types.HEIO_MaterialTexture:

*****************
Material Textures
*****************

.. reference::

	:Panel:		:menuselection:`Properties --> Material Properties --> HEIO Material --> Textures`

A list of textures that the material uses for rendering.

When the material uses a :ref:`custom shader <bpy.types.HEIO_Material.custom_shader>`, the parameters can
be freely added, edited and removed. Otherwise they are set up based on the selected shader.

Texture Properties
==================


.. _bpy.types.HEIO_MaterialTexture.name:

Type Name
	Type name of the texture. Cannot be empty.

	Cannot be edited when material is not using a custom shader.

	.. note::

		Some shaders use the same texture type multiple times! If that is the case, the order
		of textures is important and changes how same-named textures get used!


.. _bpy.types.HEIO_MaterialTexture.image:

Image
	Image to use for the texture.

	.. note::
		Some shaders allow for empty images, and some don't, which could cause glitches if no image
		is provided.


.. _bpy.types.HEIO_MaterialTexture.texcoord_index:

Texture coordinate index
	The UVmap to use (0-based index).


.. _bpy.types.HEIO_MaterialTexture.wrapmode_u:
.. _bpy.types.HEIO_MaterialTexture.wrapmode_v:

Wrapmode U & V
	How the texture should be sampled after exceeding the 0-1 uv range.

	- ``Repeat``: Repeats the texture
	- ``Mirror``: Mirrors the texture every time a wrapping point is reached.
	- ``Clamp``: Clamps the sampled uv to 0-1.
	- ``Mirror Once``: Combination of ``Mirror`` and ``Clamp``
	- ``Border``: Like ``Clamp``, but once the 0-1 range is exceeded, a static color is used.

	.. note::
		Blender does currently not support sampling a texture differently for each axis, for which
		a workaround has been implemented that simulates the wrapping modes. Unfortunately, this
		is not perfect and can sometimes cause minor artifacts.