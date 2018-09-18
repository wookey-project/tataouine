EwoK API FAQ
------------

.. contents::

General FAQ
^^^^^^^^^^^

.. highlight:: c

Why applications main function is named _main?
###############################################

EwoK applications entry points have the following prototype::

   int function(uint32_t task_id):

There is an unsigned int argument passed to the main function, giving it the
current task identifier.

When using the ``main`` symbol, the compiler requires one of the
following prototypes::

  int main(void);
  int main(int argc, char **argv);

As EwoK doesn't generate such a prototype, the ``main`` symbol cannot be
used, explaining why ``_main`` is used instead. The generated ldscript automatically
uses it as the application entry point and the application developer has
nothing to do other than to name its main function properly.

What is a typical generic task's main() function?
###########################################################

A basic main function should have the following content:

   * An initialization phase
   * A call to sys_init(INIT_DONE) to finish the initialization phase
   * A nominal phase

A basic, generic main function looks like the following::

   int _main(uint32_t task_id)
   {
     /* Local variables declaration */
     uint8_t syscall_ret;

     /* Initialization phase */
     printf("starting initialization phase\n");

     /* any sys_init call is made here */

     /* End of initialization sequence */
     sys_init(INIT_DONE);

     /* Nominal sequence */
     printf("starting nominal phase\n");

     /*
      * If any post-init configuration is needed, do it here
      * This is the case if memory-mapped devices need to be configured
      */

     /*
      * Start the main loop or main automaton
      */
     do_main_loop();

     return 0;
   }

Syscall API is complex: why?
############################

EwoK syscalls is a fully driver-oriented API. Efforts have been put in providing
various userspace abstractions to help application developers in using
generic devices through a higher level API.

These abstractions are separated in:

   * userspace drivers
       These drivers supply a higher level, easier API to applications
       and manage a given device by using the syscall API and configuring
       the corresponding registers for memory-mapped devices. Drivers API
       abstract most of the complexity of the hardware devices (such as USARTs,
       CRYP, USB, SDIO, etc.)

   * userspace libraries
       These libraries implement various hardware-independent features, but
       may depend on a given userspace driver. They supply a functional API
       for a given service (serial console, AES implementation, etc.), and
       in case of a dependency with a userspace driver, manage the driver
       initialization and configuration.

Syscalls FAQ
^^^^^^^^^^^^

What is the header to include to get the syscalls prototypes?
##############################################################

Syscalls are implemented as functions in userspace, in the libstd.
The header is ``syscalls.h``.

When I declare a device, I always get SYS_E_DENIED?
######################################################

Denying may be the consequence of various causes:
   1. You are not in the initialization phase
   2. You don't have the permission to register this type of device (see :ref:`EwoK permissions <ewok-perm>`)
   3. If you use EXTI for one or more GPIO, you must have the corresponding permission
   4. If you require a forced execution of the main thread for one more more ISR, you must have the corresponding permission
   5. You have left a field unconfigured with a value that means something not permitted in your case (for example EXTI access request for GPIO)

.. hint::
   It is a good idea to memset to 0 a device_t structure before configuring it and requesting a device to the kernel.


When I configure a device, I always get SYS_E_INVAL?
#####################################################

Returning invalid may be the consequence of various causes:
   1. Your ``device_t`` structure contains some invalid (unset) field(s). When using the Ada kernel, be sure to memset to 0 the structure before using it, the kernel is very strict with the user entries (for obvious security reasons)
   2. You try to map a device that is not in the supported device map (see :ref:`EwoK device map <technical-docs>` for information)
   3. You try to map a device with an invalid size (see :ref:`EwoK device map <technical-docs>` for information)
   4. You have set more IRQ or more GPIOs than the maximum supported in the ``device_t`` structure (see :ref:`EwoK kernel API <technical-docs>` for information)

.. hint::
   It is a good idea to memset to 0 a device_t structure before configuring it and requesting a device to the kernel, and highly recommended when using the Ada kernel

Permissions FAQ
^^^^^^^^^^^^^^^

When using a library or a driver, are specific permissions required?
####################################################################

There is no permission needed to link to a given userspace library or driver, but they may require one ore more permission to work properly.

For example, the libconsole (managing a userspace serial console) requires
the Devices/Buses permission in order to use the libusart and configure the
specified U(S)ART correctly.

Each driver and library should have its required permissions specified in its
documentation page.

Libstd API
^^^^^^^^^^

Are there helper functions to manipulate registers in userspace?
################################################################

Yes! A lot of helper functions and macros have been written to help
interacting with registers.
This API is in the libstd regutils.h header. Applications can include
this header directly in order to use it.

Ewok Security
^^^^^^^^^^^^^

Why flash is mapped RX and not Execute only for both user and kernel?
######################################################################

This is a constraint due .rodata (read only data sections).

Since .rodata must be readable, executable code and such data have to
live together in the same flash area. Using different MPU regions to split
them would have required too much MPU regions (and the number of regions
is very constrained by the hardware unit).

Another solution would be to copy .rodata content into RAM, but this
suffers from the same MPU limitations issues, with the additional drawback
of reducing the available task volatile memory.

Is the W⊕X principle supported?
################################

The EwoK kernel enforces the W⊕X mapping restriction principle, which is
a strong defense in depth mitigation against userland exploitable vulnerabilities.

Moreover, the Ada kernel integrates SPARK proofs that verify at that there is no 
region that can be mapped W and X at the same time.

EwoK build process
^^^^^^^^^^^^^^^^^^

When I switch between C-based and Ada-based kernels, the compilation is not performed?
######################################################################################

When changing the compilation mode of the kernel, the *$(OBJS)* objects files
list of the kernel is modified to point to the Ada (or C) object files. As a
consequence, the clean target does not do its work properly as its variables
has changed.
To be sure to rebuild the kernel in the other language, you can either:
   * delete the kernel/ dir from the build directory
   * execute a make distclean before calling the defconfig
   * remove the build directory manually

