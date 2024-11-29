
******************
Material Templates
******************

Stored in ``MaterialTemplates.blend``, this is where the addon will look up node setups for
each shader, copy it over to the material and fill it with textures and parameters.

Basics
======

Every material in the file is a template. Despite not needing to be attached to an object,
it's recommended to set up a dummy object to hold all the materials.

Every templates file should also have at least a ``FALLBACK`` material, which is used
whenever a shader does not have its own template set up yet.

.. figure:: /images/target_configuration_material_template_example.png

	Example: The FALLBACK material setup for Shadow Generations

Node Setups
===========

First and foremost, the addon accesses and modifies nodes by their name (not their label!), so make
sure to correctly name nodes that interface with parameters and textures!

Every template must also include 4 UV map nodes named ``UV0`` through ``UV3``.


Parameter Nodes
---------------

Float and color parameters can be assigned to multiple different types of nodes:

- An `RGB node <https://docs.blender.org/manual/en/latest/render/shader_nodes/input/rgb.html>`_
- A `combine color node <https://docs.blender.org/manual/en/latest/render/shader_nodes/converter/combine_color.html>`_ (in RGB mode)
- A `combine XYZ node <https://docs.blender.org/manual/en/latest/render/shader_nodes/converter/combine_xyz.html>`_
- A `value node <https://docs.blender.org/manual/en/latest/render/shader_nodes/input/value.html>`_ (gets filled with the x/red value)
- A `value node <https://docs.blender.org/manual/en/latest/render/shader_nodes/input/value.html>`_ with the name followed by ``.w`` or ``.a`` (gets filled with the w/alpha value)

Boolean parameters can only be assigned to `value node <https://docs.blender.org/manual/en/latest/render/shader_nodes/input/value.html>`_,
which receives a ``1`` if the parameter is set to ``true``, and otherwise a ``0``.

Texture Nodes
-------------

To properly make use of textures, you need to set up 3 nodes, of which their names need to end
with the :ref:`texture type name <HEIO_MaterialTexture.name>` they are set up for.

.. figure:: /images/target_configuration_material_template_texture_example.png

	example for a texture nodes setup


.. important::

	If a shader has a texture type more than once, and you want to make use of the second or
	even third texture entry, you need to append the occurrance index to the end of the type.

	For example, if you have 3 ``diffuse`` textures, the first one remains as is, while the
	second one uses ``diffuse1`` and the third one uses ``diffuse2``.


The Image node
	An `image texture node <https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/image.html>`_
	with the name ``Texture`` (e.g. ``Texture diffuse``) for sampling the actual image.

	.. warning::

		Make sure to set the extension mode of the node to ``Extend``!

	The image node also has special behavior regarding its label: By default, images are loaded as
	sRGB images, which is often not desired. To load images with a different color space, add the
	name of the color mode to the start of the label followed by a ``;``.

	For example: A normalmap texture would get an image texture node with the name ``Texture normal`` and
	the label ``Non-Color; Texture normal``.


The "Has Texture" node
	A `value node <https://docs.blender.org/manual/en/latest/render/shader_nodes/input/value.html>`_
	with the name ``Has Texture`` (e.g. ``Has Texture diffuse``), which receives a ``1`` if an
	image is provided, otherwise ``0``.


The UV Tiling node
	A `group node <https://docs.blender.org/manual/en/latest/render/shader_nodes/groups.html>`_
	with the ``HEIO UV Tiling`` node tree and the name ``Tiling`` (e.g. ``Tiling diffuse``) that
	gets connected to the image nodes vector input.

	You can append the node tree it from any of the default target definitions by HEIO. It
	replaces the texture wrapping to make per-axis wrapping possible.
