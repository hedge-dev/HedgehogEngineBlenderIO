
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

Mode
----

The type of sca parameters to edit.

- ``Model`` in object mode: target the SCA parameters on selected mesh objects.
- ``Model`` in pose or armeture edit mode: Target the SCA parameters on selected bones.
- ``Material``: Target sca parameters of materials on selected objects.


Name
----

The name of the sca parameter to target. Can either be manually specified as a text, or be selected
from a range of presets by clicking the ``use preset`` toggle to the right of the name.


Value Type
----------

Type to use when adding/updating the parameter. Is pre-determined if ``use preset`` is enabled.


Value
-----

The value to target and/or update/add. Kind of value depends on the value type.


Operators
=========

Select
------

Select all objects/bones that contain the targeted parameter name.


Select exact
------------

Select all objects/bones that contain the targeted parameter name and specified value (value type not checked).


Set
---

Add or update the targeted SCA parameter on all selected objects/bones.


Remove
------

Remove the targeted SCA parameters with the same name on all selected objects/bones.