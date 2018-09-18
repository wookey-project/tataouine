.. _dependencies:

Tools needed by the SDK itself
------------------------------

Now that when the SDK is deployed, some tools need to be installed in order to
build your first firmware.

.. note::
   **TL;DR**: summary of the tools needed by the Tataouine SDK, and detailed in the next paragraphs.
  
   **For the firmware compilation:**
       * *perl*
       * *python*, and specifically its *python-bincopy* package
       * A Kconfig parser (for example *kconfig-frontends*: http://ymorin.is-a-geek.org/projects/kconfig-frontends)
       * A GNU ARM none-eabi toolchain (usually *gcc-arm-none-eabi*)
       * The *AdaCore ARM cross-toolchain* for the Ada microkernel (https://www.adacore.com/download/more)

   **For the documentation compilation:**
       * *sphinx* for the main documentation
       * *doxygen* for the technical API amnuals, and *doxygen-latex* to compile
         the generated TeX documentation
   
   **For the firmware flashing on the target board:**
       * *OpenOCD* **or** *st-link* (https://github.com/texane/stlink.git) 
       

Local tools and utilities
^^^^^^^^^^^^^^^^^^^^^^^^^

The SDK depends on perl for its internal tools (including *ldscripts* generators). You need
to have perl installed on your host. There is no specific constraint on the version of perl you use.

.. hint::
   Most of the time, no action is requested here, as perl is usually installed by default in
   many distributions

You need python-bincopy (and as a consequence python) to be installed. This tool is used to
generate .hex files from multiple elf files when generating the firmware. On Debian, python-bincopy
is not packaged, but you can install it using pip (pip install bincopy).

.. hint::
   On any system having python and pip installed, just run pip install bincopy to download and deploy locally the bincopy module

You need a kconfig-conf and kconfig-nconf binaries. These binaries parse the Kconfig format
as defined in the Linux kernel sources. One of the existing projects supporting a standalone
implementation of such parsers is *kconfig-frontends* (http://ymorin.is-a-geek.org/projects/kconfig-frontends).
This is a C-based implementation of the Kconfig parsers. This software is currently being
integrated in the Debian distributions by our team but is still in the new queue by now (middle sept. 2017):
https://ftp-master.debian.org/new/kconfig-frontendsi\_4.11.0.1%2Bdfsg-1.html

We hope it will be integrated as fast as possible in the Debian main pool for unstable and testing
distributions, and in the Ubuntu current one in the same time.

.. hint::
   While the package is not yet deployed in Debian, or if you are using another distribution or OS, you can still compile it:
      * wget http://ymorin.is-a-geek.org/download/kconfig-frontends/kconfig-frontends-4.11.0.1.tar.xz
      * tar -xJvf  kconfig-frontends-4.11.0.1.tar.xz
      * cd kconfig-frontends-4.11.0.1
      * ./configure && make
      * sudo make install # if you wish

If you wish to generate the documentation, you will need *doxygen* (to generate the technical manuals), and
*sphinx* (to generate the complete documentation website). As doxygen generates LaTeX sources that
need to be compiled, you also have to install a LaTeX compiler. On Debian *doxygen-latex* will do
this for you.

.. hint::
   doxygen and sphinx are proposed in nearly all the OSes and distributions. You can use these packages as there is no specific usage that would make specific requirements on them

About the toolchain
^^^^^^^^^^^^^^^^^^^

The goal of the SDK is to build a firmware for a microcontroler. In this case this is an armv7m based
microcontroller. As a consequence, you need a cross-toolchain to do that, including:

*GNU make*, to support the Gmake syntax of the Makefiles. Please note that BSD Make will not be able to parse the SDK Makefiles.
The cross-compiler, named in Debian *gcc-arm-none-eabi*, which is a cross-compiler for native non-GNU targets.

Beware to use a none-eabi compiler, as the target is not a GNUeabi one. The Debian distribution proposes
such packages natively if needed.

.. hint::
   On Debian, just install gcc-arm-none-eabi

If you want to compile the Ada/Spark kernel, you will need the Ada cross-toolchain. This toolchain
can be downloaded here for GNU/Linux:

https://www.adacore.com/download/more

You can download the toolchain for various host type and architectures. Beware to download the ARM ELF gnat
cross-toolchain (not the native one!).

The AdaCore GNAT toolchain will help you installing the toolchain with a graphic installer. Although, remember to add the <install_path>/bin directory to your PATH variable in order to be able to use the toolchain binaries without their full paths. For this, export the proper path with and **export PATH="/gnat/install/path/bin:$PATH"**.

.. warning::
   Having the gnat toolchain binaries in your PATH is required as the Makefiles call them directly without using a full path.

About the flashing tools
^^^^^^^^^^^^^^^^^^^^^^^^

The following last dependencies are not inherent to the SDK itself: they are only necessary when interacting with
the target microcontrollers in order to **flash the firmware** produced by the SDK.

Flashing and interacting with a target usually use a JTAG/SWD interface, and dedicated tools are needed in order
to control them. Such interactions also include debugging features (through an exposed gdb server).

For STM32 based microcontrollers and the associated development boards, two open source utilities are useful:

   * OpenOCD, which is packaged in various distributions and allows to interact with the target
   * st-link (the open source version can be found on Github: https://github.com/texane/stlink.git)

OpenOCD and st-util (one of the st-link tools) can be used to connect a cross gdb (typically installed
with *gdb-arm-none-eabi*) in order to debug and interact with the execution of the microcontroller.
Breakpoints, watchpoints and many debugging features are then available to analyze the running
code.

.. hint::
   You can flash the firmware with whatever the tool you want, there is no constraints. OpenOCD and ST-link are opensource, the STMicro proprietary software also works (on Windows only), or you can use any software able to communicate with the STLinkv2 JTAG interface.
