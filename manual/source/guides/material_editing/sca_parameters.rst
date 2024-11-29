
==============
SCA Parameters
==============

A list of SCA parameters for materials.

.. note::

	not all parameters are available in every game

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


----


There are also SCA parameters that we know exist, but we don't know the purpose of, as they are
never actually used in any material:

- RenderCa (found in Shadow Generations)
- ExtnAABB (found in Shadow Generations)

They are possibly used in another hedgehog engine game that was not looked into yet.