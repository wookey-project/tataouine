Quick start
============

Welcome to the WooKey project quick start guide. The philosophy, main purpose and features of the project are
summarized in the :ref:`targetofproject` section.

The project needs some dependencies, please check the :ref:`dependencies` section to fetch them.

In order to download the current project and build the EwoK microkernel as well as the example applications
using the Tataouine SDK, please refer to the :ref:`buildprocedure` section for a step by step walk through.

For now, only two example use cases are provided with WooKey:

  * **The 'blinky' use case** (see :ref:`blinkyapp`): a standalone application toggles the board LEDs and waits
    for user button pressing events to switch its toggling pattern
  * **The 'blinky with IPC' use case** (see :ref:`blinkyipcapp`): two applications communicating with IPC and
    realizing the same functional behavior as the 'blinky' use case

Once the firmware is built, you can flash a target board using the procedure described in :ref:`flash`.
Currently, only the **STM32 Discovert F407** is supported, but more boards (including our custom WooKey
board) will come in the next months as explained in the :ref:`roadmap` section.

If you have all the :ref:`dependencies` installed, you can directly clone the repository::

   repo init -u https://github.com/wookey-project/manifest.git
   repo sync 

