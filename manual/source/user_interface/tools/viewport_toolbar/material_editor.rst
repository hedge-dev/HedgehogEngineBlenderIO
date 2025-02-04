
******************
Material Mass-edit
******************

These are tools used to help you modify multiple materials at once.


.. _bpy.ops.heio.material_setup_nodes:

Setup/Update Nodes
------------------

Set up the nodes of multiple materials based on their shader.

More information about setting up nodes can be found :ref:`in the guides <guides_material_editing_node_setup>`


.. _bpy.ops.heio.materials_to_principled:

Materials to Principled BSDF
----------------------------

Replaces node trees of materials with BSDF node trees. If the HEIO material had a diffuse or normal
texture, then it will be integrated into the tree.

This is most helpful when intending to export models to other file formats, such as GLTF.


.. _bpy.ops.heio.materials_from_principled:

Material Textures from Principled BSDF
--------------------------------------

Collects diffuse and normal textures from BSDF node trees and inserts them into the HEIO material.
This will not alter the node tree.

.. important::
	For non-custom materials, this will only fill existing texture slots, not create any!

	E.g. if your material is a non-custom shader that does not have any diffuse texture slots,
	then any found diffuse texture on that material will be ignored!


.. _bpy.ops.heio.material_mass_edit_update:
.. _bpy.types.HEIO_Material_MassEdit:

Mass-Edit properties
--------------------

There are 4 sub-menus for precisely modifying specific properties of multiple materials at once:

- Shader
- General
- Parameter
- Texture

Each of these allows you to define properties and then insert them on every targeted material.


.. _bpy.types.HEIO_Material_MassEdit.update_render_layer:
.. _bpy.types.HEIO_Material_MassEdit.update_alpha_threshold:
.. _bpy.types.HEIO_Material_MassEdit.update_backface_culling:
.. _bpy.types.HEIO_Material_MassEdit.update_blend_mode:

General
^^^^^^^

General properties are special in that they have an additional checkbox to determine which
properties you want to update, e.g. checking only the checkbox to the left of the render
layer and using ``Update`` will only update the render layer on the targeted materials.


.. _bpy.ops.heio.material_mass_edit_remove:
.. _bpy.types.HEIO_Material_MassEdit.parameter_name:
.. _bpy.types.HEIO_Material_MassEdit.texture_name:

Parameter & Texture
^^^^^^^^^^^^^^^^^^^

These also act rather uniquely.

When using ``Add/Update`` then the targeted materials will be checked for the selected
parameter/texture name. If found, then that one is simply updated. If not, and the material uses a
custom shader, then the setup will be added.

The ``Remove`` operator only affects custom shaders too.


.. _bpy.types.HEIO_Material_MassEdit.texture_index:

Texture Index
^^^^^^^^^^^^^

The texture index is also rather special: Textures can have the same slot multiple times,
so this is used to specify which slot to affect.

If a slot is added with the index of 1, but no slot of index 0 exists, then an empty slot
with the same name is added too.

If a slot is removed with the index of 0, but a slot with the index 1 exists, then no slot will
be removed so that slot 1 retains its functionality.