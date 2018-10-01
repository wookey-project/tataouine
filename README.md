# Welcome to the WooKey quickstart guide

## Introduction

This help is deliberately brief, and mostly here for a quick setup of the SDK.
A thorough and complete documentation about the WooKey project, the EwoK microkernel, 
the Tataouine SDK can be found on the [dedicated WooKey documentation](https://wookey-project.github.io/).

## Licensing

This software is published under a dual license form: LGPL2.1+ or BSD3 clause on the user's choice.

The **only exception** is the EwoK microkernel that has its own licence: Apache2.

## About repo

The WooKey project deployment depends on repo. This is required as the project aims to
support various profiles, including various end-user applications, drivers and libraries
without requiring complex modification of the SDK.
In order to do that, we use a manifest file (standard Google repo tool mechanism) to
deploy a complete image of the SDK by cloning multiple git repositories depending on the
required profile.

To properly download the WooKey project, you will need to install both `repo` and `git`. In a
Debian environment:

```
  $ apt-get install git repo
```

You can then execute the following commands:

```
  $ repo init -u https://github.com/wookey-project/manifest.git -m default.xml
  $ repo sync
```

This will deploy the SDK into a new local subdirectory named 'wookey'.


## Tools needed by the SDK itself

Now that the SDK is deployed, there are some tools that need to be installed in order to
build your first firmware.

### Local tools and utilities

The SDK depends on `perl` for its internal tools (including ldscripts generators). You need
to have `perl` installed on your host. There is no specific constraint on the version of `perl` you use.
Some distributions (such as Debian) include and use `perl` natively (no need to install it through
a package manager)

You will also need `python-bincopy` (and as a consequence `python`) to be installed. This tool is used to
generate .hex files from multiple elf files when generating the firmware. On Debian, `python-bincopy`
is not packaged, but you can install it using `pip`:

```
  $ pip install bincopy
```

You will need a Kconfig parser tool. This tool parses the Kconfig format
as defined in the Linux kernel sources. One of the existing projects supporting a standalone
implementation of such parsers is the python3 lib kconfiglib project that can be installed using `pip`:

```
  $ pip install kconfiglib
```

Other Kconfig parsers can be used at your own choice, by overloading the KCONF variables (see the Wookeypedia
documentation for more information).

If you wish to generate the documentation, you need `doxygen` (to generate the technical manuals), and
`sphinx` (to generate the complete documentation website). As `doxygen` generates LaTeX sources that
need to be compiled, you will also have to install a LaTeX runtime. On Debian `doxygen-latex` will do
this for you:

```
  $ apt-get install sphinx doxygen doxygen-latex
```

### About the toolchain

The goal of the SDK is to build a firmware for a microcontroller. In this case this is a Cortex-M4 armv7m-based
one. As a consequence, you need a cross-toolchain to do that, including:

`GNU make`, to support the Gmake syntax of the Makefile. BSD Make will not be able to parse the SDK Makefiles.
The cross-compiler, named in Debian `gcc-arm-none-eabi`, which is a cross-compiler for native non-GNU target.

Beware to use a none-eabi compiler, as the target is not a GNUeabi one. The Debian distribution proposes
such packages natively if needed:

```
  $ apt-get install make gcc-arm-none-eabi
```

If you want to compile the Ada/Spark kernel, you will need the Ada cross-toolchain. This toolchain
can be downloaded here for GNU/Linux:

https://www.adacore.com/download/more

You can download the toolchain for various host types and architectures. Beware to download the **ARM ELF gnat**
cross-toolchain (and **not the native one**).


### About the flashing tools

The last dependencies are not related to the SDK itself, but by the fact that you have to interact with
a microcontroller through a JTAG interface in order to flash the built firmware.

There are two open source utilities that can be used for that:

   * `OpenOCD`, which is packaged in various distributions and which allows to interact with the target. In a Debian
environment:
```
  $ apt-get install openocd
```
   * `st-link` (the open source version can be found on [github](https://github.com/texane/stlink)), which allows to manipulate the
     STMicroelectronics STLink interface to flash or send varous commands.

`OpenOCD` and `st-link` can be used to be connected with a cross gdb (typically installed with *gdb-arm-none-eabi*) in order
to debug and interact with the execution of the microcontroller through its SWD interface.


## Configure the project

First, you have to set your environment. This is done by sourcing the `setenv.sh` script. This script exports
all paths that are required by the SDK to work correctly.

```
   $ source setenv.sh
   =========================================================
   === Tataouine environment configuration
   =========================================================

     ADA_RUNTIME   = /opt/adacore-arm-eabi
     ST_FLASH      = /usr/local/bin/st-flash
     ST_UTIL       = /usr/local/bin/st-flash
     CROSS_COMPILE = arm-none-eabi-
   
   =========================================================
```

Most of the time, the paths proposed in this script are not the one you use in your specific installation. The `setenv.sh` script support easy variables overloading by including a `setenv.local.sh` script file if this file exists in the same directory. If you need to overload
some of the variables of the `setenv.sh` script, just add them to your own `setenv.local.sh` file.

```
  $ echo "export ADA_RUNTIME = /users/foo/opt/gnat2018" > setenv.local.sh
  $ source setenv.sh
   =========================================================
   === Tataouine environment configuration
   =========================================================

     ADA_RUNTIME   = /users/foo/opt/gnat2018
     ST_FLASH      = /usr/local/bin/st-flash
     ST_UTIL       = /usr/local/bin/st-flash
     CROSS_COMPILE = arm-none-eabi-
   
   =========================================================
```

Then you have to select a configuration. Preinstalled configurations can be listed using the *defconfig\_list* target

```
   $ make defconfig_list
```

You can select one of them and apply it directly by giving its path as an argument to make:

```
   $ make boards/32f407disco/configs/disco_blinky_defconfig
```

This will generate a local .config file will all needed configuration entries set for the blinky sample application.
Now you can compile the firmware:

```
   $ make
```

## Generate the documentation

If you wish to build **all** the documentation, you can execute the *doc* target:

```
   $ make doc
```

This will build the following content:

   * the sphinx website (including all the documentation, helpers, principles and security explanations)
   * the man pages of the kernel and libstd API
   * the Doxygen-generated datasheets, less readable than sphinx but including all the API and structures.

You can also build only the sphinx website if you prefer not to install doxygen and the (heavy) LaTeX backend with
the following command:

```
   $ make -C doc sphinx
```

This is the end of this README, as the complete documentation is accessible using the sphinx website. You will find all
the needed information on how to modify the SDK configuration, add a new application, understand the SDK internals and
the EwoK micro-kernel API and behavior.

## Connecting the board to your host

The only thing that you need to connect is the STLINK USB interface and the UART1 (this is the default
kernel output console):

   * Connect a USB/TTL adapter RX to the UART1 TX => PB6
   * Connect a USB/TTL adapter TX to the UART1 RX => PB7
   * Connect the STLINK USB interface to your USB Host.

## Burning a sample to the target board

Open a shell and launch openocd using the configuration file of your STM32F407-DISCOVERY board.

In the tools/ subdirectory you will find two configuration files (for the different revisions of
the Discovery 407 board):

   * stm32f4disco0.cfg for STM32F4xx-DISC0 boards
   * stm32f4disco1.cfg for STM32F4xx-DISC1 boards


```
   $ openocd -f tools/stm32f4disco<X>.cfg -c "program build/armv7-m/32f407discovery/wookey.hex verify reset exit"
```

## Debugging a sample application

Open a shell and launch openocd using the configuration file of your STM32F407-DISCOVERY board.

In the tools/ subdirectory you will find two configuration files:

   * stm32f4disco0.cfg for STM32F4xx-DISC0 boards
   * stm32f4disco1.cfg for STM32F4xx-DISC1 boards


In Terminal 1: launch openocd which is required to debug the target

```
   $ cd <wookey repository>
   $ openocd -f tools/stm32f4disco<X>.cfg"
```

In Terminal 2: launch your favorite ELF debugger, for example arm-none-eabi-gdb:

```
   $ cd <wookey repository>
   $ arm-none-eabi-gdb build/armv7-m/32f407discovery/wookey.elf"
   gdb> target extended-remote 127.0.0.1:3333
   gdb> symbols build/armv7-m/32f407discovery/wookey.elf
   gdb>
```

