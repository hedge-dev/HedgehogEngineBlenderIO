
##########
LoD Models
##########

LoD models (an abbreviation for \ **L**\ evel-\ **o**\ f-\ **D**\ etail) are used to reduce the
processing power needed to render a model far away from the camera by reducing its polygon count
and other related methods.

They were first used in Sonic Frontiers, but may have been supported since Sonic Forces.


Where are LoD models found?
===========================

LoD models are stored in ``.model`` and ``.terrain-model`` files, alongside additional LoD-specific
information on when to use each model. **Note that not all model files have LoD models.**

It should be noted that files with LoD models are formatted
differently, and will not work in HE1 games, as well as potentially break some tools that are not
equipped with recognizing and reading those formats.


Importing LoD models
--------------------

You can import LoD models by checking the ``import LoD models`` option in the model importers:

.. figure:: /images/guides_lod_models_import.png

	How to import LoD models

Doing this will create a new collection, to which all imported LoD models are added:

.. figure:: /images/guides_lod_models_import_collection.png

	The LoD import collection


Configuring LoD models
======================

LoD models can be configured for the followering object types:

- Armatures
- Meshes
- Curves (mesh)
- Surfaces (mesh)
- Text objects (mesh)

Each of these data types has an HEIO properties panel; For armatures, it is called ``HEIO Armature
Properties``, while for the mesh types it's called ``HEIO Mesh properties``. In these panels
you will find a sub-panel with the name "LoD Info":

.. figure:: /images/guides_lod_models_panel.png

	The lod info panels for meshes (left) and armatures (right)


Here you configure the individual LoD models, which are used when the object is **the
root** of the exported :ref:`object tree <guides/object_trees:Rooted trees>`.


Setup
-----

When first opening the LoD info subpanel you are met with a button that says "Initialize LoD Info"
(unless it's an imported object that already had LoD info):

.. figure:: /images/guides_lod_models_initialize.png

	The initial LoD info panel


Pressing the button will create the default entry and make it possible to add more entries:

.. figure:: /images/guides_lod_models_initialized.png

	The initialized LoD info panel


Lod info items
--------------

Each LoD info item in the LoD list has 3 properties:

Target
	The root of the object tree to export for the LoD model. If this is missing, then the info
	item is ignored.

LoD Cascade
	The cascade until which the model should be displayed. **(Needs confirmation)**

	The greater the number, the further away the model gets displayed.

Unknown
	We have no idea what this does yet, as the game never uses a value beside -1.


The "self" item
---------------

This item does not have a target, as it represents the object on which the list is stored.