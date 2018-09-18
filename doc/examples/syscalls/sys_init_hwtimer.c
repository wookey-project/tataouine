uint32_t  num_tim = 0;

void tim_handler(uint8_t irq)
{
  num_tim++;
}

/*
 * Registering a hardware timer. Remember to executer sys_init(INIT_DONE) after
 * to activate the timer.
 * tim_handler() will be execute every 2 seconds, in thread mode and will have
 * access to all task's globals and functions.
 */
int register_htwtimer(void)
{
  e_syscall_ret ret = 0;
  timer_config_t timer = { 0 };

  timer.prescaler = 3; // divide frequency by 4
  timer.countmode = TIMER_CNTMODE_DOWN;
  timer.period = 84000000; // (168 MHz/4)/84000000 = 0.5 Hz
  timer.clk_div = 0;
  timer.max_repeat = 0;
  timer.handler = tim_handler;

  ret = sys_init(INIT_HWTIMER, &timer, 0);
  if (ret != SYS_INIT_DONE) {
    goto oops;
  }
  return 0;
oops:
  printf("oops...\n");
  return 1; /* leaving */
}
