
.. _bpy.types.HEIO_SCAP_MassEdit:

***********************
SCA Parameter Mass-edit
***********************

SCA parameter often need to be edited across multiple objects or bones, which can be a hassle.
That's where these mass-edit tools come in handy: They allow you to select, add, update and remove
SCA parameters across a wider selection of objects or bones.

For more information on SCA Parameters, see :doc:`SCA Parameters </user_interface/object/sca_parameters>`.

Properties
==========

There are several properties to configure how to edit sca parameters:

.. _bpy.types.HEIO_SCAP_MassEdit.mode:

Mode
----

The type of sca parameters to edit.

- ``Model`` in object mode: target the SCA parameters on selected mesh objects.
- ``Model`` in pose or armeture edit mode: Target the SCA parameters on selected bones.
- ``Material``: Target sca parameters of materials on selected objects.


.. _bpy.types.HEIO_SCAP_MassEdit.use_preset:

Use Preset
----------

Whether to lock the name and type to a preset provided by the target game.


.. _bpy.types.HEIO_SCAP_MassEdit.value_name:
.. _bpy.types.HEIO_SCAP_MassEdit.value_name_enum:

Name
----

The name of the sca parameter to target. Can either be manually specified as a text, or be selected
from a range of presets by clicking the ``use preset`` toggle to the right of the name.


.. _bpy.types.HEIO_SCAP_MassEdit.value_type:

Value Type
----------

Type to use when adding/updating the parameter. Is pre-determined if ``use preset`` is enabled.


.. _bpy.types.HEIO_SCAP_MassEdit.value:
.. _bpy.types.HEIO_SCAP_MassEdit.float_value:
.. _bpy.types.HEIO_SCAP_MassEdit.boolean_value:

Value
-----

The value to target and/or update/add. Kind of value depends on the value type.


Operators
=========

.. _bpy.ops.heio.scap_massedit_select:

Select
------

Select all objects/bones that contain the targeted parameter name.


.. _bpy.ops.heio.scap_massedit_select.exact:

Select exact
------------

Select all objects/bones that contain the targeted parameter name and specified value (value type not checked).


.. _bpy.ops.heio.scap_massedit_set:

Set
---

Add or update the targeted SCA parameter on all selected objects/bones.


.. _bpy.ops.heio.scap_massedit_remove:

Remove
------

Remove the targeted SCA parameters with the same name on all selected objects/bones.