.. _blinkyipcleds:

The blinky with IPC 'leds' app
==============================

This application is coupled with the :ref:`blinkyipcbutton` as they work together using IPC channels
(InterProcess Communication).

These applications are configured with the C version of EwoK with::

  $ make boards/32f407disco/configs/disco_blinky_ipc_defconfig

These applications are configured with the Ada/Spark version of EwoK with::

  $ make boards/32f407disco/configs/disco_blinky_ipc_ada_defconfig

Purpose of the example
----------------------

This is a very basic sample application on top of the EwoK microkernel for the STM32 Discovery F407.

The purpose of this sample is to show how two applications can interact with the GPIOs and also interact
together through IPC to synchronize each other.

The current application (leds) handles the four colored LEDs GPIOs of the board in output mode (PD12 to PD15).
When a button push event is caught, an IPC is sent to the leds application notifying it of such an event.
Hence, the button application is an IPC sender and the leds application is an IPC receiver.

From a user level experience, here is how the two applications should act: two of the four user LEDs
of the board are blinking (green and red, or blue and orange). When the user pushes the user Button
('blue' button on the board), the other two LEDs start blinking and the former ones stop.

In addition to the device init, GPIOs and IPC related syscalls, a time related syscall is used in this
sample (`sys_sleep`).

Sketch of the example
----------------------

Getting the button application id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The main task of the leds application begins to get the task id of the button application
using the `sys_init` syscall with `INIT_GETTASKID`:

.. code-block:: c

    /* Get the button task id to be able to communicate with it using IPCs */
    ret = sys_init(INIT_GETTASKID, "button", &id_button);

GPIOs configuration for the LEDs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The main function of the task initializes the four LEDs (four GPIOs in input mode) inside
the `device_t` structure associated to the LEDs:

.. code-block:: c

    /* Zeroing the structure to avoid improper values detected
     * by the kernel */
    memset (&leds, 0, sizeof (leds));

    strncpy (leds.name, "LEDs", sizeof (leds.name));

    leds.gpio_num = 4; /* Number of configured GPIO */

    /*
     * Configuring the LED GPIOs. Note: the related clocks are automatically set
     * by the kernel.
     * We configure 4 GPIOs here corresponding to the STM32 Discovery F407 LEDs (LD4, LD3, LD5, LD6):
     *     - PD12, PD13, PD14 and PD15 are in output mode
     * See the datasheet of the board here for more information:
     * https://www.st.com/content/ccc/resource/technical/document/user_manual/70/fe/4a/3f/e7/e1/4f/7d/DM00039084.pdf/files/DM00039084.pdf/jcr:content/translations/en.DM00039084.pdf
     *
     * NOTE: since we do not need an ISR handler for the LED gpios, we do not configure it (we only need to
     * synchronously set the LEDs)
     */
    leds.gpios[0].kref.port = GPIO_PD;
    leds.gpios[0].kref.pin = 12;
    leds.gpios[0].mask     = GPIO_MASK_SET_MODE | GPIO_MASK_SET_PUPD |
                             GPIO_MASK_SET_TYPE | GPIO_MASK_SET_SPEED;
    leds.gpios[0].mode     = GPIO_PIN_OUTPUT_MODE;
    leds.gpios[0].pupd     = GPIO_PULLDOWN;
    leds.gpios[0].type     = GPIO_PIN_OTYPER_PP;
    leds.gpios[0].speed    = GPIO_PIN_HIGH_SPEED;

    leds.gpios[1].kref.port = GPIO_PD;
    leds.gpios[1].kref.pin = 13;
    leds.gpios[1].mask     = GPIO_MASK_SET_MODE | GPIO_MASK_SET_PUPD |
                             GPIO_MASK_SET_TYPE | GPIO_MASK_SET_SPEED;
    leds.gpios[1].mode     = GPIO_PIN_OUTPUT_MODE;
    leds.gpios[1].pupd     = GPIO_PULLDOWN;
    leds.gpios[1].type     = GPIO_PIN_OTYPER_PP;
    leds.gpios[1].speed    = GPIO_PIN_HIGH_SPEED;

    leds.gpios[2].kref.port = GPIO_PD;
    leds.gpios[2].kref.pin = 14;
    leds.gpios[2].mask     = GPIO_MASK_SET_MODE | GPIO_MASK_SET_PUPD |
                             GPIO_MASK_SET_TYPE | GPIO_MASK_SET_SPEED;
    leds.gpios[2].mode     = GPIO_PIN_OUTPUT_MODE;
    leds.gpios[2].pupd     = GPIO_PULLDOWN;
    leds.gpios[2].type     = GPIO_PIN_OTYPER_PP;
    leds.gpios[2].speed    = GPIO_PIN_HIGH_SPEED;

    leds.gpios[3].kref.port = GPIO_PD;
    leds.gpios[3].kref.pin = 15;
    leds.gpios[3].mask     = GPIO_MASK_SET_MODE | GPIO_MASK_SET_PUPD |
                             GPIO_MASK_SET_TYPE | GPIO_MASK_SET_SPEED;
    leds.gpios[3].mode     = GPIO_PIN_OUTPUT_MODE;
    leds.gpios[3].pupd     = GPIO_PULLDOWN;
    leds.gpios[3].type     = GPIO_PIN_OTYPER_PP;
    leds.gpios[3].speed    = GPIO_PIN_HIGH_SPEED;

The `sys_init` syscall is used to initialize the device:

.. code-block:: c

    ret = sys_init(INIT_DEVACCESS, &leds, &desc_leds);

Leaving the initialization phase
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that all devices have been setup, it is possible to leave the initialization phase and
move forward to the nominal one using the `sys_init` syscall:


.. code-block:: c

    /* Devices and resources registration is finished */
    ret = sys_init(INIT_DONE);

Please be aware that after the `sys_init(INIT_DONE)` milestone, no further device and resource 
registration is possible.

Main loop in nominal phase
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the nominal phase, the leds task first checks for an IPC coming from the button app:

.. code-block:: c

    while (1) {
        id = id_button;
        msg_size = sizeof(button_pressed);

        ret = sys_ipc(IPC_RECV_ASYNC, &id, &msg_size, (char*) &button_pressed);
        ...

Beware of the `IPC_RECV_ASYNC`, meaning that we ask for an IPC reception in **asynchronous mode**.
This is important since we do not want the syscall to be blocking: some other work must be done periodically in order
to make the leds blinking.

Since the IPC reception is asynchronous, three cases can occur and can be discriminated using the return
value of the syscall:
  * `SYS_E_DONE`: there is an awaiting message sent by the button application
  * `SYS_E_BUSY`: there is no awaiting message
  * `SYS_E_DENIED` or `SYS_E_INVAL`: these are syscall errors and should not occur in a nominal behavior. Possible causes are missing permissions or improper parameters (ie. invalid task id)

In order to catch these cases, we use a `switch case`. When a button push event is caught through IPC, we 
change the internal state of the LEDs, making the other LEDs couple blink:

.. code-block:: c

        switch (ret) {
            case SYS_E_DONE:
                printf("BUTTON sent message: %x\n", button_pressed);

                if (button_pressed == true) {
                    /* Change leds state */
                    green_state   = (green_state == ON) ? OFF : ON;
                    orange_state  = (orange_state == ON) ? OFF : ON;
                    red_state     = (red_state == ON) ? OFF : ON;
                    blue_state    = (blue_state == ON) ? OFF : ON;

                    /* Show leds */
                    display_leds  = ON;
                }

                break;
            case SYS_E_BUSY:
                break;
            case SYS_E_DENIED:
            case SYS_E_INVAL:
            default:
                printf("sys_ipc(): error. Exiting.\n");
                return 1;
        }

After checking the IPC asynchronously, we can proceed to the effective hardware setting of the LEDs using
the `sys_cfg` syscall and their current state (ON or OFF):

.. code-block:: c

        ...
        if (display_leds == ON) {
            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[0].kref.val, green_state);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }

            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[1].kref.val, orange_state);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }

            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[2].kref.val, red_state);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }

            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[3].kref.val, blue_state);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }
        } else {
            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[0].kref.val, 0);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }
            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[1].kref.val, 0);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }
            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[2].kref.val, 0);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }
            ret = sys_cfg(CFG_GPIO_SET, (uint8_t) leds.gpios[3].kref.val, 0);
            if (ret != SYS_E_DONE) {
                printf("sys_cfg(): failed\n");
                return 1;
            }
        }
       ...

The global variable `display_leds` handles the current ON or OFF state of the
LEDs couple (the other couple not blinking being forced at OFF).

In order to effectively blink, a solution would be to perform an active polling
of the current time using `sys_get_systick`. We have chosen to use a more elegant
solution where the task sleeps 500 milliseconds with a possible awakening in
case of an IRQ (a button push) using the `sys_sleep` syscall. This has the advantage
of being less CPU time consuming:

.. code-block:: c

        /* Sleeping for 500 ms */
        sys_sleep (500, SLEEP_MODE_INTERRUPTIBLE);
