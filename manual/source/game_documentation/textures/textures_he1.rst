
.. _textures.he1:

#################
Hedgehog engine 1
#################

Texture types
=============

Hedgehog Engine 1 games limit themselves to a few texture types (with exceptions), which can make
configuring materials difficult, as many shaders use certain types differently than what their name
suggests.

Here is a list of all texture types and how they are most commonly used:

.. list-table:: Texture types and their common use cases
	:widths: auto
	:header-rows: 1

	* - Type
	  - Primarily used with
	  - Occasionally used with

	* - diffuse
	  - `Diffuse`_
	  - `Emission`_

	* - opacity
	  - `Diffuse`_
	  - `Opacity`_

	* - reflection
	  - `Environment map`_
	  - /

	* - specular
	  - `Specular`_
	  - `Diffuse`_, `Gloss`_

	* - gloss
	  - `Gloss`_
	  - `Diffuse`_, `Specular`_

	* - normal
	  - `Normal map`_
	  - /

	* - displacement
	  - General use texture type
	  - `Falloff`_, `Emission`_


File formats and encodings
==========================

Textures are always stored in `DDS <https://en.wikipedia.org/wiki/DirectDraw_Surface>`_ files,
of which the vast majority use some form of
`block-compression <https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression>`_
encoding. Only a handful are not compressed.

Since HE1 is programmed with `Direct3D 9 <https://en.wikipedia.org/wiki/Direct3D#Direct3D_9>`_,
the number of available block compression encodings is limited to BC1, BC2 and BC3.

More info on DDS block compression can be found
`here <https://learn.microsoft.com/en-us/windows/win32/direct3d11/texture-block-compression-in-direct3d-11>`_.

.. note::

	The `Direct3D 11 mod for Sonic Generations (PC) <https://gamebanana.com/mods/407367>`_ by Skyth
	makes the game run on `Direct3D 11 <https://en.wikipedia.org/wiki/Direct3D#Direct3D_11>`_,
	which can read newer DDS encodings like BC4, BC5, BC6, BC7 and more.


Kinds of textures
=================

The majority of textures used by materials are one of the following kind of textures.


.. _textures.he1.diffuse:

Diffuse
-------

.. reference::

	:File suffix: 			``_dif``
	:Composition:			``RGBA``
	:Recommended encoding:	- ``BC1_UNORM`` when opaque
							- ``BC3_UNORM`` when transparent


.. figure:: /game_documentation/images/textures_he1_dif.png
	:align: right
	:figwidth: 40%

	``chr_sonic_body01_dif_HD.dds`` from Sonic Generations


Diffuse textures are color-transparency textures that are sampled directly for the base
color of a material.

.. container:: lead

	.. clear


.. _textures.he1.opacity:

Opacity
-------

.. reference::

	:File suffix: 			``_alp``, ``_a``, Often none
	:Composition:			``Grayscale``
	:Recommended encoding:	``BC1_UNORM``


.. figure:: /game_documentation/images/textures_he1_alp.png
	:align: right
	:figwidth: 40%

	``csc_etc_ty1_wind01_alp.dds`` from Sonic Generations


Opacity textures determine the transparency of a material.

Usually transparency is relayed to `Diffuse`_ textures, and actual opacity textures
are only used when special alpha compositing happens.

.. container:: lead

	.. clear


.. _textures.he1.falloff:

Falloff
-------

.. reference::

	:File suffix: 			``_fal``
	:Composition:			``Color``
	:Recommended encoding:	``BC1_UNORM``


.. figure:: /game_documentation/images/textures_he1_fal.png
	:align: right
	:figwidth: 40%

	``chr_sonic_body01_fal_HD.dds`` from Sonic Generations


.. figure:: /game_documentation/images/textures_fal.gif
	:align: right
	:figwidth: 40%

	A camera rotating around Suzanne with a raw falloff factor.
	The diffuse texture is black, and the falloff texture is white


Falloff textures change the color of the diffuse texture based on the viewing angle:
The greater the angle between the camera and the surface of the model, the greater
the influence.

Depending on the shader, the falloff color either gets mixed with the diffuse color or
added to it.

Additionally, shaders with falloff colors or textures basically always come with a parameter that
controls how the falloff factor gets calculated.

.. container:: lead

	.. clear


.. _textures.he1.environment_map:

Environment map
---------------

.. reference::

	:File suffix: 			``_ref``, ``_env``, ``_cube``
	:Composition:			``RGBA``
	:Recommended encoding:	- ``BC1_UNORM`` when opaque,
							- ``BC3_UNORM`` when transparent


Environment textures are used to project a fake reflection of the surroundings onto a model
based on the viewing angle.

Some get layered on top of e.g. a diffuse texture, and have an alpha
channel for their layer-transparency.

Depending on the shader, these have 3 different layouts:


.. _textures.he1.environment_map.cubemap:

Cubemap
^^^^^^^

.. figure:: /game_documentation/images/textures_he1_cm.png
	:align: right
	:figwidth: 40%

	``chr_sonic_white_ref.dds`` from Sonic Unleashed


The most detailed, and probably best known type of reflection map.
Uses 6 square areas, one for each side of a cube, to represent reflections from each axis.

.. container:: lead

	.. clear


.. _textures.he1.environment_map.sem:

Spherical environment map
^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/textures_he1_sem.png
	:align: right
	:figwidth: 40%

	``ghz_obj_kk1_giant_batabata_body_ref.dds`` from Sonic Generations


.. figure:: /game_documentation/images/textures_he1_sem.gif
	:align: right
	:figwidth: 40%

	A camera rotating **around** Suzanne with a spherical environment map


The cheapest type of reflection, which always directly faces the camera.

Also known as `MatCap <https://learn.foundry.com/modo/content/help/pages/shading_lighting/shader_items/matcap.html>`_ textures.

.. container:: lead

	.. clear


.. _textures.he1.environment_map.dpem:

Dual paraboloid environment map
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/textures_he1_dpem.png
	:align: right
	:figwidth: 40%

	``ghz_metal_yy1_sky_ref.dds`` from Sonic Generations


Effectively a full skybox composed of 2 spherical environment maps that cover the front and
back of an environment.

Covers the same area as a cubemap but with less detail.

.. container:: lead

	.. clear


.. _textures.he1.emission:

Emission
--------

.. reference::

	:File suffix: 			``_ems``, ``_lum``
	:Composition:			``Color``
	:Recommended encoding:	``BC1_UNORM``


.. figure:: /game_documentation/images/textures_he1_ems.png
	:align: right
	:figwidth: 40%

	``boss_timeeater_light_ems_HD.dds`` from Sonic Generations


Emission textures make parts of a model emit light.

.. container:: lead

	.. clear


.. _textures.he1.specular:

Specular
--------

.. reference::

	:File suffix: 			``_spc``
	:Composition:			``RGBA``
	:Recommended encoding:	``BC3_UNORM``


Specular textures contain 2 different maps:

- The `blinn phong lighting <https://en.wikipedia.org/wiki/Blinn%E2%80%93Phong_reflection_model>`_ specular color in the RGB channels
- The environment map (reflection) influence in the alpha channel

.. figure:: /game_documentation/images/textures_he1_spc_rgb.png
	:align: left
	:figwidth: 40%

	The color component of ``chr_sonic_body01_spc_HD.dds`` from Sonic Generations


.. figure:: /game_documentation/images/textures_he1_spc_a.png
	:align: right
	:figwidth: 40%

	The alpha component of ``chr_sonic_body01_spc_HD.dds`` from Sonic Generations


.. container:: lead

	.. clear


.. _textures.he1.gloss:

Gloss
-----

.. reference::

	:File suffix: 			``_pow``
	:Composition:			``Grayscale``
	:Recommended encoding:	``BC1_UNORM``


.. figure:: /game_documentation/images/textures_he1_pow.png
	:align: right
	:figwidth: 40%

	``ghz_rock_sk1_wall01_pow.dds`` from Sonic Generations


Gloss textures determine the `blinn phong lighting <https://en.wikipedia.org/wiki/Blinn%E2%80%93Phong_reflection_model>`_
specular power.

.. note::

	Almost every Hedgehog Engine 1 game calculates the gloss factor differently, which may cause
	the same gloss texture to look different in each game.


.. container:: lead

	.. clear


.. _textures.he1.normal_map:

Normal map
----------

.. reference::

	:File suffix: 			``_nrm`` (rarely ``_norm``, ``_nor``, ``_nml``)
	:Composition:			``Color``
	:Recommended encoding:	``BC1_UNORM``

.. figure:: /game_documentation/images/textures_he1_nrm.png
	:align: right
	:figwidth: 40%

	``ghz_rock_sk1_wall01_nrm.dds`` from Sonic Generations

Normal map textures are used for faking bumps and dents on a model to affect lighting, falloff,
environment maps and similar.

See :ref:`normal mapping <shaders.common.normal_mapping>` for reference.

.. note::

	Compared to blender, the green channel is inverted. This gets adjusted on import/export.


.. container:: lead

	.. clear