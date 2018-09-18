#include "syscall.h"

void my_cryptin_handler(uint8_t irq, uint32_t status)
{
  /*
   * this handler is executed in user mode, but in ISRTHREAD mode, with a
   * dedicated stack
   * Yet it has access to the task's data if needed (globals, functions...)
   * irq is the IRQ number, starting with VTOR[0], this permits to use the same
   * handler for multiple IRQs if needed.
   * status is the DMA Stream status register value
   */
}

void my_cryptout_handler(uint8_t irq, uint32_t status)
{
  /*
   * this handler is executed in user mode, but in ISRTHREAD mode, with a
   * dedicated stack
   * Yet it has access to the task's data if needed (globals, functions...)
   * irq is the IRQ number, starting with VTOR[0], this permits to use the same
   * handler for multiple IRQs if needed.
   * status is the DMA Stream status register value
   */
}

#define DMA2_CHANNEL_CRYP    2
#define DMA2_STREAM_CRYP_OUT 5
#define DMA2_STREAM_CRYP_IN  6

uint8_t data_in[512];
uint8_t data_out[512];
uint16_t data_len = 512;

/*
** Example configuration for CRYP device, using two DMA streams,
** one for memory to device, one for device to memory (automatically
** transfered by the device when finished, see CRYP device driver
** implementation).
*/
int register_device(void)
{
  e_syscall_ret ret = 0;

  dma_t dma_in = {
    .channel = DMA2_CHANNEL_CRYP,
    .dir = MEM_TO_PERIPH,
    .in_addr = (physaddr_t)data_in,
    .out_addr = (volatile physaddr_t)r_CORTEX_M_CRYP_DIN,
    .dma = DMA2,
    .size = data_len,
    .stream = DMA2_STREAM_CRYP_IN,
    .mode = DMA_DIRECT_MODE,
    .in_handler = my_cryptin_handler,
    .out_handler = my_cryptout_handler /* not used */
  };

  printf("init DMA CRYP in...\n");
  ret = sys_init(INIT_DMA, &dma_in, 0);
  if (ret != SYS_INIT_DONE) {
    goto oops;
  }

  dma_t dma_out = {
    .channel = DMA2_CHANNEL_CRYP,
    .dir = PERIPH_TO_MEM,
    .in_addr = (volatile physaddr_t)r_CORTEX_M_CRYP_DOUT,
    .out_addr = (physaddr_t)data_out,
    .dma = DMA2,
    .size = data_len,
    .stream = DMA2_STREAM_CRYP_OUT,
    .mode = DMA_DIRECT_MODE,
    .in_handler = my_cryptin_handler, /* not used */
    .out_handler = my_cryptout_handler
  };

  printf("init DMA CRYP out...\n");
  ret = sys_init(INIT_DMA, &dma_out, 0);
  if (ret != SYS_INIT_DONE) {
    goto oops;
  }

  /* now, the kernel activate the DMA steams: */
  ret = sys_init(INIT_DONE, 0, 0);
  if (ret != SYS_INIT_DONE) {
    goto oops;
  }
  /* okay; init step is now finished.*/
  while (1) {
    sys_yield();
  }
oops:
  printf("oops...\n");
  return 1; /* leaving */
}

