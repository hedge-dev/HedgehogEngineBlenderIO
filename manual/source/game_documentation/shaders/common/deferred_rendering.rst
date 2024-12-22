
==================
Deferred rendering
==================

Deferred rendering is a rendering technique used in Hedgehog Engine 2 games.

The "standard" way of rendering is called "forward rendering", and simply draws one mesh after
another, including all the lighting calculations. But since one mesh can hide a significant portion
of another, many of those lighting calculations go to waste and could be better spent elsewhere.

This is where deferred rendering comes in: Instead of calculating the lighting for every mesh
individually, a meshes rendering properties can be stored in multiple frame buffers, which can
then be composited together and achieve a similar result!


An example
----------

Here are some example frame buffers for a scene that uses deferred rendering:

.. list-table::
    :widths: 50 50
    :header-rows: 0
    :align: center

    * - .. figure:: /images/gamedoc_shaders_deferred_rendering_albedo.png

            The :ref:`albedo <shaders.common.pbr.albedo>` buffer

      - .. figure:: /images/gamedoc_shaders_deferred_rendering_pbr.png

            The :ref:`specular <shaders.common.pbr.specular>`, inverted :ref:`smoothness <shaders.common.pbr.smoothness>` and :ref:`ambient occlusion <shaders.common.pbr.ambient_occlusion>` buffer

    * - .. figure:: /images/gamedoc_shaders_deferred_rendering_normal.png

            The normals buffer

      - .. figure:: /images/gamedoc_shaders_deferred_rendering_emission.png

            The :ref:`Emission <shaders.common.pbr.emission>` buffer


These, as well as some niche other buffers, can now be combined with lighting and result in this:

.. figure:: /images/gamedoc_shaders_deferred_rendering_combined.png

    A composited scene of Kingdom Valley from Shadow Generations


Drawbacks
---------

While faster than forward rendering, this technique is not perfect and has several drawbacks:

- Requires more GPU memory to store the frame buffers
- Does not allow for transparency blending
- No multi-sample-anti-aliasing (MSAA)

Since transparency is a very important feature, only ppaque and punch-through meshes use deferred
rendering, while transparent meshes get drawn after the compositing of the frame buffers.