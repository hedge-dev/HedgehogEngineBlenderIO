
***************
Installing HEIO
***************

Installing HEIO is not as straightforward as most other addons. It requires **.NET 8** to be
installed, as the addon relies on **C# Libraries** to boost performance and reduce on the amount
of code needed to manage. You will have to ensure that you have the **.NET 8 Runtime** installed
before being able to use the addon to its fullest.


Installing .NET 8
=================

If you are unsure of whether your machine already has .NET 8 installed, you can check by opening
the console and running ``dotnet --list-runtimes``.

The output should look similar to this:

.. figure:: /images/installing_dotnet8.png

Notice the line marked in green, ``Microsoft.NETCore.App 8.X.X``. if you find this (or a newer
version) among your installed runtimes, you have all you need!

------------

If you don't have the needed runtime installed, head over to
`the download page <https://dotnet.microsoft.com/en-us/download>`_ and install the runtime.

.. note::

	The website recommends downloading the **SDK** (**S**\ oftware **D**\ evelopment **K**\ it). Unless you are a
	developer, **you may only want the runtime**. You can head over to
	"`All .NET 8.0 downloads <https://dotnet.microsoft.com/en-us/download/dotnet/8.0>`_" and
	download the Desktop runtime from further down, saving space on your machines storage.


Installing Blender
==================

| The Addon is only supported on `Blender <https://blender.org/>`_ version 4.3 and above.
| It is recommended to install blender through `Steam <https://store.steampowered.com/app/365670>`_. This will ensure you're always using the latest release version.


Installing the Addon
====================

.. warning::

	As of now, there is no release version, only a dev version!


This addon utilizes the blender extension system. Yet, due to various reasons, we cannot host the
addon on the `official blender extension repository <https://extensions.blender.org/>`_.
That is why we have set up our own repository under ``https://Justin113D.com/blender/release/``,
which will always host the newest release of this addon.

To set up the repository and download the addon, follow these steps:

	1. Open blender
	2. Open the preferences and open the ``Get Extensions`` tab
	3. Expand ``Repositories`` on the top right
	4. Click the ``+`` on the top right and select ``Add remote Repository``
	5. Enter ``https://justin113d.com/blender/release/index.json`` for the URL and check ``Check for Updates on Startup``
	6. Confirm
	7. Rename the newly added list entry from ``Justin113D.com`` to ``Sonic I/O``
	8. Select the list entry, expand the ``advanced`` section and change the module from ``justin113d_com`` to ``sonic_io``
	9. Press the 🔄 button in the top right to refresh the module
	10. Search for ``Hedgehog`` in the search bar and install the ``Hedgehog Engine Blender I/O`` addon

Congratulations! You have successfuly installed the addon!


.. note::
	If you are interested in testing the WIP dev version, you have to repeat these steps for the developer repository:

	- In step **5.** enter ``https://justin113d.com/blender/dev/index.json`` for the URL
	- In step **8.** change the module to ``sonic_io_dev``

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