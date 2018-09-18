e_syscall_ret ret = 0;
char buffer_in[16];
uint8_t size;

printf("trying to receive...\n";
ret = sys_ipc(IPC_RECV_SYNC, 2, &size, buffer_in);
/* We are now frozen until there is something to read in the task input IPC buffer */
