int register_device(void)
{
  e_syscall_ret ret = 0;
  char const *devname = "mydev";
  device_t dev;

  strncpy(dev.name, devname, sizeof(devname));
  dev.address = 0x40028000;
  dev.size = 0x1400;
  dev.irq_num = 1;
  dev.irqs[0].handler = (void*)my_irq_handler;
  dev.irqs[0].irq = ETH_IRQ;
  dev.gpio_num = 2;
  dev.gpios[0].kref = 1;
  dev.gpios[1].kref = 0;
  dev.gpios[1].port = 1;
  dev.gpios[1].pin = 5;
  dev.busref = AHB1;
  ret = sys_init(INIT_DEVACCESS, &dev, 0);
  if (ret != SYS_INIT_DONE) {
    goto oops;
  }
  /* okay; init step is now finished.*/
  while (1) {
    /* main task execution loop... */
  }
oops:
  printf("oops...\n");
  return 1; /* leaving */
}

void my_irq_handler(uint8_t irq)
{
  /*
   * this handler is executed in user mode, but in ISRTHREAD mode, with a
   * dedicated stack
   * Yet it has access to the task's data if needed (globals, functions...)
   * irq is the IRQ number, starting with VTOR[0], this permits to use the same
   * handler for multiple IRQs if needed.
   */
}
