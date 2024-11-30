
=================
Hedgehog engine 2
=================

Hedgehog Engine 2 games limit themselves to a few texture types, which can make configuring
materials difficult, as many shaders use certain types differently than what their name suggests.

Here is a list of all texture types and how they are most commonly used:

.. list-table:: Texture types and their common use cases
	:widths: auto
	:header-rows: 1

	* - Type
	  - Primarily used with
	  - Occasionally used with

	* - diffuse
	  - `Albedo`_, `Falloff`_
	  - /

	* - transparency
	  - `Albedo`_
	  - `Transparency`_

	* - emission
	  - `Emission`_
	  - /

	* - reflection
	  - `Flow map`_, `Fur noise`_
	  - `Iridescence reflection`_, `Offset map`_

	* - specular
	  - `PRM`_
	  - /

	* - normal
	  - `Normal map`_
	  - /


File formats and encodings
==========================

Textures are always stored in `DDS <https://en.wikipedia.org/wiki/DirectDraw_Surface>`_ files.

HE2 is programmed with `Direct3D 11 <https://en.wikipedia.org/wiki/Direct3D#Direct3D_11>`_
(or newer), which means all DDS encodings are available for use.

More info on DDS block compression can be found
`here <https://learn.microsoft.com/en-us/windows/win32/direct3d11/texture-block-compression-in-direct3d-11>`_.

.. tip::

	HE2 games often use BC7 encoding for its higher image quality.

	If the recommended encoding does
	not give satisfying results, you can always use BC7 encoding to increase the quality, but keep
	in mind that this will also increase file size!


File streaming
--------------

Many textures in Frontiers and onwards make use of file streaming to reduce texture-load-time
and reuse the same texture between multiple archives.

The addon automatically handles those on import (if you specified the
:doc:`NTSP directory </guides/addon_config>`), but if you want to handle streamed file data
outside of blender, you can use
`NeedleTextureStreamingUtility <https://github.com/Justin113D/NeedleTextureStreamingUtility>`_.


Kinds of textures
=================

The majority of textures used by materials are one of the following kind of textures.


Albedo
-------

.. reference::

	:File suffix: 			``_abd``
	:Composition:			``RGBA``
	:Recommended encoding:	- ``BC1_UNORM`` when opaque,
 							- ``BC7_UNORM`` when transparent

.. figure:: /images/guides_material_editing_textures_he2_dif.png
	:align: right
	:figwidth: 40%

	``chr_big_fur_abd.dds`` from Sonic X Shadow Generations


Albedo textures are color-transparency textures that are sampled directly for the base
color of a material.

.. container:: lead

	.. clear


Transparency
------------

.. reference::

	:File suffix: 			``_alp``
	:Composition:			``Grayscale``
	:Recommended encoding:	``BC4_UNORM``


.. figure:: /images/guides_material_editing_textures_he2_alp.png
	:align: right
	:figwidth: 40%

	``cmnisl_blackstone501_tk1_alp.dds`` from Sonic X Shadow Generations


Transparency textures determine the transparency of a material.

Usually transparency is relayed to `Albedo`_ textures, and actual opacity textures
are only used when special alpha compositing happens.

.. container:: lead

	.. clear

Falloff
-------

.. reference::

	:File suffix: 			``_fal``
	:Composition:			``Color``
	:Recommended encoding:	``BC1_UNORM``


.. figure:: /images/guides_material_editing_textures_he2_fal.png
	:align: right
	:figwidth: 40%

	``chr_big_fur_fal.dds`` from Sonic X Shadow Generations


.. figure:: /images/guides_material_editing_textures_fal.gif
	:align: right
	:figwidth: 40%

	A camera rotating around Suzanne with a raw falloff factor.
	The albedo texture is black, and the falloff texture is white


Falloff textures change the color of the albedo texture based on the viewing angle:
The greater the angle between the camera and the surface of the model, the greater
the influence.

Depending on the shader, the falloff color either gets mixed with the albedo color or
added to it.

Additionally, shaders with falloff colors or textures basically always come with a parameter that
controls how the falloff factor gets calculated.

.. container:: lead

	.. clear


Emission
--------

.. reference::

	:File suffix: 			``_ems``
	:Composition:			``HDR``
	:Recommended encoding:	``BC6H_UF16``


.. figure:: /images/guides_material_editing_textures_he2_ems.png
	:align: right
	:figwidth: 40%

	``bos_mephiles_body_ems.dds`` from Sonic X Shadow Generations


Emission textures make parts of a model emit light. These are usually
`HDR <https://en.wikipedia.org/wiki/High_dynamic_range>`_ textures.

.. container:: lead

	.. clear


PRM
---

.. reference::

	:File suffix: 			``_prm``
	:Composition:			``RGBA``
	:Recommended encoding:	- ``BC1_UNORM`` when no alpha channel is needed
							- ``BC3_UNORM`` when alpha channel is needed


.. figure:: /images/guides_material_editing_textures_he2_prm.png
	:align: right
	:figwidth: 40%

	``chr_big_rod_prm.dds`` from Sonic X Shadow Generations


PRM textures, likely an abbreviation for "Physical rendering map", are the defacto PBR textures
of Hedgehg Engine 2 games.

If you are unfamiliar with Physically based rendering, it is recommended to
`read up on that <https://marmoset.co/posts/physically-based-rendering-and-you-can-too/>`_ before
trying to edit materials.

.. container:: lead

	.. clear

Each channel contains one PBR map:

.. list-table:: PRM channels
	:widths: 10 12 10 48 20
	:header-rows: 1
	:class: valign

	* - Channel
	  - Contents
	  - "Default" value
	  - Notes
	  - | Example from
	    | ``chr_big_rod_prm.dds``

	* - Red
	  - f0 Specular
	  - 0.5
	  -
	  - .. figure:: /images/guides_material_editing_textures_he2_prm_r.png

	* - Green
	  - Smoothness
	  - 0.8
	  - Blender uses a roughness setup, which is just the inverse of smoothness
	  - .. figure:: /images/guides_material_editing_textures_he2_prm_g.png

	* - Blue
	  - Metallic
	  - 0
	  -
	  - .. figure:: /images/guides_material_editing_textures_he2_prm_b.png

	* - Alpha
	  - Ambient Occlusion
	  - 1
	  - Many tutorials claim that AO is just multiplied into the albedo channel, which is **not** true.

	    AO gets mixed into the lighting, which is difficult to replicate in render engines like Cycles, but doable in Eevee.
	  - .. figure:: /images/guides_material_editing_textures_he2_prm_a.png


.. important::

	Older HE2 games, primarily **Sonic Forces** and **Mario & Sonic at the Rio 2016 Olympic Games** use
	a slightly different PRM setup:

	.. list-table:: PRM channels in older HE2 titles
		:widths: auto
		:header-rows: 1
		:class: valign

		* - Channel
		  - Contents
		  - Notes

		* - Red
		  - f0 Specular
		  - If the value is above 0.9, the material gets treated as completely metallic.

		* - Green
		  - Smoothness
		  - Same as above

		* - Blue
		  - Ambient Occlusion
		  -

		* - Alpha
		  - Metallic
		  - Only used in select shaders like ``MCommon``, where the specular-above-0.9 check isnt done

Normal map
----------

.. reference::

	:File suffix: 			``_nrm``
	:Composition:			``RG``
	:Recommended encoding:	``BC5_UNORM``

.. figure:: /images/guides_material_editing_textures_he2_nrm.png
	:align: right
	:figwidth: 40%

	``chr_big_rod_nrm.dds`` from Sonic X Shadow Generations

Normal map textures are used for faking bumps and dents on a model to affect lighting, falloff,
environment maps and similar.

.. note::

	As with most program, HE2 automatically calculates the blue / Z channel for normal maps when
	not provided by the encoding; Usually BC5 is used, which is a 2-component encoding and has this
	happen.

	If you end up using a 3-component encoding, like BC1 or BC7, make sure to include a
	pre-calculated blue / Z channel yourself.


.. container:: lead

	.. clear

Other
-----

Flow map
^^^^^^^^

.. reference::

	:File suffix: 			``_flw``
	:Composition:			``RG``
	:Recommended encoding:	``BC5_UNORM``


.. figure:: /images/guides_material_editing_textures_he2_flw.png
	:align: right
	:figwidth: 40%

	``chr_shadow_fur_flw.dds`` from Sonic X Shadow Generations


Flow textures are two-component textures that, similar to normal maps, encode a direction.
Each pixel determines the direction of "flow" to use when sampling the noise texture.

.. note::

	Older flow texture have a blue channel, which went unused.


.. container:: lead

	.. clear


Fur noise
^^^^^^^^^

.. reference::

	:File suffix: 			``_fur``
	:Composition:			``RGBA``
	:Recommended encoding:	``BC3_UNORM``


.. figure:: /images/guides_material_editing_textures_he2_fur.png
	:align: right
	:figwidth: 40%

	``chr_shadow_fur_fur.dds`` from Sonic X Shadow Generations


Fur noise textures get sampled based on the direction of a flow map to create a "flowing lines"
type of pattern.

The color channel gets multiplied into the albedo color, while the alpha channel determine the
specularity.

This allows for characters to have fine details without needing huge textures.

.. container:: lead

	.. clear


Iridescence reflection
^^^^^^^^^^^^^^^^^^^^^^

.. reference::

	:File suffix: 			``_ref``
	:Composition:			``Color``
	:Recommended encoding:	``BC1_UNORM``


.. figure:: /images/guides_material_editing_textures_he2_ref.png
	:align: right
	:figwidth: 40%

	``w05_ruins_biometal_ref.dds`` from Sonic X Shadow Generations


Iridescence shaders use these reflection textures to create their effect of the same name.

.. container:: lead

	.. clear


Offset map
^^^^^^^^^^

.. reference::

	:File suffix: 			``_off``
	:Composition:			``RG``
	:Recommended encoding:	``BC5_UNORM``


.. figure:: /images/guides_material_editing_textures_he2_off.png
	:align: right
	:figwidth: 40%

	``w09_btl02_poisonswamp_s3_jh1_off.dds`` from Sonic X Shadow Generations


Offset maps are basically normal maps that are used to distore another texture by shifting the
sample coordinate.

These are often used with things like water or wind.

.. container:: lead

	.. clear