:og:description: HEIO Addon Preferences
:og:image: _images/index_user_interface.png

.. _bpy.types.HEIO_AddonPreferences:

*****************
Addon Preferences
*****************

.. reference::

	:Panel:		:menuselection:`Edit --> Preferences --> Add-ons --> Hedgehog Engine I/O`

.. _bpy.types.HEIO_AddonPreferences.multi_threading_mode:

Multi-threading mode
	How to utilize multi threading for when importing/exporting

	- ``Enabled - Automatic``: Use multi threading and automatically determine how many threads to use
	- ``Enabled - Limited``: Use multi threading, but limit to/target a specific number of threads
	- ``Disabled``: Do not use multi threading


.. _bpy.types.HEIO_AddonPreferences.multi_threading_limit:

Multi-threading limit
    Used when the Multi-threading mode is set to ``Enabled - Limited``. Allows you to limit/specify the
    number of threads to use.

    .. warning::
        this can be used to exceed the number of simultaneous threads used by the addon, not just limit
        them. Be aware that using a high number of threads may cause problems!


.. _bpy.types.HEIO_AddonPreferences.ntsp_dir_frontiers:
.. _bpy.types.HEIO_AddonPreferences.ntsp_dir_shadow_generations:

NTSP directory
    Path to each games ``Needle texture streaming package`` folder. Used for when importing
    streamed textures.