
**************
SCA Parameters
**************

Stored in ``SCAParameters.json``, an optional file that defines SCA Parameter presets for specific
storage containers.

Earlier Hedgehog Engine games do not support SCA parameters at all, and may not need an this file
at all.

File Structure
==============

All top-level dictionary properties are optional.

.. code-block:: json

	{
	  // SCA Parameter Types for material
	  "Material": {

	    // Name of the SCA parameter; They can at most be 8 characters long
	    "ParaName": {

	      // Type of the parameter. Used when creating from a preset or when importing.
	      // Possible values are
	      // - "Integer"
	      // - "Float"
	      // - "Boolean"
	      "Type": "Integer",

	      // A description of what the parameter does
	      "Description": "Does something!"
	    },
	    /*...*/
	  }
	}