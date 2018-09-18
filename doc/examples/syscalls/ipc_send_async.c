e_syscall_ret ret = 0;
char buffer_out[16] = "[hello moto!  ]\0";

do {
printf("trying to send %s...\n", buffer_out);
ret = sys_ipc(IPC_SEND_ASYNC, 2, 15, buffer_out);
} while (ret == SYS_E_BUSY);

if (ret == SYS_E_DONE) {
  printf("okay, buffer sent. Yet don't know if it has been read or not.\n");
}


