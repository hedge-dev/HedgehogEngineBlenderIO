
.. |X| replace:: :octicon:`x`

.. _sca_parameters:

==============
SCA Parameters
==============

.. note::

    not every parameter is available in every game


.. _sca_parameters.material:

Material parameters
-------------------

The following parameters were **found** in material files, where an |X| denotes that
it was found in that games files:

.. list-table::
    :widths: auto
    :width: 70 em
    :header-rows: 1

    * - Name
      - Type
      - Description
      - Lost World
      - Forces
      - Origins
      - Frontiers
      - Shadow Gens

    * - ``MaxAniso``
      - Integer
      - Maximum anisotropy filtering level
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|

    * - ``TrnsType``
      - Boolean
      - Transparency type (?)
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|

    * - ``TrnsPrio``
      - Integer
      - Transparency rendering priority. Used to adjusted drawing order.
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|

    * - ``MipBias``
      - Float
      - Mipmap selection bias
      - |X|
      - |X|
      - |X|
      - |X|
      - |X|

    * - ``UsePrior``
      - Boolean
      - Use Priority (?)
      - |X|
      - |X|
      -
      - |X|
      - |X|

    * - ``UseGrass``
      - Integer
      - Render grass on material (?)
      - |X|
      - |X|
      -
      -
      -

    * - ``VertSnap``
      - Boolean
      - Vertex snapping (?)
      -
      -
      -
      - |X|
      - |X|

    * - ``VatVolum``
      - Boolean
      - Whether the material is affected by VAT volumes
      -
      -
      -
      -
      - |X|


There are also SCA parameters that we know exist, but we don't know the purpose of, as they are
never actually used in any material:

- RenderCa (found in Shadow Generations)
- ExtnAABB (found in Shadow Generations)

They are possibly used in another hedgehog engine game that was not looked into yet.


.. _sca_parameters.mesh:

Mesh parameters
---------------

The following parameters were **found** in model files, where an |X| denotes that
it was found in that games files:

.. list-table::
    :widths: auto
    :width: 70 em
    :header-rows: 1

    * - Name
      - Type
      - Description
      - Lost World
      - Forces
      - Origins
      - Frontiers
      - Shadow Gens

    * - ``ShadowCa``
      - Boolean
      - Mesh can cast shadow when enabled
      -
      - |X|
      - |X|
      - |X|
      - |X|

    * - ``ShadowRe``
      - Boolean
      - Mesh can receive shadow when enabled
      -
      - |X|
      - |X|
      - |X|
      - |X|

    * - ``DisableC``
      - Boolean
      - If enabled, mesh does not render (but can still cast shadows)
      -
      - |X|
      -
      - |X|
      - |X|

    * - ``RenderPa``
      - Integer
      - Render pass to use(?); Values from 1 to 6 were found
      -
      -
      - |X|
      - |X|
      - |X|

    * - ``RenderCa``
      - Integer
      - Unknown; Values of 1, 2 and 5 were found
      -
      - |X|
      -
      - |X|
      -

    * - ``GIOcclus``
      - Boolean
      - Enable for global illumination occlusion (?)
      -
      -
      - |X|
      - |X|
      - |X|

    * - ``Occluder``
      - Boolean
      - Unknown
      -
      - |X|
      -
      -
      -

    * - ``GPUOcclu``
      - Boolean
      - Unknown
      -
      -
      -
      - |X|
      - |X|

    * - ``CPUOcclu``
      - Boolean
      - Unknown
      -
      -
      -
      - |X|
      - |X|

    * - ``CullType``
      - Integer
      - Culling type(?); Values from 1 to 3 found
      - |X|
      -
      -
      -
      -

    * - ``Peepable``
      - Boolean
      - Characters are visible behind the mesh
      - |X|
      -
      -
      -
      - |X|

    * - ``TerrainB``
      - Boolean
      - Unknown
      -
      -
      - |X|
      - |X|
      - |X|

    * - ``ColorMas``
      - Boolean
      - Color mask(?)
      -
      -
      - |X|
      - |X|
      - |X|

    * - ``CyberMas``
      - Boolean
      - Cyber mask(?)
      -
      -
      -
      - |X|
      - |X|

    * - ``UsageCPU``
      - Boolean
      - Unknown
      -
      - |X|
      -
      -
      -

    * - ``TrRLRPre``
      - Boolean
      - Unknown
      -
      -
      -
      - |X|
      - |X|
