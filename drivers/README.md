== Userspace drivers library pool

This directory hosts the userspace drivers library pool. All applications
can use these drivers as libraries.
The usage of drivers may require specific permissions. For example, the
CRYP driver (libcryp) requires devaccess, cryp-user or cryp-cfg (depending on the usage)
to work properly. The DMA driver (libdma) requires devaccess and ext-io permissions
to work properly.

All drivers use the kernel API defined in the kernel\_api document to configure
the corresponding device and propose a higher, functionnal API to the application.

Some drivers may depends on others. For example, using the CRYP driver in DMA mode
require the DMA driver.

Adding a driver is done by:
- creating a "libxxx" directory where xxx is the name of the physical IP or feature
  (e.g. usbdfu) supported by the driver
- updating the Makefile.objs and the Kconfig of this directory accordingly
- In the driver directory, just add the sources and a Makefile similar to the ones
  used in other drivers, replacing the driver name in the first line of the Makefile
- all exported headers of the driver should be hosted in a subdirectory of the driver
  dir named 'api'. This directory will be automatically added to the inclusion search
  path of the applications

That's all folks :)

If an application needs to use one or multiple drivers, list them in its Makefile
(see crypto application for example)
