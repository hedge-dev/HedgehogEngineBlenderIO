
=======
Weather
=======

Hedgehog Engine 2 has a dynamic environment system internally referred to as "weather" that is
responsible for doing things like generating a skybox at runtime or changing how materials look.

.. _shaders.common.weather.pbr_effect:

Effect on PBR materials
-----------------------

While the details are not exactly known right now, it's possible to deduce several functions from
reading the shaders (which, as of writing this, has only been done for Shadow Generations).

For the majority of all shaders, the following PBR properties get interpolated based on currently
unknown values:

- The :ref:`albedo color <shaders.common.pbr.albedo>` to itself squared
- The :ref:`specular value <shaders.common.pbr.specular>` to ``0.02``
- The :ref:`smoothness value <shaders.common.pbr.smoothness>` to ``0.9``
- The :ref:`ambient occlusion <shaders.common.pbr.smoothness>` to ``1``
