
.. include:: ../include.rst

.. _shaders.shadow_generations.Emission_dE:
.. _shaders.shadow_generations.Emission_dpE:
.. _shaders.shadow_generations.Emission_dpnE:
.. _shaders.shadow_generations.Emission_dpnEa:
.. _shaders.shadow_generations.EmissionTone_dapnE:
.. _shaders.shadow_generations.EmissionTone_dpnE:
.. _shaders.shadow_generations.EmissionTone_E:
.. _shaders.shadow_generations.EmissionToneOpAnim_dpnE:

================
Emission shaders
================

These are the standard emission PBR shaders. For non-emission PBR shaders, see :doc:`common shaders<common>`.

Shader table
------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Shader
      - | Texture
        | ":ref:`diffuse<shaders.shadow_generations.emission.textures.diffuse>`"
      - | Texture
        | ":ref:`specular<shaders.shadow_generations.emission.textures.specular>`"
      - | Texture
        | ":ref:`normal<shaders.shadow_generations.emission.textures.normal>`"
      - | Texture
        | ":ref:`transparency<shaders.shadow_generations.emission.textures.transparency>`"
      - | Texture
        | ":ref:`emission<shaders.shadow_generations.emission.textures.emission>`"
      - | Parameter
        | ":ref:`PBRFactor<shaders.shadow_generations.emission.parameters.PBRFactor>`"
      - | Parameter
        | ":ref:`Luminance<shaders.shadow_generations.emission.parameters.Luminance>`"
      - | Parameter
        | ":ref:`diffuse<shaders.shadow_generations.emission.parameters.diffuse>`"

    * - Emission_dE
      - |x|
      -
      -
      -
      - |x|
      - |x|
      - |x|
      -

    * - Emission_dpE
      - |x|
      - |x|
      -
      -
      - |x|
      -
      - |x|
      -

    * - Emission_dpnE
      - |x|
      - |x|
      - |x|
      -
      - |x|
      -
      - |x|
      -

    * - Emission_dpnEa
      - |x|
      - |x|
      - |x|
      - |x|
      - |x|
      -
      - |x|
      -

    * - EmissionTone_dapnE
      - |x|
      - |x|
      - |x|
      - |x|
      - |x|
      -
      - |x|
      -

    * - EmissionTone_dpnE
      - |x|
      - |x|
      - |x|
      - |x|
      -
      -
      - |x|
      -

    * - EmissionTone_E
      -
      -
      -
      -
      - |x|
      - |x|
      - |x|
      -

    * - EmissionToneOpAnim_dpnE
      - |x|
      - |x|
      - |x|
      -
      - |x|
      -
      - |x|
      - |x|


Behavior
--------

Standard behaviors
    - Supports :doc:`deferred rendering </game_documentation/shaders/common/deferred_rendering>`
    - Supports :ref:`transparency blending <shaders.common.mesh_layers.transparent>`
    - Supports :ref:`transparency clipping <shaders.common.mesh_layers.punchthrough>`
    - Uses the :doc:`PBR lighting model </game_documentation/shaders/common/pbr>`
    - Uses :doc:`dithering </game_documentation/shaders/common/dithering>`
    - Uses :ref:`weather <shaders.common.weather.pbr_effect>` effects


Vertex colors
    :doc:`Vertex colors </game_documentation/shaders/common/vertex_colors>`, **excluding** alpha,
    get combined with the
    :ref:`diffuse texture <shaders.shadow_generations.emission.textures.diffuse>` via
    multiplication

    **Exceptions:**

    - ``EmissionTone_E``, which does not have a diffuse texture, uses only the vertex color alpha
      for transparency.
    - ``EmissionTone_dapnE`` uses the vertex color alpha for transparency (combined with
      :ref:`diffuse <shaders.shadow_generations.emission.textures.diffuse>` alpha via
      multiplication)
    - ``Emission_dpnEa`` uses the vertex color alpha for transparency (combined with
      :ref:`diffuse <shaders.shadow_generations.emission.textures.diffuse>` alpha via
      multiplication) **and** combines it with the
      :ref:`luminance <shaders.shadow_generations.emission.parameters.luminance>` via
      multiplication.


Tone
    The shaders that include "Tone" in their name get their luminance adjusted by the average
    brightness of the screen.

    This behavior is not reproducible in blender.


Textures
--------

.. _shaders.shadow_generations.emission.textures.diffuse:

diffuse
    A standard :ref:`albedo texture <textures.he2.albedo>`.

    Uses alpha channel for transparency.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.emission.textures.specular:

specular
    A standard :ref:`PRM texture <textures.he2.prm>`.

    Uses the 1st UV channel.


.. _shaders.shadow_generations.emission.textures.normal:

normal
    A standard :ref:`normal map texture <textures.he2.normal_map>`.

    Uses the 1st UV channel.

    **Exceptions:**

    - ``Emission_dpnE`` attempts to use the 3rd UV channel


.. _shaders.shadow_generations.emission.textures.transparency:

transparency
    This texture is used differently between shaders:

    - ``EmissionTone_dapnE`` uses it as a standard
      :ref:`transparency texture <textures.he2.transparency>`.

      It's combined with alpha from the
      :ref:`diffuse texture <shaders.shadow_generations.emission.textures.diffuse>` via multiplication.

    - ``Emission_dpnEa`` uses it to alter the
      :ref:`luminance <shaders.shadow_generations.emission.parameters.luminance>`
      via multiplication.

    Attempts to use the 4th UV channel.


.. _shaders.shadow_generations.emission.textures.emission:

emission
    A standard :ref:`emission texture <textures.he2.emission>`.

    Attempts to use the 3rd UV channel.

    **Exceptions:**

    - ``EmissionTone_E`` uses the 1st UV channel
    - ``Emission_dpnE`` attempts to use the 4th UV channel


Parameters
----------

.. _shaders.shadow_generations.emission.parameters.PBRFactor:

PBRFactor
    A float parameter that acts as replacement for the missing
    :ref:`specular texture <shaders.shadow_generations.emission.textures.specular>`.

    - X is the :ref:`specular <shaders.common.pbr.specular>` value
    - Y is the :ref:`smoothness <shaders.common.pbr.smoothness>` value
    - Z is the :ref:`metallic <shaders.common.pbr.metallic>` value


.. _shaders.shadow_generations.emission.parameters.luminance:

Luminance
    A float parameter of which the first component alters the brightness of the
    :ref:`emission texture <shaders.shadow_generations.emission.textures.emission>`.


.. _shaders.shadow_generations.emission.parameters.diffuse:

diffuse
    A float parameter containing a color.

    Exclusive to the ``EmissionToneOpAnim_dpnE`` shader, which combines the **alpha component** with the
    :ref:`diffuse textures <shaders.shadow_generations.emission.textures.diffuse>` alpha channel via
    multiplication.