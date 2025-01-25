
================================
Physically Based Rendering (PBR)
================================

Physically based rendering is used in HE2 games and mostly associated with
:ref:`"PRM"<textures.he2.prm>` textures. By combining several textures
of various properties, you can create a wide range of materials to render physically accurate
looking surfaces.


Components
----------

.. _shaders.common.pbr.albedo:

Albedo
^^^^^^

Albedo is the base color of a surface and is used with "diffuse" lighting.

.. figure:: /game_documentation/images/shaders_pbr_albedo.png

	Materials with various albedo colors in Shadow Generations


.. _shaders.common.pbr.smoothness:

Smoothness
^^^^^^^^^^

Smoothness determines how reflective a surface is. The lower the smoothness, the blurrier the
reflection. This is represented by a value between 0 and 1.

.. figure:: /game_documentation/images/shaders_pbr_smoothness.png

	Materials with full specularity and a gradually increasing smoothness in Shadow Generations


.. _shaders.common.pbr.specular:

Specular
^^^^^^^^

Specularity is less a physical property and moreso an artistic tool for creating materials.
Hedgehog Engine 2 specifically makes use of "F0 reflectance".

Seperately from diffuse lighting, specular lighting controls the visibility of specular lighting
and reflections. You can imagine it as a "layer" on top of the diffuse lighting, with the
specularity acting as the "layer transparency".

It's represented by a value between 0 and 1; Usually a specular value of 0.125 is considered the
"default".

.. figure:: /game_documentation/images/shaders_pbr_specular.png

	Gold-ish (#FFAA00) materials with a gradually increasing specularity in Shadow Generations


.. important::

	When used in a ``PBRFactor`` shader parameter, the specular value is used as is.

	In PRM textures however, it is divided by 4. Thus, the highest specular value achievable
	with a standard image format is 0.25.

	This can be circumvented by using using an HDR image format such as ``R16G16B16A16_FLOAT``.


.. _shaders.common.pbr.metallic:

Metallic
^^^^^^^^

Metallic is similar to specular, with the 2 differences:

- The albedo color affects the color of reflection
- A more linear value progression

Similarly to specular, it also can be seen as a seperate "layer" that is placed above the specular
lighting.

It too is represented by a value between 0 and 1. Usually a metallic value of 0 is considered the "default".

.. figure:: /game_documentation/images/shaders_pbr_metallic.png

	Gold-ish (#FFAA00) materials with a gradually increasing metallicness in Shadow Generations


.. tip::

	Usually, metallic is done either 0 or 1, and rarely anything in between.


.. _shaders.common.pbr.specular_and_metallic:

Combining Specular and Metallic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While rarely done, it is possible to use specular and metallic lighting together.

.. figure:: /game_documentation/images/shaders_pbr_specular_metallic.png

	Gold-ish (#FFAA00) materials with a smoothness of 0.85 and gradually increasing specularity and metallicness in Shadow Generations


.. _shaders.common.pbr.emission:

Emission
^^^^^^^^

Emission is essentially the colored "glow" of the surface, like the light coming from a lamp.
This is unaffected by any lighting that may hit the surface.

.. figure:: /game_documentation/images/shaders_pbr_emission.png

	Black materials with various emission colors in Shadow Generations


Unlike the other surface values, emission supports high-dynamic-range images, and can use values
beyond the 0-1 range, which the rendering engine may process in various ways.

Additionally, emission is often accompanied by a "Luminance" parameter that changes how bright
the emission texture appears.

.. figure:: /game_documentation/images/shaders_pbr_luminance.png

	Black materials with white emission and gradually increasing luminance in Shadow Generations


.. _shaders.common.pbr.ambient_occlusion:

Ambient occlusion
^^^^^^^^^^^^^^^^^

Ambient occlusion (often abbrivated with "AO" or "A/O") is, as the name implies, responsible for
occluding/removing ambient lighting.

In Hedgehog Engine 2 games, ambient lighting consists of

- Global illumination (GI)
- Environment reflections ("Image based lighting"; IBL)
- Screen space reflections (SSR)

Ambient occlusion too is represented by a value between 0 and 1. However, unlike the other values,
where a higher greater value "increases" the effect, here a lower value increases the occlusion of
ambient lighting.

Thus the default value, at which no ambient light is occluded, is 1.

.. figure:: /game_documentation/images/shaders_pbr_ambient_occlusion.png

	Gold-ish (#FFAA00) materials with different lighting values and gradually decreasing ambient occlusion in Shadow Generations


.. note::

	Note how, in the chart above, the "sun" in the reflection is still visible. That is because it
	is a sun light, and not actually part of the environmental reflections.


Ambient occlusion is often used to simulate shadows in narrow spaces and corners, as ambient light
is more likely to get trapped in such spaces.

.. figure:: /game_documentation/images/shaders_pbr_ao_composition.png

	An example scene of how ambient occlusion looks in practive (rendered with blender cycles)

.. dropdown:: Compositing setup used above
	:icon: workflow

	.. figure:: /game_documentation/images/shaders_pbr_ao_composition_nodes.png


Examples
--------

Now, with all the info above, even moreso when combined with :doc:`Normal maps<normal_mapping>`, we can
create a wide range of materials to use!

Let's look at some examples:


Example 1: ARK Techno Panels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/shaders_pbr_example_1.png

	``m01_techno_panel_emsa_sy1`` from the ARK in Shadow Generations


Example 2: Rail Canyon Asphalt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/shaders_pbr_example_2.png

	``m06_ds_asphalt_base_sy1`` from Rail Canyon in Shadow Generations


Example 3: Kingdom Valley Wood bark
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/shaders_pbr_example_3.png

	``m03_kdv_wood02_dfsp_n_ih1`` from Kingdom Valley in Shadow Generations


Example 4: Sunset Heights Building wall
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/shaders_pbr_example_4.png

	``m06_ds_wall_window18_fh1`` from Sunet Heights in Shadow Generations


Example 5: Chaos Island Rock cliff
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/shaders_pbr_example_5.png

	``m05_rockcliff01_sy1`` (top layer) from Chaos Island in Shadow Generations


Example 6: Radical Highway Tunnel Wall
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /game_documentation/images/shaders_pbr_example_6.png

	``m06_ds_tunnel_d_kk1`` from Radical Highway in Shadow Generations