
.. include:: ../include.rst

.. _shaders.shadow_generations.Common_d:
.. _shaders.shadow_generations.Common_dither_dpn:
.. _shaders.shadow_generations.Common_dn:
.. _shaders.shadow_generations.Common_dp:
.. _shaders.shadow_generations.Common_dpn:
.. _shaders.shadow_generations.Common_dpna:

==============
Common shaders
==============

These are the standard non-emission PBR shaders. For emission PBR shaders, see :doc:`emission shaders<emission>`.


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
      - |x|
      -
      -
      -
      - |x|
      -

    * - ``Common_dp``
      - |x|
      - |x|
      - |x|
      -
      -
      -

    * - ``Common_dn``
      - |x|
      -
      - |x|
      -
      - |x|
      -

    * - ``Common_dpn``
      - |x|
      - |x|
      - |x|
      -
      -
      -

    * - ``Common_dither_dpn``
      - |x|
      - |x|
      - |x|
      -
      -
      - |x|

    * - ``Common_dpna``
      - |x|
      - |x|
      - |x|
      - |x|
      -
      -


Behavior
--------

Standard behaviors
    - Supports :doc:`deferred rendering </game_documentation/shaders/common/deferred_rendering>`
    - Supports :ref:`transparency blending <shaders.common.mesh_layers.transparent>`
    - Supports :ref:`transparency clipping <shaders.common.mesh_layers.punchthrough>`
    - Uses the :doc:`PBR lighting model </game_documentation/shaders/common/pbr>`
    - Uses :doc:`dithering </game_documentation/shaders/common/dithering>`
    - Uses :ref:`weather <shaders.common.weather.pbr_effect>` effects
    - :doc:`Vertex colors </game_documentation/shaders/common/vertex_colors>`, including alpha,
      get combined with the
      :ref:`diffuse texture <shaders.shadow_generations.common.textures.diffuse>` via
      multiplication


Common_dither_dpn
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

    Attempts to use the 3rd UV channel.


.. _shaders.shadow_generations.common.textures.transparency:

transparency
    A standard :ref:`transparency texture <textures.he2.transparency>`.

    Combined with alpha from the diffuse texture via multiplication.

    Attempts to use the 4th UV channel.


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

    Exclusive to the ``Common_dither_dpn`` shader, which combines the **alpha component** with the
    :ref:`diffuse textures <shaders.shadow_generations.common.textures.diffuse>` alpha channel via
    multiplication.
