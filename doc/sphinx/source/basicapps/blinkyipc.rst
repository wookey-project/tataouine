.. _blinkyipcapp:

The 'blinky with IPC basic' apps
================================

The aim of this sample is to provide the same functionality as the one
provided by the 'blinky' standalone application described in :ref:`blinkyapp`.

The idea is to make the four LEDs of the STM32 Discovery blink by pair (green and red, blue
and orange) with a switch of the colors pair when the button is pressed. The main difference
with the 'blinky' standalone app is that **two applications** are used here instead of one:
one 'button' app handling the button push events, and one 'leds' app handling the LEDs toggling.
The two applications communicate using **IPC**, 'button' being the sender and 'leds' the
receiver.

These applications are configured with the C version of EwoK with::

  $ make boards/32f407disco/configs/disco_blinky_ipc_defconfig

These applications are configured with the Ada/Spark version of EwoK with::

  $ make boards/32f407disco/configs/disco_blinky_ipc_ada_defconfig


.. toctree::
   The Blinky IPC 'button' app <blinkyipcbutton>
   The Blinky IPC 'leds' app <blinkyipcleds>

