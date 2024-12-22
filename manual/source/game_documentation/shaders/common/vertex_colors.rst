
=============
Vertex colors
=============

Vertex colors are just as the name implies colors stored on the vertices of a mesh.

They can be edited in blender via the `vertex paint mode <https://docs.blender.org/manual/en/latest/sculpt_paint/vertex_paint/introduction.html>`_.

Use as base color
-----------------

Their default use is to multiply their color into the base color of a material:

.. figure:: /images/gamedoc_shaders_vertex_colors_default.png
	:figwidth: 75%

	A material without (left) and with (right) vertex colors applied to the base color via multiplication in blender


.. important::

	While not easily viewable, vertex colors do have an alpha channel, which can affect the
	transparency of a material!


Masking and blending
--------------------

The second most common use case for vertex colors is to mask or blend multiple layers of textures:

.. figure:: /images/gamedoc_shaders_vertex_colors_blending.png
	:figwidth: 75%

	Vertex colors (left) used to blend two different textures together (right) in blender


There are also many other applications for vertex colors, but how and which channel gets used
depends entirely on each shader.