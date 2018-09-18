/*
 * To be executed before sys_init(INIT_DONE)
 */
int init_mypeerid(void)
{
  e_syscall_ret ret = 0;
  char const *peer = "usbdrv";
  uint32_t id = 0;

  ret = sys_init(INIT_GETTASKID, peer, &id);
  if (ret == SYS_RET_INVAL) {
    goto oops;
  }
  return id;
oops:
  printf("peer %s not found!\n", peer);
  return 1;
fail:
  printf("oops...\n");
  return 1; /* leaving */
}

