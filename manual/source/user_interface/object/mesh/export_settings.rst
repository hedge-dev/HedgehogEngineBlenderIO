
***************
Export Settings
***************

.. reference::

	:Panel:		:menuselection:`Properties --> Mesh Properties --> HEIO Mesh Properties --> Export Settings`

Various export settings for meshes.

Force enable 8-weight export
	Forces the mesh to export with a weight limit of 8 per vertex, instead of the usual 4.

	Usually enabled per mesh-set by adding and enabling the ``enable_max_bone_influence_8``
	boolean parameter to a material.

	This feature is only available in HE2 games.

Force enable multi tangent export
	Forces the mesh to export with a second set of tangents based on the third UV map.

	Usually enabled per mesh-set by adding and enabling the ``enable_multi_tangent_space``
	boolean parameter to a material.

	This feature is only available for specific shaders in HE2 games.