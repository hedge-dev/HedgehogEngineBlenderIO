
.. include:: ../include.rst

.. _shaders.shadow_generations.DirectionBlend_dpndpn:
.. _shaders.shadow_generations.DirectionBlend_dpnndpn:

=======================
Direction blend shaders
=======================

These are standard PBR shaders that blend two sets of textures based on the meshes red vertex
color and slope angle.

They are a variation of the :doc:`blend shaders </game_documentation/shaders/shadow_generations/blend>`.

Shader table
------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Shader
      - | Texture
        | ":ref:`diffuse<shaders.shadow_generations.direction_blend.textures.diffuse>`"
      - | Texture
        | ":ref:`specular<shaders.shadow_generations.direction_blend.textures.specular>`"
      - | Texture
        | ":ref:`normal<shaders.shadow_generations.direction_blend.textures.normal>`"
      - | Texture
        | ":ref:`diffuse1<shaders.shadow_generations.direction_blend.textures.diffuse1>`"
      - | Texture
        | ":ref:`specular1<shaders.shadow_generations.direction_blend.textures.specular1>`"
      - | Texture
        | ":ref:`normal1<shaders.shadow_generations.direction_blend.textures.normal1>`"
      - | Texture
        | ":ref:`normal2<shaders.shadow_generations.direction_blend.textures.normal2>`"
      - | Parameter
        | ":ref:`DirectionParam<shaders.shadow_generations.direction_blend.parameters.DirectionParam>`"
      - | Parameter
        | ":ref:`NormalBlendParam<shaders.shadow_generations.direction_blend.parameters.NormalBlendParam>`"
      - | Parameter
        | ":ref:`ambient<shaders.shadow_generations.direction_blend.parameters.ambient>`"

    * - DirectionBlend_dpndpn
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      -
      - |X|
      - |X|
      - |X|

    * - DirectionBlend_dpnndpn
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
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
    Support only :ref:`transparency clipping <shaders.common.mesh_layers.punchthrough>`, and
    **not** :ref:`transparency blending <shaders.common.mesh_layers.transparent>`.

    The shader uses the final blending factor as the alpha.


.. _shaders.shadow_generations.direction_blend.behavior.texcoord:

Texture coordinates
    ``DirectionBlend_dpnndpn`` uses each textures provided texture coordinate index, while
    ``DirectionBlend_dpndpn`` uses a specific one per texture.


Multiple Tangents
    These shaders can use a second set of tangents for the second set of textures when the bool
    parameter ``enable_multi_tangent_space`` is set to true.


Vertex colors
    The red :doc:`vertex color </game_documentation/shaders/common/vertex_colors>` is used for the
    slope blending bias.

    Mysteriously, the ``DirectionBlend_dpnndpn`` shader allows the combination of the RGB channels
    by using the
    :ref:`ambient parameters <shaders.shadow_generations.direction_blend.parameters.ambient>` red
    component as a blending factor.


Texture Blending
    These shaders rely on the meshes slope angle to determine the blending factor, which is used to
    blend the two sets of textures together.

    Additionally, the red vertex color is used as a "blending bias":

    .. figure:: /game_documentation/shaders/shadow_generations/images/direction_blend_bias.png

        A sphere with two textures being blend together and a gradually increasing blending bias.

    A blending bias of 0.5 is considered the default.


Textures
--------

.. _shaders.shadow_generations.direction_blend.textures.diffuse:

diffuse
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    The alpha is used to adjust the slope blending factor via multiplication.

    Uses the 1st UV channel.
    :ref:`* <shaders.shadow_generations.direction_blend.behavior.texcoord>`


.. _shaders.shadow_generations.direction_blend.textures.specular:

specular
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Uses the 1st UV channel.
    :ref:`* <shaders.shadow_generations.direction_blend.behavior.texcoord>`


.. _shaders.shadow_generations.direction_blend.textures.normal:

normal
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 1st UV channel.
    :ref:`* <shaders.shadow_generations.direction_blend.behavior.texcoord>`


.. _shaders.shadow_generations.direction_blend.textures.diffuse1:

diffuse1
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    The alpha is used to adjust the slope blending factor via multiplication.

    Attempts to use the 3rd UV channel.
    :ref:`* <shaders.shadow_generations.direction_blend.behavior.texcoord>`


.. _shaders.shadow_generations.direction_blend.textures.specular1:

specular1
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Attempts to use the 3rd UV channel.
    :ref:`* <shaders.shadow_generations.direction_blend.behavior.texcoord>`


.. _shaders.shadow_generations.direction_blend.textures.normal1:

normal1
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 3rd UV channel.

    .. warning::
        This texture is not used in the ``BlendDetail_dpndpnn`` shader!

        Yet, a slot is required to be able to specify the
        :ref:`normal2 texture <shaders.shadow_generations.direction_blend.textures.normal2>`, even if this
        one is left empty!


.. _shaders.shadow_generations.direction_blend.textures.normal2:

normal2
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Attempts to use the UV channel specified by the textures texcoord index.

    Gets blended together with the
    :ref:`normal texture <shaders.shadow_generations.direction_blend.textures.normal>`
    (influenced by the
    :ref:`camera distance <shaders.shadow_generations.direction_blend.behavior.distance_blending>`).


Parameters
----------

.. _shaders.shadow_generations.direction_blend.parameters.DirectionParam:

DirectionParam
    A normal direction that determines which direction the slope blending starts.


.. _shaders.shadow_generations.direction_blend.parameters.NormalBlendParam:

NormalBlendParam
    A float parameter to modify the slope blend factor.

    - The first component changes the blend factors strength (multiplicative).
    - The second component raises the minimum blend factor (additive).


.. _shaders.shadow_generations.direction_blend.parameters.ambient:

ambient
    A float parameter containing a color.

    The **red component** changes the visibility of the vertex colors on the diffuse texture.

    A value of 1 hides the vertex colors, while a value of 0 makes them fully visible.
