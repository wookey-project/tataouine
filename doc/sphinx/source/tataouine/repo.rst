Tataouine and repo
-----------------

The goal of Tataouine is to propose a full modular Software Development Kit. As a consequence, the
following are *not* a part of Tataouine

   - The applications
   - The userspace drivers
   - The userspace libraries and stacks
   - The kernel sources
   - The bootloader sources
   - Any potential external libraries and tools

As a consequence, there is various repositories, one for each component:
   - one repository per application
   - one repository per driver
   - one repository per library
   - one repository for EwoK (the kernel)
   - one repository for the bootlader

In order to deploy a given project SDK, we use repo. This permit to download
the various repositories and deploy them properly in the good place automatically.

.. image:: img/repo_archi.png
   :width: 650 px
   :alt: Wookey repositories architecture
   :align: center

repo uses manifest files, that are hosted in a single, independent, git repository. In our case,
this repository is named `manifest.git` in the wookey repository list.

This manifest permits to deploy the entire Wookey project.

.. hint:: 
   This structure permit to replace any items with your own in another manifest. You can create your own project manifest file
   with your own applications list, reducing or increasing the number of drivers or libraries as needed


Initialize the SDK
------------------

Initialize the SDK is made using the standard repo command::

   repo init -u https://github.com/wookey-project/manifest.git -m default.xml
   repo sync

The manifest name can be replaced by any of the existing manifest of the manifest.git repository, depending on your needs.

Theses commands creates a `wookey` directory in the current directory, containing all the extracted repositories in order
to build the project.

If you whish to modify one of the repositories of the SDK, use the following command::

   cd path/to/the/repository
   repo start mybranch

This will create a named branch in the repository.

.. hint::
   The repo tool command reference can be `read here <https://source.android.com/setup/develop/repo>`_
