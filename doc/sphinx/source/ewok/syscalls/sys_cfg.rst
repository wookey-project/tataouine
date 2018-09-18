sys_cfg
-------
EwoK ressource reconfiguration API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Synopsis
""""""""

The ressource (GPIOs, DMA, etc.) reconfiguration request is done by the
sys_cfg() syscall familly. The sys_cfg() familly support the following
prototypes::

   e_syscall_ret sys_cfg(CFG_GPIO_SET, uint8_t gpioref, uint8_t value);
   e_syscall_ret sys_cfg(CFG_GPIO_GET, uint8_t gpioref, uint8_t *val);
   e_syscall_ret sys_cfg(CFG_DMA_RECONF, dma_t*dma, dma_reconf_mask_t reconfmask);
   e_syscall_ret sys_cfg(CFG_DMA_RELOAD, uint32_t dma_id);


sys_cfg(CFG_GPIO_SET)
"""""""""""""""""""""

GPIOs are not directly mapped in the task's memory. As a consequence, setting the GPIO output value, for
GPIO in output mode, must be done using a syscall.
There is no need to use the entire GPIO structure (or parent device_t structure) to set a GPIO. As describred in
the ``sys_init(INIT_DEVACCESS)`` explanations, each GPIO has a kref identifier. This identifier is used here
to identify the GPIO when asking the kernel for an action on it.

Setting an output GPIO previously registered is done with the following API::

   e_syscall_ret sys_cfg(CFG_GPIO_SET, uint8_t gpioref, uint8_t value);

The value set is the one given in third argument.

.. important::
  The GPIO to set must have been previously declared in the initialization phase.

sys_cfg(CFG_GPIO_GET)
"""""""""""""""""""""

In the same way, getting a GPIO value for a GPIO configured in input mode is done using a syscall.

GPIOs are not directly mapped in the task's memory. As a consequence,i in the same way has for ``sys_cfg(CFG_GPIO_SET)``
getting a GPIO value for a GPIO in input mode must be done using a syscall.

In the same maner, there is no need to use the entire GPIO structure (or parent device_t structure) to set a GPIO. As describred in
the ``sys_init(INIT_DEVACCESS)`` explanations, each GPIO has a kref identifier. This identifier is used here
to identify the GPIO when asking the kernel for an action on it.

Getting an input value of a GPIO previously registered is done with the following API::

   e_syscall_ret sys_cfg(CFG_GPIO_GET, uint8_t gpioref, uint8_t *val);

The value read is set in the syscall third argument.

.. important::
  The GPIO value to get must have been previously declared in the initialization phase.

sys_cfg(CFG_DMA_RECONF)
"""""""""""""""""""""""

.. note::
   Syncrhonous syscall, executable in ISR mode

In a generic DMA channel usage, it is a standard behavior to reconfigure a part of the DMA channel
informations. This is for example the case for input or output buffers when using direct access mode
with chained data.

EwoK allows some reconfiguration of DMA channels, in a controlled way. Only some fields of the ``dma_t``
can be reconfigured. This is the case of:

   * ISR handlers address
   * Input buffer address (for memory to peripheral mode)
   * Output buffer address (for peripheral to memory mode)
   * Buffer size
   * DMA mode (direct, FIFO or circular)
   * DMA priority

In order to reconfigure only a subset of theses fields, a mask exists specifying
which field(s) need(s) to be reconfigured.

As these fields are a part of the ``dma_t`` structure (see Ewok kernel API technical refence documentation), the
syscall requires this entire structure. This is also require to determine which DMA channel is
targeted by this syscall, by using the DMA id set in this structure by the kernel at initialization time.

Reconfiguring a part of a DMA stream is done with the following API::

   e_syscall_ret sys_cfg(CFG_DMA_RECONF, dma_t*dma, dma_reconf_mask_t reconfmask);


.. hint::
   The easiest way to use this syscall is to keep the dma_t structure used during the initialization
   phase and to update it during the nominal phase

.. important::
   The DMA that need to be reconfigured must have been previously declared in the initialization phase.

sys_cfg(CFG_DMA_RELOAD)
"""""""""""""""""""""""

.. note::
   Syncrhonous syscall, executable in ISR mode

There is some time when we only want the DMA controller to restart a copy action, without modifying
any of its properties. In that later case, only a reload is needed. The kernel only need to identify
the DMA controller and stream, and doesn't need a whole DMA structure. The task can then
use only the ``id`` field of the ``dma_t`` structure.

Reloading a DMA stream is done with the following API::

   e_syscall_ret sys_cfg(CFG_DMA_RELOAD, uint32_t dma_id);

.. important::
  The DMA that need to be reload must have been previously declared in the initialization phase.

sys_cfg(CFG_DMA_DISABLE)
""""""""""""""""""""""""

.. note::
   Syncrhonous syscall, executable in ISR mode

It is possible to disable a DMA stream. In that case, the DMA is stopped and can be re-enabled only by calling
one of sys_cfg(CFG_DMA_RELOAD) or sys_cfg(CFG_DMA_RECONF) syscalls.

This is usefull for DMA streams in circular mode, as they never stop while the software doesn't ask them to.

Disabling a DMA stream is done with the following API::

   e_syscall_ret sys_cfg(CFG_DMA_DISABLE, uint32_t dma_id);

.. important::
  The DMA that need to be disabled must have been previously declared in the initialization phase.

sys_cfg(CFG_DEV_MAP)
""""""""""""""""""""

.. note::
   Syncrhonous syscall, executable only in main thread mode

It is possible to declare a device as voluntary mapped (field ``map_mode`` of the *device_t* structure.
This field can be set to the following values:

   * DEV_MAP_AUTO
   * DEV_MAP_VOLUNTARY

When using DEV_MAP_AUTO, the device is automatically mapped to the task address space when finishing the
initialization phase, and is keeped mapped until the end of the task lifecycle.

When using DEV_MAP_VOLUNTARY, the device is not mapped by the kernel and the task has to map the device
itself. In that case, the device is mapped using this very syscall.

Voluntary mapped devices permit to map, configure and unmap in sequence more than the maximum number of
concurrently mapped devices. It also permit to avoid mapping devices for which concurrent mapping is
dangerous (e.g. concatenated mapping).

Mapping a device is done using the device id, hosted in the ``id`` field of the *device_t* structure,
which is set by the kernel at registration time.

Mapping a device is done with the following API::

   e_syscall_ret sys_cfg(CFG_DEV_MAP, uint8_t dev_id);

.. important::
   Declaring a voluntary mapped device require a specific permission: PERM_RES_MEM_DMAP

.. note::
   mapping a device requires a call to the scheduler, in order to reconfigure the MPU, this action is costly

sys_cfg(CFG_DEV_UNMAP)
""""""""""""""""""""""

.. note::
   Syncrhonous syscall, executable only in main thread mode

When using DEV_MAP_VOLUNTARY, a previoulsy voluntary mapped device can be unmap by the task.
Unmapping a device free a MPU slot when the task requires more than the maximum number of concurrently
usable MPU slots by managing devices in sequence in the main thread.

.. important::
   while the device is configured, device's ISR still map the device, even if it is unmap from the main thread

.. important::
   unmapping a device does not mean disable it, the hardware device still works and emit IRQs that are handled
   by the task's registered ISR

.. note::
   unmapping a device requires a call to the scheduler, in order to reconfigure the MPU, this action is costly

Unmapping a device is done using the device id, hosted in the ``id`` field of the *device_t* structure,
which is set by the kernel at registration time.

Unmapping a device is done with the following API::

   e_syscall_ret sys_cfg(CFG_DEV_UMAP, uint8_t dev_id);

