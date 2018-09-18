e_syscall_ret ret = 0;
char buffer_in[16];
uint8_t size;

printf("trying to receive...\n";
do {
  /* check if there is an IPC to read */
  ret = sys_ipc(IPC_RECV_ASYNC, 2, &size, buffer_in);
  /* doing something else in the meantime here... if there is nothing in the input IPC buffer */
} while (ret == SYS_E_INVAL);
/* buffer_in is now fullfill */
