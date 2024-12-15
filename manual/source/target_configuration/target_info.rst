
***********
Target Info
***********

Stored in ``TargetInfo.json``, the target info defines meta data and data-encoding versions used
by exporters.


File Structure
==============

.. code-block:: json

	{
	  // Display name of the target
	  "Name": "Shadow Generations",

	  // A short description of the target game
	  "Description": "The Shadow expansion of Sonic X Shadow Generations",

	  // Year in which the target game released
	  "ReleaseYear": 2024,

	  // The hedgehog engine version used (either 1 or 2)
	  "HedgehogEngine": 2,

	  // Whether the game makes use of needle texture streaming packages,
	  // A feature available since Sonic Frontiers that allows for texture streaming
	  "UsesNTSP": true,

	  // The various data versions to encode files with
	  "DataVersions": {

	    // Version of the material data (1-3)
	    "Material": 3,

	    // Version of the material file sample chunk structure (1-2)
	    "MaterialSampleChunk": 2
	  },

	  // Default texture modes to use for each texture type when importing images for materials.
	  // Can be "sRGB" for color textures, "Linear" for non-color textures, and "Normal" for normal textures (enables y-channel flipping)
	  "DefaultTextureModes": {
	    "diffuse": "sRGB",
	    "specular": "Linear",
	    "normal": "Normal",
	    /*...*/
	  }
	}