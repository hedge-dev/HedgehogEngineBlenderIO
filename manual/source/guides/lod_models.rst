
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


----


How are LoD models made?
========================

Unfortunately, this is where it gets a little complicated, as there is no simple 1-2 step way to
creating LoD models (yet).

Sonic Team reportedly used `InstaLOD <https://instalod.com/>`_ for generating most, if not all LoD
models, which they must have integrated into their own pipeline via plugins.

In default blender, the simplest way to creating LoD models is by using the
`Decimate modifier <https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/decimate.html>`_,
which organically reduces the number of polygons in a model.

The recommended way to create simple LoD models right now is:

1. Create a duplicate of the model using the `duplicate linked` operator
2. Change the name of the duplicate object to end with the level prefix ("_lv1", "_lv2", etc.)
3. Add a decimate modifier to the duplicate and configure it to your liking
4. Create and configure a new LoD info item on the original object
5. Set the duplicate object as the target of the new LoD info item

.. important::

	Keep in mind that LoD info is only sourced from the root of an object tree!

	If your object tree has an armature and/or children, then make sure that the entire object
	tree is link-duplicated and that only the root object has the LoD infos!


----


Examples
========

Terrain
-------

Here is a terrain model from Kingdom Valley from Shadow Generations:

.. figure:: /images/guides_lod_models_example_terrain.png

	The different LoD models from the terrain model ``w03_rockcliff_up01_noshadow_ins.terrain-model``


As observable, the LoD models simply reduce the number of polygons used with each level.

Also notice how the LoD cascade does not go up to 31, which means that the terrain will not be
rendered at all beyond cascade level 20 (to be confirmed).

These LoD models were most definitely automatically generated.


Model
-----

Here is a platform model from Kingdom Valley from Shadow Generations:

.. figure:: /images/guides_lod_models_example_model.png

	The different LoD models from the model ``w03_obj_floor01A.model``


Similar to the terrain model above, the first LoD model simply reduces the number of polygons used.

However, the second (and last) LoD model does something interesting: It is a simple box with
special textures unique to the level.

While the previous models used 9 different materials, each with different textures, this model
uses just one material with its own low resolution textures, which could mean that it was hand
made, or at least handled differently from terrain LoD models.

This probably stems from the fact that the platforms are used very generously throughout the stages
and challenges in Shadow generations, and needed special care to not impact the games performance.