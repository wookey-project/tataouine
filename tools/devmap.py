#!/usr/bin/python3

import sys
# with collection, we keep the same device order as the json file
import json, collections

if len(sys.argv) != 2:
    print("usage: ", sys.argv[0], " <filename.json>\n");
    sys.exit(1);

filename = sys.argv[1];
with open(filename, "r") as jsonfile:
    data = json.load(jsonfile, object_pairs_hook=collections.OrderedDict);

# print type:
device_type = """
/* \\file devmap.h
 *
 * Copyright 2018 The wookey project team <wookey@ssi.gouv.fr>
 *   - Ryad     Benadjila
 *   - Arnauld  Michelizza
 *   - Mathieu  Renard
 *   - Philippe Thierry
 *   - Philippe Trebuchet
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 *     Unless required by applicable law or agreed to in writing, software
 *     distributed under the License is distributed on an "AS IS" BASIS,
 *     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *     See the License for the specific language governing permissions and
 *     limitations under the License.
 *
 * This file has been generated by tools/devmap.py
 *
 */
#ifndef DEVMAP_H_
#define DEVMAP_H_

#include "types.h"
#include "perm.h"
#include "soc-rcc.h"
#include "soc-interrupts.h"
#include "soc-dma.h"
#include "regutils.h"


/*
** This file defines the valid adress ranges where devices are mapped.
** This allows the kernel to check that device registration requests correct
** mapping.
**
** Of course these informations are SoC specific
** This file may be completed by a bord specific file for board devices
*/

/*!
** \\brief Structure defining the STM32 device map
**
** This table is based on doc STMicro RM0090 Reference manual memory map
** Only devices that may be registered by userspace are mapped here
**
** See #soc_devices_list
*/

struct device_soc_infos {
    char const *name;      /**< Device name, as as string */
    physaddr_t addr;       /**< Device MMIO base address */
    volatile uint32_t *rcc_enr;
                   /**< device's enable register (RCC reg) */
    uint32_t rcc_enb;      /**< device's enable bit in RCC reg */
    uint32_t size;         /**< Device MMIO mapping size */
    uint8_t mask;          /**< subregion mask when needed */
    uint8_t irq[4];        /**< IRQ line, when exist, or 0, max 4 irq lines per device */
    bool ro;           /**< True if the device must be mapped RO */
    res_perm_t minperm;   /**< minimum permission in comparison with the task's permission register */
};


/**
** \\var struct device_soc_infos *soc_device_list
** \\brief STM32F4 devices map
**
** This structure define all available devices and associated informations. This
** informations are separated in two parts:
**   - physical information (IRQ lines, RCC references, physical address and size...)
**   - security information (required permissions, usage restriction (RO mapping, etc.)
**
** This structure is used in remplacement of a full device tree for simplicity in small
** embedded systems.
*/
static struct device_soc_infos soc_devices_list[] = {
""";


footer= """
};

static const uint8_t soc_devices_list_size =
    sizeof(soc_devices_list) / sizeof(struct device_soc_infos);

struct device_soc_infos* soc_devmap_find_device
    (physaddr_t addr, uint16_t size);

void soc_devmap_enable_clock (const struct device_soc_infos *device);

struct device_soc_infos *soc_devices_get_dma // FIXME rename
    (enum dma_controller id, uint8_t stream);

#endif/*!DEVMAP_H_ */
""";

print(device_type);


#print data;
for device in data:
    # device name
    print("  { \"%s\", " % device, end='');
    dev = data[device];
    # device address
    print("%s, " % dev["address"], end='');
    # device control register
    print("%s, " % dev["enable_register"], end='');
    # device control register bit(s)
    enbrbits = dev["enable_register_bits"];

    print("%s" % enbrbits[0], end='');
    if len(enbrbits) > 1: # other bits ?
        for enb in enbrbits[1:]:
            print (" | %s" % enb, end='');
    print(", ", end='');

    # device size
    print("%s, " % dev["size"], end='');
    # device memory mapping mask
    print("%s, " % dev["memory_subregion_mask"], end='');
    # device irq
    irqs = dev["irqs"];
    print("{ ", end='');
    print(irqs[0], end='');
    for irq in irqs[1:]:
        print(", %s" % irq, end='');
    print(" }, ", end='');
    # device mapping ro ?
    print("%s, " % dev["read_only"], end='');
    # device permissions
    print("%s }," %  dev["permission"]);

print(footer);
