
==================
Game documentation
==================

This is where you can find information on how each game utilizes assets, shaders, sca parameters
and more.

Textures
--------

Describes various types of textures utilized by each engine.

Split up into :doc:`Hedgehog Engine 1<textures/textures_he1>`
and :doc:`Hedgehog Engine 2<textures/textures_he2>`.


Shaders
-------

Lists of shaders for each game that are specified for each material and determine how the material
gets rendered ingame.

There are several shader principles that are shared between games:

- :doc:`Physically based rendering (PBR)<shaders/common/pbr>`
- :doc:`Normal mapping<shaders/common/normal_mapping>`
- :doc:`Weather<shaders/common/weather>`
- :doc:`Vertex colors <shaders/common/vertex_colors>`
- :doc:`Mesh layers <shaders/common/mesh_layers>`
- :doc:`Deferred rendering <shaders/common/deferred_rendering>`

Shaders are documented for all games that are natively supported by HEIO:

- :doc:`Sonic Unleashed<shaders/unleashed/index>`
- :doc:`Sonic Generations<shaders/generations/index>`
- :doc:`Sonic Lost World<shaders/lost_world/index>`
- :doc:`Sonic Forces<shaders/forces/index>`
- :doc:`Sonic Origins<shaders/origins/index>`
- :doc:`Sonic Frontiers<shaders/frontiers/index>`
- :doc:`Shadow Generations<shaders/shadow_generations/index>`

Additionally, earlier titles may make use of :doc:`shader features<shader_features>`.


:doc:`SCA Parameters<sca_parameters>`
-------------------------------------

Additional parameter data attached to selected data structures, like materials, meshes and bones of skeletons.


.. container:: global-index-toc

    .. toctree::
        :maxdepth: 2

        textures/index
        shaders/index
        shader_features
        sca_parameters