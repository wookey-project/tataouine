.. _flash:

Flashing a new firmware
-----------------------

As explained in the dependencies section, there is no constraint on how to flash the firmware. Multiple solutions exist,
some use open source tools and others can use proprietary tools. In the sequel, we will focus on using the
*openocd* open source tool.

After the wookey.hex file is built (using the make all target), use the following steps to flash it on the target board.

.. note::
   For now, this help targets the STM32 F407 Discovery board (https://www.st.com/en/evaluation-tools/stm32f4discovery.html).

   Future evolutions of the Tataouine SDK will include more boards: the current section will be updated
   accordingly.

Connecting OpenOCD to the board
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First you have to setup openocd to communicate with the board connected to one of your USB ports.
If your board is connected, you should see something like this when running lsusb::

    Bus 001 Device 005: ID 0483:374b STMicroelectronics ST-LINK/V2.1

You can see the vendor and product id here (0483 and 374b). In tataouine, you have openocd configuration files for Discovery boards.
For the STM32 Discovery F407, just run::

   $ openocd -f tools/stm32f4disco1.cfg

You may need to be root (try with sudo) depending on your groups and user permissions.

.. hint::
   If stm32f4disco1.cfg fails, try stm32f4disco0.cfg, if it doesn't, check the file for the vendor and product id and compare them to the one you have seen using lsusb.
   Actually, these two openocd configurations are due to various revisions of the F407 board (explaining diverging openocd setups).

Now that openocd is connected, you can interact with it through a local server.

This can be done:
   * with a cross-gdb which will connect to it
   * directly using telnet and typing openocd commands

If you use telnet, you can just connect to openocd on localhost, port 4444::

   $ telnet localhost 4444

Now you have a command line on openocd server, in which you can execute commands to manipulate the board debug interface.

Reseting and flashing the device
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first command is usually a reset command::

   reset halt

This asks the board to reset and to halt at startup, freezing the core on its first instruction so that flashing
it is safe.

Now you can flash the board with the image you have built::

   flash write_image erase build/armv7-m/32f407discovery/wookey.hex

Now that the firmware is flashed, you can reset and start the board::

   reset run

Other ways
^^^^^^^^^^

You can also use the ST-link tool to flash the firmware, simply by using the st-flash tool of the st-link project.

.. hint::
   You can also use gdb to flash the image, by calling monitor command through the gdb shell connected to openocd. Using gdb allows to create breakpoints and to debug the embedded software easily

.. hint::
   If you use a cross-gdb to connect to openocd (in order to flash but also to debug the board) you must use the port 3333 instead of the port 4444, which is dedicated to telnet connection
