:og:description: Configuring shader definitions for HEIO target games
:og:image: _images/index_target_configuration.png

*******
Shaders
*******

Stored in ``Shaders.json``, it defines all shaders and their properties to use in the material
editor.


File Structure
==============

At the top, the file is a dictionary, where the shaders are defined by keys and contain shader
definition objects:

.. code-block:: json

	{
	  // The "base" shader definition, which all shaders inherit from (optional)
	  "": {
	    /*...*/ // the shader definition
	  },

	  "some_shader":
	  {
	    /*...*/
	  },

	  /*...*/
	}


Shader Definition
=================

This is how a shader definition is set up. Note that none of these properties are required,
and all of them can be left out entirely.

.. code-block:: json

	{
	  // Whether to hide this shader, and only show it when "show all shaders" is enabled
	  "Hide": false,

	  // The automatic mesh layer to use when using this shader. Possible values are:
	  // - "Opaque"
	  // - "Transparent"
	  // - "PunchThrough"
	  // - "Special"
	  "Layer": "Opaque",

	  // Shader variants, a list of strings.
	  "Variants": [
	    "",
	    "b",
	    /*...*/
	  ]

	  // A dictionary of parameters and their types and default values
	  "Parameters": {

	    "diffuse": {
	      // The type of parameter. Possible values are:
	      // - "Float"
	      // - "Color"
	      // - "Boolean"
	      "Type": "Color",

	      // The default value to use when creating this parameter.
	      // For "Float" and "Color", it must be an array with 4 numbers.
	      // For "Boolean", it must be a boolean
	      "Default": [1,1,1,0]
	    },

	    /*...*/
	  },

	  // A list of texture type names
	  "Textures": [
	    "diffuse",
	    /*...*/
	  ]
	}