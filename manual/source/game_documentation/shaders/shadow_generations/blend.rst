
.. include:: ../include.rst

.. _shaders.shadow_generations.Blend_dpnbdpn:
.. _shaders.shadow_generations.Blend_dpndpn:
.. _shaders.shadow_generations.BlendDetail_dpndpnn:

=============
Blend shaders
=============

These are standard PBR shaders that blend two sets of textures based on the meshes alpha vertex
color.

Shader table
------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Shader
      - | Texture
        | ":ref:`diffuse<shaders.shadow_generations.blend.textures.diffuse>`"
      - | Texture
        | ":ref:`specular<shaders.shadow_generations.blend.textures.specular>`"
      - | Texture
        | ":ref:`normal<shaders.shadow_generations.blend.textures.normal>`"
      - | Texture
        | ":ref:`transparency<shaders.shadow_generations.blend.textures.transparency>`"
      - | Texture
        | ":ref:`diffuse1<shaders.shadow_generations.blend.textures.diffuse1>`"
      - | Texture
        | ":ref:`specular1<shaders.shadow_generations.blend.textures.specular1>`"
      - | Texture
        | ":ref:`normal1<shaders.shadow_generations.blend.textures.normal1>`"
      - | Texture
        | ":ref:`normal2<shaders.shadow_generations.blend.textures.normal2>`"
      - | Parameter
        | ":ref:`DetailFactor<shaders.shadow_generations.blend.parameters.DetailFactor>`"

    * - Blend_dpnbdpn
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      -
      -

    * - Blend_dpndpn
      - |X|
      - |X|
      - |X|
      -
      - |X|
      - |X|
      - |X|
      -
      -

    * - BlendDetail_dpndpnn
      - |X|
      - |X|
      - |X|
      -
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|


Behavior
--------

Standard behaviors
    - Uses the :doc:`PBR lighting model </game_documentation/shaders/common/pbr>`
    - Uses :doc:`dithering </game_documentation/shaders/common/dithering>`
    - Uses :ref:`weather <shaders.common.weather.pbr_effect>` effects


Rendering
    The shaders **only** support
    :doc:`deferred rendering </game_documentation/shaders/common/deferred_rendering>` and have not
    been compiled for forward rendering.


Transparency
    Neither :ref:`transparency clipping <shaders.common.mesh_layers.punchthrough>`, nor
    :ref:`transparency blending <shaders.common.mesh_layers.transparent>` are supported.


Multiple Tangents
    These shaders can use a second set of tangents for the second set of textures when the bool
    parameter ``enable_multi_tangent_space`` is set to true.


Vertex colors
    :doc:`Vertex colors </game_documentation/shaders/common/vertex_colors>` get combined with the
    :ref:`diffuse texture <shaders.shadow_generations.common.textures.diffuse>` via multiplication

    The alpha gets combined with the blending factor via multiplication.


Texture Blending
    The shaders use a blending factor to determine how much the two sets of textures should be blended
    together.

    - ``Blend_dpnbdpn`` uses the
      :ref:`transparency textures<shaders.shadow_generations.blend.textures.transparency>` red channel.
    - ``Blend_dpndpn`` and ``BlendDetail_dpndpnn`` rely solely on the vertex color alpha.

    Furthermore, the :ref:`diffuse1 textures<shaders.shadow_generations.blend.textures.diffuse1>`
    alpha channel influences how the diffuse textures get blended together by multiplying into the
    previous blending factor.


.. _shaders.shadow_generations.blend.behavior.distance_blending:

Distance blending
    The ``BlendDetail_dpndpnn`` shader will fade in the
    :ref:`normal2 <shaders.shadow_generations.blend.textures.normal2>` based on the distance
    between the camera and surface being rendered. The game usually starts the fade-in at a
    distance of 180, and fully fades them in at a distance of 150.


Textures
--------

.. _shaders.shadow_generations.blend.textures.diffuse:

diffuse
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.blend.textures.specular:

specular
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Uses the 1st UV channel


.. _shaders.shadow_generations.blend.textures.normal:

normal
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.blend.textures.transparency:

transparency
    The red channel is used for blending between the two texture sets.

    Uses the 4th UV channel.


.. _shaders.shadow_generations.blend.textures.diffuse1:

diffuse1
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    The alpha influences the blending between this and the
    :ref:`diffuse texture <shaders.shadow_generations.blend.textures.diffuse>`.

    Uses the 3rd UV channel.


.. _shaders.shadow_generations.blend.textures.specular1:

specular1
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Uses the 3rd UV channel.


.. _shaders.shadow_generations.blend.textures.normal1:

normal1
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 3rd UV channel.

    .. warning::
        This texture is not used in the ``BlendDetail_dpndpnn`` shader!

        Yet, a slot is required to specify the
        :ref:`normal2 texture <shaders.shadow_generations.blend.textures.normal2>`, even if this
        one is left empty!


.. _shaders.shadow_generations.blend.textures.normal2:

normal2
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Attempts to use the 4th UV channel.

    Gets blended together with the
    :ref:`normal texture <shaders.shadow_generations.blend.textures.normal>`
    (influenced by the
    :ref:`camera distance <shaders.shadow_generations.blend.behavior.distance_blending>`).


Parameters
----------

.. _shaders.shadow_generations.blend.parameters.DetailFactor:

DetailFactor
    A float parameter of which the first component scales the texture coordinates of the
    :ref:`normal2 textures <shaders.shadow_generations.blend.textures.normal2>`.