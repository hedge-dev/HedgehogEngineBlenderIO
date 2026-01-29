
***************
Installing HEIO
***************

.. attention::

	Right now, only x64-Windows and x64-Linux are supported!

Installing Blender
==================

| The Addon is only supported on `Blender <https://blender.org/>`_ version 4.5 and above.
| It is recommended to install blender through `Steam <https://store.steampowered.com/app/365670>`_. This will ensure you're always using the latest release version.


Installing the Addon
====================

.. attention::

	As of now, there is no release version, only a dev version!

	As such, the instructions below are for the dev version.


This addon utilizes the blender extension system. Yet, due to various reasons, we cannot host the
addon on the `official blender extension repository <https://extensions.blender.org/>`_.
That is why we have set up our own repository under ``https://Justin113D.com/blender/dev/``,
which will always host the newest release of this addon.

To set up the repository and download the addon, follow these steps:

	1. Open blender
	2. Open the preferences and open the ``Get Extensions`` tab
	3. Expand ``Repositories`` on the top right
	4. Click the ``+`` on the top right and select ``Add remote Repository``
	5. Enter ``https://justin113d.com/blender/dev/index.json`` for the URL and check ``Check for Updates on Startup``
	6. Confirm
	7. Rename the newly added list entry from ``Justin113D.com`` to ``Sonic I/O Dev``
	8. Select the list entry, expand the ``advanced`` section and change the module from ``justin113d_com`` to ``sonic_io_dev``
	9. Press the 🔄 button in the top right to refresh the module
	10. Search for ``Hedgehog`` in the search bar and install the ``Hedgehog Engine Blender I/O DEV BUILD`` addon

Congratulations! You have successfuly installed the addon!


Updating the addon
------------------

1. Repeat steps 1-3 from the installation
2. Click the ``v`` button in the top right
3. Press the 🔄 button
4. Search for the installed addon in your list
5. Click the ``update`` button


Addon dependencies
==================

HEIO requires other addons to unfold its full potential:

- `Blender DDS Addon <https://github.com/matyalatte/Blender-DDS-Addon>`_: Allows for exporting DDS textures out of blender, as well as providing a better import.