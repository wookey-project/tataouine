/**
 * @file main.c
 *
 * \brief Main of dummy
 *
 */

#include "autoconf.h"
#include "debug.h"
#include "m4_systick.h"
#include "init.h"
#include "stm32f4xx_usart.h"
#include "stm32f4xx_usart_regs.h"
#include "soc-layout.h"
#include "stack_check.h"
#include "mpu_config.h"
#include "product.h"
#ifdef CONFIG_FPU_ENABLE
# include "m4_fpu.h"
#endif
#include "leds.h"


/*
 * By default GDB doesn’t know how to view the call stack that lead to a HardFault, but we can help it. Stick this anywhere:
 * On hard fault, copy HARDFAULT_PSP to the sp reg so gdb can give a trace
 * https://stm32.agg.io/
 */
void **HARDFAULT_PSP;
register void *stack_pointer asm("sp");
void HardFault_Handler(void) {
	asm("mrs %0, psp" : "=r"(HARDFAULT_PSP) : :);
	stack_pointer = HARDFAULT_PSP;
	while(1);
}

/*
 * We use the local -fno-stack-protector flag for main because
 * the stack protection has not been initialized yet.
 */
__attribute__((optimize("-fno-stack-protector"))) int main(int argc, char * args[])
{
	char * base_address = 0;
    usart_config_t console_config = {0};

	disable_irq();

	/* Initialize the stack protection */
	init_stack_chk_guard();

	leds_init();
    debug_console_init(&console_config);

	if (argc == 1){
		base_address = (char * )args[0];
		system_init((uint32_t)base_address-VTORS_SIZE);
	}
	else{
		while (1);
	}
#ifdef CONFIG_FPU_ENABLE
    fpu_enable();
#endif

	enable_irq();

	dbg_log("\tHello ! I'm dummy !\n");
	dbg_flush();

	while (1) {
		leds_on(PROD_LED_STATUS); //FIXME
		sleep_intern(MEDIUM_TIME);
		leds_off(PROD_LED_STATUS); //FIXME
		sleep_intern(LONG_TIME);
        dbg_flush();
	}
	return 0;
}
