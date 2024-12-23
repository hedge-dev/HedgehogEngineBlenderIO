
.. include:: ../include.rst

.. _shaders.shadow_generations.Detail_dpndpn:
.. _shaders.shadow_generations.Detail_dpnn:

==============
Detail shaders
==============

Detail shaders are basically standard PBR shaders that blend in a second set of textures based on
how close the camera is to the surface.

Shader table
------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Shader
      - | Texture
        | ":ref:`diffuse<shaders.shadow_generations.detail.textures.diffuse>`"
      - | Texture
        | ":ref:`specular<shaders.shadow_generations.detail.textures.specular>`"
      - | Texture
        | ":ref:`normal<shaders.shadow_generations.detail.textures.normal>`"
      - | Texture
        | ":ref:`diffuse1<shaders.shadow_generations.detail.textures.diffuse1>`"
      - | Texture
        | ":ref:`specular1<shaders.shadow_generations.detail.textures.specular1>`"
      - | Texture
        | ":ref:`normal1<shaders.shadow_generations.detail.textures.normal1>`"
      - | Parameter
        | ":ref:`DetailFactor<shaders.shadow_generations.detail.parameters.DetailFactor>`"

    * - Detail_dpndpn
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|

    * - Detail_dpndpn
      - |X|
      - |X|
      - |X|
      -
      -
      - |X|
      - |X|


Behavior
--------

Standard behaviors
    - **Only** uses :doc:`deferred rendering </game_documentation/shaders/common/deferred_rendering>`
    - Does **not** support :ref:`transparency blending <shaders.common.mesh_layers.transparent>`
    - Supports :ref:`transparency clipping <shaders.common.mesh_layers.punchthrough>`
    - Uses the :doc:`PBR lighting model </game_documentation/shaders/common/pbr>`
    - Uses :doc:`dithering </game_documentation/shaders/common/dithering>`
    - Uses :ref:`weather <shaders.common.weather.pbr_effect>` effects


.. _shaders.shadow_generations.detail.behavior.distance_blending:

Distance blending
    The shader will fade in the second set of textures
    (:ref:`diffuse1 <shaders.shadow_generations.detail.textures.diffuse1>`,
    :ref:`specular1 <shaders.shadow_generations.detail.textures.specular1>`,
    :ref:`normal1 <shaders.shadow_generations.detail.textures.normal1>`) based on the distance
    between the camera and surface being rendered. The game usually starts fading textures in at a
    distance of 180, and fully fades them in at a distance of 150.


Textures
--------

.. _shaders.shadow_generations.detail.textures.diffuse:

diffuse
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    Uses alpha channel for transparency.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.detail.textures.specular:

specular
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.detail.textures.normal:

normal
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.detail.textures.diffuse1:

diffuse1
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    Attempts to use the 3rd UV channel.

    The RGB channels get "overlaid" over
    :ref:`diffuse <shaders.shadow_generations.detail.textures.diffuse>`
    (influenced by the
    :ref:`camera distance <shaders.shadow_generations.detail.behavior.distance_blending>`).

    .. figure:: /images/gamedoc_shaders_overlay_ref.png
        :figwidth: 75%

        An image overlaid over various base colors


.. _shaders.shadow_generations.detail.textures.specular1:

specular1
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Attempts to use the 3rd UV channel.

    Each channel affects the base of the
    :ref:`specular texture <shaders.shadow_generations.detail.textures.specular>` differently
    (influenced by the
    :ref:`camera distance <shaders.shadow_generations.detail.behavior.distance_blending>`):

    - Specular is ignored
    - Smoothness is overlaid over the base (see
      :ref:`diffuse1 <shaders.shadow_generations.detail.textures.diffuse1>`)
    - Metallic is remapped to range from -1 to 1 and then added to the base
    - Ambient occlusion is multiplied to the base


.. _shaders.shadow_generations.detail.textures.normal1:

normal1
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Attempts to use the 3rd UV channel.

    Gets blended together with the
    :ref:`normal texture <shaders.shadow_generations.detail.textures.normal>`
    (influenced by the
    :ref:`camera distance <shaders.shadow_generations.detail.behavior.distance_blending>`).


Parameters
----------

.. _shaders.shadow_generations.detail.parameters.DetailFactor:

DetailFactor
    A float parameter of which the first component scales the texture coordinates of the second
    texture set (:ref:`diffuse1 <shaders.shadow_generations.detail.textures.diffuse1>`,
    :ref:`specular1 <shaders.shadow_generations.detail.textures.specular1>`,
    :ref:`normal1 <shaders.shadow_generations.detail.textures.normal1>`).