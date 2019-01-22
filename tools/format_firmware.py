#!/usr/bin/python

from intelhex import *
import json, collections

# Import our local utils
from crypto_utils import *
from firmware_utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print("Error when executing %s\n\tUsage:\t%s json_layout hex_file_to_format" % (executable, executable))
    sys.exit(-1)



if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    # Get the arguments
    if len(sys.argv) <= 2:
        PrintUsage()
    json_path = sys.argv[1]
    hex_path = sys.argv[2]
    # Open and parse json layout
    with open(json_path, "r") as jsonfile:
        json_data = json.load(jsonfile, object_pairs_hook=collections.OrderedDict);
    # Open hex file
    firmware_hex = IntelHex()
    try:
        firmware_hex.loadhex(hex_path)
    except:
        print("Error: error when opening %s as a hex file ..." % sys.argv[2]);
        sys.exit(-1);
    # Get flip and flop base
    dual_bank = True
    flip_base_addr = int(json_data['flash-flip']['address'], 0)
    flip_size = int(json_data['flash-flip']['size'], 0)
    flop_base_addr = int(json_data['flash-flop']['address'], 0)
    flop_size = int(json_data['flash-flop']['size'], 0)
    flash_base_addr = flip_base_addr
    if (flop_base_addr == None) and (flop_size == None):
        dual_bank = False
    if (flip_base_addr == None) or (flip_size == None):
        print("Error: FLIP not found in json layout %s" % (json_path));
        sys.exit(-1);
    if (dual_bank == True) and ((flop_base_addr == None) or (flop_size == None)):
        print("Error: FLOP not found in json layout %s" % (json_path));
        sys.exit(-1);
    if dual_bank == True:
        flash_size = flip_size + flop_size
    flash_max_addr = flash_base_addr + flash_size
    print("FLIP base = 0x%x, size = 0x%x" % (flip_base_addr, flip_size))
    print("FLOP base = 0x%x, size = 0x%x" % (flop_base_addr, flop_size))
    # Now sanity check on all the addresses of the hex file, and fill
    last_addr_stop = None
    holes_to_fill = []
    (addr_start, addr_stop) = firmware_hex.segments()[0]
    if addr_start > flash_base_addr:
        holes_to_fill.append(addr_start, flash_base_addr)
    for (addr_start, addr_stop) in firmware_hex.segments():
        if (addr_start < flash_base_addr) or (addr_start > flash_max_addr):
            print("Error: segment [0x%x, 0x%x] is not in flash range (0x%x, 0x%x)" % (addr_start, addr_stop, size, flash_base_addr, flash_max_addr));
            sys.exit(-1)
        if (addr_stop < flash_base_addr) or (addr_stop > flash_max_addr):
            print("Error: segment [0x%x, 0x%x] is not in flash range (0x%x, 0x%x)" % (addr_start, addr_stop, size, flash_base_addr, flash_max_addr));
            sys.exit(-1)
        if last_addr_stop != None:
            if(addr_start != last_addr_stop):
                holes_to_fill.append((last_addr_stop, addr_start-last_addr_stop))
        last_addr_stop = addr_stop
    if last_addr_stop != flash_max_addr:
        holes_to_fill.append((last_addr_stop, flash_max_addr-last_addr_stop))
    print("%s addresses sanity check is OK!" % (hex_path))
    # Now fill the holes with random data
    for (hole_start, size) in holes_to_fill:
        #print("Filling 0x%x-0x%x"%(hole_start, hole_start+size))
        for i in range(hole_start, hole_start+size):
            firmware_hex[i] = random.randint(0, 255)
    # Now get flip-shr and flop-shr base address and size
    flip_shr_base_addr = int(json_data['flash-flip-shr']['address'], 0)
    flip_shr_size = int(json_data['flash-flip-shr']['size'], 0)
    if dual_bank == True:
        flop_shr_base_addr = int(json_data['flash-flop-shr']['address'], 0)
        flop_shr_size = int(json_data['flash-flop-shr']['size'], 0)
    # magic
    initial_flip_magic = expand(inttostring(0x0), 32, "LEFT")
    # partition type
    initial_flip_type = expand(inttostring(partitions_types['FLIP']), 32, "LEFT")
    # version = 0 for initial firmware
    initial_flip_version = expand(inttostring(0x0), 32, "LEFT")
    # length
    initial_flip_len = expand(inttostring(flip_size), 32, "LEFT")
    # sig length to zero since original firmware is not signed (pushed through jtag)
    initial_flip_siglen = expand(inttostring(0x0), 32, "LEFT")
    # chunksize to zero
    initial_flip_chunksize = expand(inttostring(0x0), 32, "LEFT") 
    if dual_bank == True:
        # magic
        initial_flop_magic = expand(inttostring(0x0), 32, "LEFT")
        # partition type
        initial_flop_type = expand(inttostring(partitions_types['FLOP']), 32, "LEFT")
        # version = 0 for initial firmware
        initial_flop_version = expand(inttostring(0x0), 32, "LEFT")
        # length
        initial_flop_len = expand(inttostring(flop_size), 32, "LEFT")
        # sig length to zero since original firmware is not signed (pushed through jtag)
        initial_flop_siglen = expand(inttostring(0x0), 32, "LEFT")
        # chunksize to zero
        initial_flop_chunksize = expand(inttostring(0x0), 32, "LEFT") 
    # Compute the hash of binary flip and flop with prepended initial header
    flip_header = initial_flip_magic + initial_flip_type + initial_flip_version + initial_flip_len + initial_flip_siglen + initial_flip_chunksize
    (flip_hash_value, _, _) = local_sha256(flip_header + firmware_hex[flip_shr_base_addr:flip_base_addr+flip_size].tobinstr())
    if dual_bank == True:
        flop_header = initial_flop_magic + initial_flop_type + initial_flop_version + initial_flop_len + initial_flop_siglen + initial_flop_chunksize
        (flop_hash_value, _, _) = sha256(flop_header + firmware_hex[flop_shr_base_addr:flop_base_addr+flop_size].tobinstr())
    # Now forge the SHR sections
    # FLIP
    for i in range(flip_shr_base_addr, flip_shr_base_addr+flip_shr_size):
        firmware_hex[i] = 0xff
    # Place the base header
    for i in range(0, len(flip_header)):
        firmware_hex[flip_shr_base_addr+i] = ord(flip_header[i])
    # Place the hash value
    for i in range(0, len(flip_hash_value)): 
        firmware_hex[flip_shr_base_addr+len(flip_header)+4+i] = ord(flip_hash_value[i])
    # Place the bootable value
    for i in range(0, len(firmware_bootable_types['BOOTABLE'])): 
        firmware_hex[flip_shr_base_addr+(flip_shr_size/2)+i] = ord(firmware_bootable_types['BOOTABLE'][i])
    # Now compute the crc32 of this hole sector and place it
    string_to_crc = ""
    for i in range(0, flip_shr_size):
        string_to_crc += chr(firmware_hex[flip_shr_base_addr+i])
    crc = expand(inttostring(dfu_crc32_update(string_to_crc, 0xffffffff)), 32, "LEFT")[::-1]
    for i in range(0, len(crc)):
        firmware_hex[flip_shr_base_addr+len(flip_header)+i] = ord(crc[i])
    # FLOP
    if dual_bank == True:
        for i in range(flop_shr_base_addr, flop_shr_base_addr+flop_shr_size):
            firmware_hex[i] = 0xff
        header = initial_flop_magic + initial_flop_type + initial_flop_version + initial_flop_len + initial_flop_siglen + initial_flop_chunksize
        # Place the base header
        for i in range(0, len(header)):
            firmware_hex[flop_shr_base_addr+i] = ord(header[i])
        # Place the hash value
        for i in range(0, len(flop_hash_value)): 
            firmware_hex[flop_shr_base_addr+(7*4)+i] = ord(flop_hash_value[i])
        # Place the bootable value
        for i in range(0, len(firmware_bootable_types['BOOTABLE'])): 
            firmware_hex[flop_shr_base_addr+(flop_shr_size/2)+i] = ord(firmware_bootable_types['BOOTABLE'][i])
        # Now compute the crc32 of this hole sector and place it
        string_to_crc = ""
        for i in range(0, flop_shr_size):
            string_to_crc += chr(firmware_hex[flop_shr_base_addr+i])
        crc = expand(inttostring(dfu_crc32_update(string_to_crc, 0xffffffff)), 32, "LEFT")[::-1]
        for i in range(0, len(crc)):
            firmware_hex[flop_shr_base_addr+(6*4)+i] = ord(crc[i])

    # Get base name
    base_path = os.path.dirname(hex_path)
    # Dump the new hex and bin files
    firmware_hex.tofile(base_path+"/wookey.hex", format='hex')
    firmware_hex.tofile(base_path+"/wookey.bin", format='bin')
    # Dump FLIP to sign
    firmware_hex[flip_shr_base_addr:flip_base_addr+flip_size].tofile(base_path+"/flip_fw.hex", format='hex')
    firmware_hex[flip_shr_base_addr:flip_base_addr+flip_size].tofile(base_path+"/flip_fw.bin", format='bin')
    # Dump FLOP to sign
    firmware_hex[flop_shr_base_addr:flop_base_addr+flop_size].tofile(base_path+"/flop_fw.hex", format='hex')
    firmware_hex[flop_shr_base_addr:flop_base_addr+flop_size].tofile(base_path+"/flop_fw.bin", format='bin')
