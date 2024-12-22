
.. _sca_parameters:

==============
SCA Parameters
==============

.. note::

    not every parameter is available in every game


.. _sca_parameters.material:

Material parameters
-------------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Name
      - Type
      - Description

    * - MaxAniso
      - Integer
      - Maximum anisotropy filtering level

    * - TrnsType
      - Boolean
      - Transparency type (?)

    * - TrnsPrio
      - Integer
      - Transparency rendering priority. Used to adjusted drawing order.

    * - MipBias
      - Float
      - Mipmap selection bias

    * - UsePrior
      - Boolean
      - Use Prior (?)

    * - UseGrass
      - Integer
      - Render grass on material (?)

    * - VertSnap
      - Boolean
      - Vertex snapping (?)

    * - VatVolum
      - Boolean
      - Whether the material is affected by VAT volumes


There are also SCA parameters that we know exist, but we don't know the purpose of, as they are
never actually used in any material:

- RenderCa (found in Shadow Generations)
- ExtnAABB (found in Shadow Generations)

They are possibly used in another hedgehog engine game that was not looked into yet.


.. _sca_parameters.mesh:

Mesh parameters
---------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Name
      - Type
      - Description

    * - ShadowCa
      - Boolean
      - Mesh can cast shadow when enabled

    * - ShadowRe
      - Boolean
      - Mesh can receive shadow when enabled

    * - DisableC
      - Boolean
      - If enabled, mesh does not render (but can still cast shadows)

    * - GIOcclus
      - Boolean
      - Enable for global illumination occlusion (?)

    * - TerrainB
      - Unknown
      - Unknown, found on terrain models

    * - ColorMas
      - Unknown
      - Unknown
