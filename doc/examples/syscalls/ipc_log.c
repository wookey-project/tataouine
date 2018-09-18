my_buffer = "hello !";
/* ret should returns SYS_E_DONE here */
ret = sys_ipc(0, IPC_LOG, 7, my_buffer);

/* an abstration to IPC_LOG is the printf function */
printf("my name is john !\n");
