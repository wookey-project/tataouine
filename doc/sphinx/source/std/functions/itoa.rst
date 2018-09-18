itoa
----
Convert an integer into a string
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Synopsys
""""""""

itoa uses the printf ring buffer.

itoa respects the following prototype::

   #include "string.h"

   void itoa(unsigned long long value, uint8_t base);


