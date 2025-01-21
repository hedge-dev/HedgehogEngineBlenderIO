
*******************
Material Properties
*******************

.. reference::

	:Panel:		:menuselection:`Properties --> Material Properties --> HEIO Material`


.. _HEIO_Material.custom_shader:

Custom Shader
	If checked, all material properties can be fully customized, without being tied to a
	pre-defined shader from the :ref:`target game <HEIO_Scene.target_game>`


.. _HEIO_Scene.show_all_shaders:

Show All Shaders
	Most target games have over 100 shaders, many of which are for very niche use cases and will
	only rarely need to be used. For each game, a hand picked list of shaders is displayed by
	default, which should suffice for most users.

	Enable this property to show all shaders, instead of just the handpicked subset.

	.. note::

		The shader subsets were automatically picked based on how often they were used in their
		respective games, without experience on which actually get used by most modders.

		If you have a better list of shaders to display by default, create an issue with the list
		(optimally explaining what each shader is used for) and we will see about adjusting the
		addon


.. _HEIO_Material.shader_name:
.. _HEIO_Material.shader_definition:

Shader
	Every material specified the shader it uses by its name, which determine how the parameters
	and textures get used to render it ingame.

	When the material uses a custom shader, then shader is an editable text.
	Otherwise, it's a dropdown with shaders specified for the targeted game.

	.. note::
		Changing the shader via the dropdown will add needed and remove unneeded parameters and
		textures.


.. _HEIO_Material.variant_name:
.. _HEIO_Material.variant_definition:

Variant
	Some shaders, primarily from Hedgehog Engine 1 games, had several variations per shader to use
	which enabled different features, such as enabling bone deformation.

	When the material uses a custom shader, then the shader properties will be an editable text.
	Otherwise, depending on whether the selected shader has any variants, you it's a dropdown.


.. _bpy.ops.heio.material_setup_nodes_active:

Setup/Update Nodes
	When pressed, the addon will look up the shader (+ variant) in the target games material
	templates and set it up accordingly for the material.


General
=======


.. _HEIO_Material.render_layer:

Render Layer
	The render layer to use when exporting a model. This is a property that is not actually tied to
	materials, but to mesh-sets of a model, but since blender has nothing like mesh-sets,
	the layer gets derived from materials on export.

	HEIO adds the ability to specify the layer to use per polygon using
	:doc:`Render layers </user_interface/object/mesh/render_layers>`, but usually
	the materials render layer is all you need.

	If set to automatic the layer will be taken from the selected shader. If the shader
	is not defined by the targeted game, ``Opaque`` will be used.

	When choosing ``Special``, a textfield will be shown that lets you specify the special layer
	name.

Clip Threshold
	The default clip threshold property added here for convenience.

Backface Culling
	`The default backface culling property <https://docs.blender.org/manual/en/latest/render/eevee/material_settings.html#bpy-types-material-use-backface-culling>`_
	added here for convenience.


.. _HEIO_Material.use_additive_blending:

Use additive blending
	Will render the material using additive blending, instead of normal blending.


Lists
=====

.. container:: global-index-toc

	.. toctree::
		:maxdepth: 1

		material_parameters
		material_textures

- :doc:`Parameters </user_interface/object/material_parameters>`
- :doc:`Textures </user_interface/object/material_textures>`
- :doc:`SCA Parameters </user_interface/object/sca_parameters>`