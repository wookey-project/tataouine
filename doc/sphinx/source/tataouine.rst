The Tataouine SDK
================

About the dependencies
----------------------

Downloading Tataouine
--------------------

Tataouine allows to deploy the complete WooKey SDK using repo to collect and
deploy the overall WooKey git repositories.
This allows to support various applications, libraries and drivers profiles
for versatile hardware platforms using the manifest file to select the corresponding list
of software elements.

.. hint::
   Please install repo on your build host first before continuing

.. toctree::
   Downloading Tataouine with repo <tataouine/repo>
   About the dependencies <tataouine/deps>

Using Tataouine
--------------

Now that the SDK has been downloaded, we detail how to use it.
More precisely, we describe how to build the sample application given with
the Tataouine SDK, to understand the basic build targets.

Then, we explain how you can create your own, custom, EwoK
userspace application and how you can build and flash it.

.. toctree::
   Building a blinky project <tataouine/build>
   Flashing a new firmware <tataouine/flash>
   Creating a new application <tataouine/newapp>

About Tataouine hierarchy
------------------------

Now that the basics have been covered, we can dive deeper in the Tataouine architecture
to understand how it works and how software modules are integrated, configured, built and flashed.

The Tataouine SDK hosts all needed sources and configuration
to build an embedded system based on EwoK microkernel.

Tataouine contains the following main directories:

+------------+------------------------------------------+
| Directory  | Purpose                                  |
+============+==========================================+
| kernel     | the EwoK microkernel                     |
+------------+------------------------------------------+
| drivers    | Userspace drivers of various hardware IP |
+------------+------------------------------------------+
| libs       | Userspace libraries                      |
+------------+------------------------------------------+
| loader     | Platform bootloader                      |
+------------+------------------------------------------+


.. toctree::
   Debugging the project <tataouine/debug>
   About the configuration <tataouine/config>
