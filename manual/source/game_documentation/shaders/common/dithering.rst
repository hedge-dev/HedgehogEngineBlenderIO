
=========
Dithering
=========

.. figure:: /images/gamedoc_shaders_dithering_texture.png
	:figwidth: 160
	:width: 128
	:align: right

	The dithering texture used in Shadow Generations

.. figure:: /images/gamedoc_shaders_dithering.gif
	:figwidth: 288
	:width: 256
	:align: right

	A circle slowly dithering out (recreated in blender) (scaled up by 400%)

Dithering, specifically transparency dithering, is a technique used in shaders with alpha-clipping
(which is usually used with the
:ref:`punch-through mesh layer <shaders.common.mesh_layers.punchthrough>`) to make a fade-out effect
without having to use transparency blending.

All Hedgehog Engine 2 shaders have dithering code implemented (only confirmed for Shadow Generations
right now), but more research is required to understand under which circumstances it is used.
