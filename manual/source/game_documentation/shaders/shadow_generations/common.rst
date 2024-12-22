
.. _shaders.shadow_generations.Common_d:
.. _shaders.shadow_generations.Common_dither_dpn:
.. _shaders.shadow_generations.Common_dn:
.. _shaders.shadow_generations.Common_dp:
.. _shaders.shadow_generations.Common_dpn:
.. _shaders.shadow_generations.Common_dpna:

==============
Common shaders
==============

These are the standard, non-emission PBR shaders. For emission PBR shaders, see :doc:`Emission Shaders<emission>`.


Shader table
------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Shader
      - | Texture
        | ":ref:`diffuse<shaders.shadow_generations.common.textures.diffuse>`"
      - | Texture
        | ":ref:`specular<shaders.shadow_generations.common.textures.specular>`"
      - | Texture
        | ":ref:`normal<shaders.shadow_generations.common.textures.normal>`"
      - | Texture
        | ":ref:`transparency<shaders.shadow_generations.common.textures.transparency>`"
      - | Parameter
        | ":ref:`PBRFactor<shaders.shadow_generations.common.parameters.PBRFactor>`"
      - | Parameter
        | ":ref:`diffuse<shaders.shadow_generations.common.parameters.diffuse>`"

    * - ``Common_d``
      - :octicon:`x`
      -
      -
      -
      - :octicon:`x`
      -

    * - ``Common_dp``
      - :octicon:`x`
      - :octicon:`x`
      - :octicon:`x`
      -
      -
      -

    * - ``Common_dn``
      - :octicon:`x`
      -
      - :octicon:`x`
      -
      - :octicon:`x`
      -

    * - ``Common_dpn``
      - :octicon:`x`
      - :octicon:`x`
      - :octicon:`x`
      -
      -
      -

    * - ``Common_dither_dpn``
      - :octicon:`x`
      - :octicon:`x`
      - :octicon:`x`
      -
      -
      - :octicon:`x`

    * - ``Common_dpna``
      - :octicon:`x`
      - :octicon:`x`
      - :octicon:`x`
      - :octicon:`x`
      -
      -


Behavior
--------

Transparency
    No alpha blending occurs. Pixels with a transparency below the materials transparency threshold
    get clipped/discarded.


Vertex colors
    The shader combines the vertex color, including the alpha channel, with the
    :ref:`diffuse texture <shaders.shadow_generations.common.textures.diffuse>` via multiplication.


Weather
    PBR properties get altered by the games
    :ref:`weather parameters <shaders.common.weather.pbr_effect>`.


Dithering
    The ``Common_dither_dpn`` shader uses a different dithering texture for forced transparency
    dithering. It also completely ignores the materials transparency threshold.


Textures
--------

.. _shaders.shadow_generations.common.textures.diffuse:

diffuse
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    Uses alpha channel for transparency.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.common.textures.specular:

specular
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.common.textures.normal:

normal
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 3rd UV channel.


.. _shaders.shadow_generations.common.textures.transparency:

transparency
    A standard :ref:`transparency texture <textures.he2.transparency>`.

    Combined with alpha from the diffuse texture via multiplication.

    Uses the 4th UV channel.


Parameters
----------

.. _shaders.shadow_generations.common.parameters.PBRFactor:

PBRFactor
    A float parameter that acts as replacement for the missing
    :ref:`specular texture <shaders.shadow_generations.common.textures.specular>`.

    - X is the :ref:`specular <shaders.common.pbr.specular>` value
    - Y is the :ref:`smoothness <shaders.common.pbr.smoothness>` value
    - Z is the :ref:`metallic <shaders.common.pbr.metallic>` value


.. _shaders.shadow_generations.common.parameters.diffuse:

diffuse
    A float parameter containing a color.

    Exclusive to the ``Common_dither_dpn`` shader, which combines the alpha channel with the
    :ref:`diffuse texture <shaders.shadow_generations.common.textures.diffuse>` via multiplication.