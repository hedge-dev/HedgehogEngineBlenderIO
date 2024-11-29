
####################
Target Configuration
####################

.. warning::

	**This is developer documentation!**

	If you just intend on using the addon with an existing target game, you can ignore this section
	of the manual entirely.


HEIO determines how to import, export and configure several properties via "Target Definitions",
several json (and other) files that provide the addon all the information needed to support a
hedgehog engine game.

Every target definition has its own directory, and contains the following files:

- :doc:`TargetInfo.json <target_info>`
- :doc:`Shaders.json <shaders>`
- :doc:`MaterialTemplates.blend <material_templates>`
- :doc:`SCAParameters.json <sca_parameters>` (optional)

.. container:: global-index-toc

	.. toctree::
		:maxdepth: 1

		target_info
		shaders
		material_templates
		sca_parameters


Adding a new target configuration
=================================

Since HEIO is powered by SharpNeedle, it's possible the addon has all the necessary
code to support editing the files of a hedgehog engine game that is not supported by
default.

While HEIO will never add every hedgehog engine game, its possible to write an addon/extension
that adds a new target configuration to HEIO. The code to do so is very simple:

.. code-block:: python

	import bpy
	if "hedgehog_engine_io" in bpy.context.preferences.addons.keys():
	   from bpy_ext.sonic_io.hedgehog_engine_io import register_definition
	   register_definition("/path/to/target/definition/directory", "MY_NEW_TARGET")

Unfortunately, this is not very robust right now and may cause issues when addons are being loaded,
unloaded or updated.