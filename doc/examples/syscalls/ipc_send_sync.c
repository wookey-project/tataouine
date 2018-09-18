e_syscall_ret ret = 0;
char buffer_out[16] = "[hello moto!  ]\0";

printf("trying to send %s...\n", buffer_out);
do {
ret = sys_ipc(IPC_SEND_SYNC, 2, 15, buffer_out);
// If busy (unable to distribute the buffer), the IPC return BUSY, otherwise, it locks the task.
} while (ret == SYS_E_BUSY);
/* We are now frozen until the target task (2) has read the IPC */
