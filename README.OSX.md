# Welcome the the WooKey quickstart guide for OSX users

## Introduction

This help is deliberately brief, and mostly here for a quick setup of the SDK.
A thorough and complete documentation about the WooKey project, the EwoK microkernel,
the Tataouine SDK can be found on the [dedicated wiki]().

## Licensing

This software is published under a dual license form: LGPL2.1+ or BSD3 clause on the user's choice.

## About repo

The WooKey project deployment depends on repo. This is required as the project aims to
support various profiles, including various end-user applications, drivers and libraries
without requiring complex modification of the SDK.
In order to do that, we use a manifest file (standard Google repo tool mechanism) to
deploy a complete image of the SDK by cloning multiple git repositories depending on the
required profile.

To properly download the WooKey project, you will need to install both `repo` and `git`.

 - Official version:

	```
	$ git clone https://gerrit.googlesource.com/git-repo ~/tools/git-repo
    $ sudo /bin/echo "~/tools/git-repo/ > /etc/paths.d/git-repo"
	```

- Version without google syncro:

	```
	$ git clone https://github.com/l0kod/git-repo ~/tools/git-repo
	$ sudo /bin/echo "~/tools/git-repo/ > /etc/paths.d/git-repo"
	```


You can then execute the following commands:

```
$ repo init -u https://wookey.github.io/wookey-project/manifest.git -m default.xml
$ repo sync
```

This will deploy the SDK into a new local subdirectory named 'wookey'.



## Tools needed by the SDK itself

Now that the SDK is deployed, there are some tools that need to be installed in order to
build your first firmware.

### Local tools and utilities

* Perl:  The SDK depends on perl for its internal tools (including ldscripts generators).
There is no specific constraint on the version of perl you use.

* Python:
    - python-bincopy: This tool is used to generate .hex files from multiple elf files
        when generating the firmware.
        You can install it using pip:

		```
   		$ pip install python-bincopy
		```


* kconfig-frontends (http://http://ymorin.is-a-geek.org/projects/kconfig-frontends):
    This is a C-based implementation of the Kconfig parsers. It is used to parse the
    Kconfig format as defined in the Linux kernel sources.

	```
	$ brew tap px4/homebrew-px4
	$ brew install kconfig-frontends
	```

	or:

	```
	$ sudo port install kconfig-frontends
	```



* sphinx-doc:
    sphinx-doc is used to generate the complete documentation website.
	```
	$ brew install sphinx-doc
	```

	or:

	```
	$ sudo port install py36-sphinx
	$ sudo port select --set python python36
	$ sudo port select --set sphinx py36-sphinx
	```



* doxygen:
    doxygen is used to generate the technical manuals documentation.

	```
	$ brew install doxygen
	```

	or:

	```
	$ sudo port install doxygen
	```



* imagemagick:
    imagemagick is used to generate images for the documentation.

	```
	$ brew install imagemagick
	```

	or:

	```
	$ sudo port install
	```


* latex:
    As doxygen generates LaTeX sources that need to be compiled, you also have to install a LaTeX runtime.
    see [MacTeX](http://www.tug.org/mactex/).



### About the toolchain

The goal of the SDK is to build a firmware for a microcontroler. In this case this is an armv7-m-based
microcontroler. As a consequence, you need a cross-toolchain to do that, including:

* arm-none-eabi:
    Classic arm-gcc toolchain:

	```
	$ brew tap px4/homebrew-px4
	$ brew install gcc-arm-none-eabi
	```

    or:

	```
	$ sudo port install arm-none-eabi-gcc
	```



* Ada ARM ELF:
    If you want to compile the Ada/Spark kernel, you will need the Ada cross-toolchain. This toolchain
    can be downloaded [here](https://www.adacore.com/download)

      - [Current version](http://mirrors.cdn.adacore.com/art/5b071301c7a447e5727f2a86) :


        	SHA-1: 10303d2822001364257562dc3e56d52c5780c8d0

    You can download the toolchain for various host type and archtecture. Beware to download the ARM ELF gnat
    cross-toolchain (not the native one !).


### About the flashing tools

The last dependencies... are not due to the SDK itself but by the fact that you have to interact with
a microcontroler through a JTAG interface. There is two utilities that can be used for that:

* openocd:
    OpenOCD is used in order to debug and burn the firmware to the target
    OpenOCD can be used to be connected with a cross gdb (typically installed with
    *gdb-arm-none-eabi*) in order to debug and interact with the execution of the microcontroller
    through its DWT interface.

	```
$ brew install openocd
	```
or:

	```
$ sudo port install openocd

	```

* st-link:
    permit to manipulate the STMicro interface only to flash or send varous commands.

	```
	$ brew install stlink

	```
	or:

	```
	$ sudo port install stlink

	```

	This is all you need by now... :-)


## Configure the project

First you have to select a configuration. Preinstalled configurations can be listed using the *defconfig\_list* target

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


The only thing that you need to connect is the STLINK USB interface and the UART1.

   * Connect a USB/TTL adapter RX to the UART1 TX => PB6
   * Connect a USB/TTL adapter TX to the UART1 RX => PB7
   * Connect the STLINK USB interface to your USB Host.

## Burning a sample to the target board


Open a shell and launch openocd using the configuration file of your STM32F407-DISCOVERY board.

In the tools/ subdirectory you will find two configuration files:

   * stm32f4disco0.cfg for STM32F4xx-DISC0 boards
   * stm32f4disco1.cfg for STM32F4xx-DISC1 boards


```
   $ openocd -f tools/stm32f4disco<X>.cfg -c "program build/armv7-m/32f407discovery/wookey.elf verify reset exit"
```

## Debuging a sample application

Open a shell and launch openocd using the configuration file of your STM32F407-DISCOVERY board.

In the tools/ subdirectory you will find two configuration files:

   * stm32f4disco0.cfg for STM32F4xx-DISC1 boards
   * stm32f4disco1.cfg for STM32F4xx-DISC0 boards


* In Terminal 1: Launch openocd which is required to debug the target

```
   $ cd <wookey repository>
   $ openocd -f tools/stm32f4disco<X>.cfg"
```

* In Terminal 2: Launch your favorite debugger, for example arm-none-eabi-gdb:

```
   $ cd <wookey repository>
   $ arm-none-eabi-gdb build/armv7-m/32f407discovery/wookey.elf"
   gdb>target extended-remote 127.0.0.1:3333
   gdb>symbols build/armv7-m/32f407discovery/wookey.elf
   gdb>
```

