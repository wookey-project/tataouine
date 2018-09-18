sys_ipc  
-------
EwoK Inter-Proccess Communication API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Synopsis
""""""""

In EwoK there is no **process** structure as there is no MMU on
microcontrolers, but there is a task notion and an IPC principle.

Inter-Process Communication is done using the sys_ipc() syscall familly.
The sys_ipc() familly support the following prototypes::

   e_syscall_ret sys_ipc(IPC_LOG, logsize_t size, const char *msg);
   e_syscall_ret sys_ipc(IPC_SEND_SYNC, uint8_t target, logsize_t size, const char *msg);
   e_syscall_ret sys_ipc(IPC_RECV_SYNC, uint8_t *sender, logsize_t *size, char *msg);
   e_syscall_ret sys_ipc(IPC_SEND_ASYNC, uint8_t target, logsize_t size, const char *msg);
   e_syscall_ret sys_ipc(IPC_RECV_ASYNC, uint8_t *sender, logsize_t *size, char *msg);

Communicating with another task requests to know its identifier. Each task has
a unique numeric identifier generated at build time by Tataouine.

Getting a task identifier is done by using sys_init(INIT_GETTASKID), as explained above.



sys_ipc(IPC_LOG)
""""""""""""""""

This special IPC is used to log into the kernel console. This is used in association wih the kernel
serial port for informational and debug purpose. In production, the kernel USART may not be connected
and the interface not accessible to the user.

The ipc log syscall has the following API::

   e_syscall_ret sys_ipc(IPC_LOG, logsize_t size, const char *msg);

sys_ipc(SEND_SYNC)
""""""""""""""""""

The ipc syncrhonous send syscall has the following API::

   e_syscall_ret sys_ipc(IPC_SEND_SYNC, uint8_t target, logsize_t size, const char *msg);



sys_ipc(SEND_ASYNC)
"""""""""""""""""""

The ipc syncrhonous receive syscall has the following API::

   e_syscall_ret sys_ipc(IPC_RECV_SYNC, uint8_t *sender, logsize_t *size, char *msg);

sys_ipc(RECV_SYNC)
""""""""""""""""""

The ipc asyncrhonous send syscall has the following API::

   e_syscall_ret sys_ipc(IPC_SEND_ASYNC, uint8_t target, logsize_t size, const char *msg);

sys_ipc(RECV_ASYNC)
"""""""""""""""""""

The ipc asyncrhonous receive syscall has the following API::

   e_syscall_ret sys_ipc(IPC_RECV_ASYNC, uint8_t *sender, logsize_t *size, char *msg);


