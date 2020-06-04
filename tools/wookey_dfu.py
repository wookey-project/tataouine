#!/usr/bin/env python

from __future__ import print_function

from os import path
from sys import argv
from math import ceil
import argparse
import re
import struct
import sys
import usb.core
import usb.util
import zlib
import time
import inspect
import array
import binascii

VID = 0xdead
PID = 0xcafe

USB_TIMEOUT             = 	9000
DFU_DESCRIPTOR_TYPE     =	0x21
DFU_WINDEX              = 	0
MAX_TRIES               = 	7
LDR_ADDRESS             = 	0x20000000
DFU_TSFR_SIZE		=	64
METADATA_SIZE		=	20

DFU_CMDS = {
    "DETACH"                : 0x00,
    "DNLOAD"                : 0x01,
    "UPLOAD"                : 0x02,
    "GETSTATUS"             : 0x03,
    "CLRSTATUS"             : 0x04,
    "GETSTATE"              : 0x05,
    "ABORT"                 : 0x06
}


DFU_REQUEST_TYPE = {
    "DETACH"                : 0x21,
    "DNLOAD"                : 0x21,
    "UPLOAD"                : 0xA1,
    "GETSTATUS"             : 0xA1,
    "CLRSTATUS"             : 0x21,
    "GETSTATE"              : 0xA1,
    "ABORT"                 : 0x21
}


DFU_STATE = {
    "appIDLE"		    : 0x0,
    "appDETACH"		    : 0x1,
    "IDLE"		    : 0x2,
    "DNLOAD-SYNC"	    : 0x3,
    "DNBUSY"		    : 0x4,
    "DNLOAD-IDLE"	    : 0x5,
    "MANIFESTSYNC"	    : 0x6,
    "MANIFEST"		    : 0x7,
    "MANIFEST-WAIT-RESET"   : 0x8,
    "UPLOAD-IDLE"	    : 0x9,
    "ERROR"		    : 0xA,
}

DFU_STATUS = {
    "OK"		    : 0x00,
    "TARGET"		    : 0x01,
    "FILE"		    : 0x02,
    "WRITE"		    : 0x03,
    "ERASE"		    : 0x04,
    "CHECK-ERASED"	    : 0x05,
    "PROG"		    : 0x06,
    "VERIFY"		    : 0x07,
    "ADDRESS"		    : 0x08,
    "NOTDONE"		    : 0x09,
    "FIRMWARE"		    : 0x0A,
    "VENDOR"		    : 0x0B,
    "USBR"		    : 0x0C,
    "POR"		    : 0x0D,
    "UNKNOWN"		    : 0x0E,
    "STALLEDPKT"	    : 0x0F,
    "HEADER"		    : 0x20,
    "SIGNATURE"		    : 0x21,
}

def get_key_by_value(dic,val):
    return list(dic.keys())[list(dic.values()).index(val)]

def print_status(status):
    return str(get_key_by_value(DFU_STATUS, status.tolist()[0]))

def print_state(state):
    return str(get_key_by_value(DFU_STATE, state.tolist()[0]))

class dfu_device:
    def __init__(self, dev):
        self.dev = dev
        self.connect()

    def connect(self):
        for cfg in self.dev:
            for intf in cfg:
                iface_class = intf.bInterfaceClass
                iface_subclass = intf.bInterfaceSubClass
                if (iface_class == 0xfe and iface_subclass == 1):
                    print("[+] Found DFU interface...")
                    print("[-] Configuration\t:\t",str(cfg.bConfigurationValue))
                    print(' |- Interface Number\t:\t',str(intf.bInterfaceNumber))
                    print(' |- Alternate settings\t:\t',str(intf.bAlternateSetting))
                    for ep in intf:
                        print(' |--Endpoint Address\t:\t', str(ep.bEndpointAddress))
                    self.intf = intf.bInterfaceNumber
                    self.altsetting = intf.bAlternateSetting
                    self.cfg = cfg
                    break

        print("[+] Setting configuration...")
        self.dev.set_configuration(self.cfg)
        print("[+] Claiming device...")
        usb.util.claim_interface(self.dev, self.intf)
	print("[*] Getting device descriptor...")
        self.std_get_dev_desc()
	print("[*] Getting Status...")
	myStatus = self.get_status()
	if(myStatus.tolist()[0] == DFU_STATUS["OK"]):
	    print(" |- Status\t\t:  \t{}".format(print_status(myStatus)))
	else:
	    print(" |- Error\t\t:  \t{}".format(print_status(myStatus)))
	    print(" |- Clearing status...")
	    self.clr_status()
	    myStatus = self.get_status()
	    if(myStatus.tolist()[0] == DFU_STATUS["OK"]):
	    	print(" |- Status\t\t:  \t{}".format(print_status(myStatus)))
	    else:
	    	print(" |- Error\t\t:  \t{}".format(print_status(myStatus)))
		print(" |- Something went wrong, please reset the board")
		quit()

    def std_get_dev_desc(self):
	myDescriptor =  self.dev.ctrl_transfer(
				bmRequestType	= 0x80,
				bRequest	= 0x06,
				wValue		= (1<<8),
				wIndex		= 0,
				data_or_wLength	= 18,
				timeout		= USB_TIMEOUT)
        print(" |- ",str(myDescriptor.tolist()))

    def clr_status(self):
        self.dev.ctrl_transfer(
                                bmRequestType   = DFU_REQUEST_TYPE["CLRSTATUS"],
                                bRequest        = DFU_CMDS["CLRSTATUS"],
                                wValue          = 0,
                                wIndex          = self.intf,
                                data_or_wLength = None,
                                timeout         = USB_TIMEOUT)

    def get_status(self):
	myStatus = self.dev.ctrl_transfer(
                                bmRequestType   = DFU_REQUEST_TYPE["GETSTATUS"],
                                bRequest        = DFU_CMDS["GETSTATUS"],
                                wValue          = 0,
                                wIndex          = 0,
                                data_or_wLength = 6,
                                timeout         = USB_TIMEOUT)
	# Response is an array of unsigned char :
	# array('B', [bStatus, bwPollTimeout[0], bwPT[1], bwPT[2], bState, iString] )
	# array.tolist() to convert it to an ordinary list
        return myStatus

    def clr_state(self):
        self.dev.ctrl_transfer(
                                bmRequestType   = DFU_REQUEST_TYPE["CLRSTATE"],
                                bRequest        = DFU_CMDS["CLRSTATE"],
                                wValue          = 0,
                                wIndex          = self.intf,
                                data_or_wLength = None,
                                timeout         = USB_TIMEOUT)

    def get_state(self):
	myState = self.dev.ctrl_transfer(
                                bmRequestType   = DFU_REQUEST_TYPE["GETSTATE"],
                                bRequest        = DFU_CMDS["GETSTATE"],
                                wValue          = 0,
                                wIndex          = 0,
                                data_or_wLength = 1,
                                timeout         = USB_TIMEOUT)
	return myState

    def upload(self):
        i = 0
	uploadInProgress = True
	myFirmware = []
	print("[*] Retrieving firmware...")
	print(" |- Starting ...")
	while(uploadInProgress):
	    myFirmwarePacket = self.dev.ctrl_transfer(
                                bmRequestType   = DFU_REQUEST_TYPE["UPLOAD"],
                                bRequest        = DFU_CMDS["UPLOAD"],
                                wValue          = 0,
                                wIndex          = 0,
                                data_or_wLength = DFU_TSFR_SIZE,
                                timeout         = USB_TIMEOUT).tolist()
	    size = len(myFirmwarePacket)
	    myStatus = self.get_status()
	    if(myStatus.tolist()[4] != DFU_STATUS["OK"]):
		print("\n |- An error occured\t:\t{}".format(print_status(myStatus)))
		quit()
	    if(size < 0):
	 	print("\n |- ERROR")
		uploadInProgress = False
	    elif(size == DFU_TSFR_SIZE):
                sys.stdout.write("\r |- Firmware packet #{}\t:\t{}B".format(i, size))
		sys.stdout.flush()
		myFirmware = myFirmware + myFirmwarePacket
	    	i+=1
	    elif(size < DFU_TSFR_SIZE):
		print("\n |- Last packet #{}\t\t:\t{}B".format(i, size))
		myFirmware = myFirmware + myFirmwarePacket
		if (size):
			i+=1
		uploadInProgress = False
	    else:
		print("\n |- ERROR\t\t:\tReceived too many bytes !")
		uploadInProgress = False

	print(" |- Done : Received {}kB ({} packets, {}B)".format(len(myFirmware)/1024, i, len(myFirmware)))
	print("[*] Saving firmware...")
	# Format data because unhexlify accepts only even-length number,
	# and integers < 16 are odd-length number
	f = open(argv[2], 'wb+')
	for c in myFirmware:
		if c < 10:
			f.write(
				binascii.unhexlify('0%x' % c)
			)
		elif c < 16:
			f.write(
				binascii.unhexlify('0%s' % format(c, 'x'))
			)
		else:
			f.write(
				binascii.unhexlify(format(c, 'x'))
			)
	print(" |-- Done.")
	# Get status
	print("[*] Getting Status...")
	print(" |- Upload complete \t\t:  \t{}".format(print_status(self.get_status())))
        return len(myFirmware)

    def packet_dnload(self, packet):
	    self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
			    DFU_CMDS["DNLOAD"],
			    0,
			    self.intf,
			    packet,
			    USB_TIMEOUT)

    def dnload_status(self, i):
	# Get device status
	myStatus = self.get_status()
	if(myStatus.tolist()[0] == DFU_STATUS["OK"]):
	    sys.stdout.write("\r |- Packet #{}\t\t:\t{}".format(i, print_status(myStatus)))
	    sys.stdout.flush()
	else:
	    print("\n |- ERROR\t\t:\t{}".format(print_status(myStatus)))
	    print(" |- Please reset the board")
	    quit()

    def dnload(self):
	print("[*] Downloading firmware...")
	# Open bin file
	f = open(argv[2], "rb")
	# Retrieving siglen from file
	f.seek(16, 0)
	fwx_siglen = ord(f.read(1))
	f.seek(0, 0)
	# Computing size and packets number
	size = path.getsize(argv[2])
	pkt_nb = (size-20-fwx_siglen)/64
	if(size%64 > 0):
		pkt_nb = pkt_nb + 1
	# Computing fwx and sig size
	fwx_size = size - METADATA_SIZE - fwx_siglen
	sig_pkt_nb = fwx_siglen/64
	if(fwx_siglen%64 > 0):
		sig_pkt_nb = sig_pkt_nb + 1
	print(" |- Firmware size\t:\t", fwx_size)
	print(" |- Total size\t\t:\t", size)
	# Sending routine
	print(" |- Starting download...")
	fwx = []
	# Metadata (5 * uint32_t)
	for k in range(20):
	    fwx.append(ord(f.read(1)))
	self.packet_dnload(fwx)
	self.dnload_status(0)

	# Signature
	# Set offset
	f.seek(fwx_size+20, 0)
	# Send signature
	for i in range(sig_pkt_nb):
	    del fwx[:]
            if(i == sig_pkt_nb-1 and fwx_siglen%64 != 0): # Last packet < 64B FIXME sig size
	    	for k in range(fwx_siglen % 64):
		    fwx.append(ord(f.read(1)))
	    else:
	    	for k in range(64):
	    	    fwx.append(ord(f.read(1)))
	    self.packet_dnload(fwx)
	    self.dnload_status(i+1)

	# Firmware
	# Set offset
	f.seek(20, 0)
	# Send firmware
	for i in range(pkt_nb):
		# Setting and filling buffer to send
		del fwx[:]
		# Raw firmware
		if(fwx_size - (i*64) < 64): # Last packet < 64B
		    for k in range((fwx_size - (i*64))% 64):
			fwx.append(ord(f.read(1)))
		else: # Firmware packet
		    for k in range(64):
		        fwx.append(ord(f.read(1)))
		# Send buffer
		self.packet_dnload(fwx)
		self.dnload_status(i + sig_pkt_nb + 1)
	f.close()

	# Informs that transfer is complete
	self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
			    	DFU_CMDS["DNLOAD"],
			    	0,
			    	self.intf,
			    	0,
			    	USB_TIMEOUT*4)

	# Get status
	myStatus = self.get_status()
	if(myStatus.tolist()[0] == DFU_STATUS["OK"]):
	   print("\n |- Download complete\t:\t{}".format(print_status(myStatus)))
	else:
	    print("\n |- ERROR\t\t:\t{}".format(print_status(myStatus)))
	    myState = self.get_state()
	    print(" |- Device state\t:\t{}".format(print_state(myState)))
	    print(" |- Please reset the board")
	    quit()

    def mass_erase(self):
        # Send DNLOAD with first byte=0x41
        self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                            DFU_CMDS["DNLOAD"],
                                0,
                                self.intf,
                                "\x41",
                                USB_TIMEOUT)

        # wait for the command to complete
        for i in range(MAX_TRIES):
            if self.get_status() != DFU_STATE["DOWNLOAD_BUSY"]:
                break
            else:
                time.sleep(1)

        if i == tries:
            raise Exception("mass_erase() failed")

        # Check command state
        if self.get_status() != DFU_STATE["DOWNLOAD_IDLE"]:
            raise Exception("mass_erase() failed")


    def page_erase(self, addr):
        print("Erasing page: 0x%x..." % (addr))

        # Send DNLOAD with first byte=0x41 and page address
        buf = struct.pack("<BI", 0x41, addr)
        self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                                DFU_CMDS["DNLOAD"],
                                0,
                                self.intf,
                                buf,
                                USB_TIMEOUT)

        # wait for the command to complete
        for i in range(MAX_TRIES):
            if self.get_status() != DFU_STATE["DOWNLOAD_BUSY"]:
                break
            else:
                time.sleep(1)

        if i == tries:
            raise Exception("page_erase() failed")

        # Check command state
        if self.get_status() != DFU_STATE["DOWNLOAD_IDLE"]:
            raise Exception("page_erase() failed")


    def set_address(self, addr):
        # Send DNLOAD with first byte=0x21 and page address
        buf = struct.pack("<BI", 0x21, addr)
        self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                                DFU_CMDS["DNLOAD"],
                                0,
                                self.intf,
                                buf,
                                USB_TIMEOUT)

    def set_address(self, addr):
        # Send DNLOAD with first byte=0x21 and page address
        buf = struct.pack("<BI", 0x21, addr)
        self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                                DFU_CMDS["DNLOAD"],
                                0,
                                self.intf,
                                buf,
                                USB_TIMEOUT)

        # wait for the command to complete
        for i in range(MAX_TRIES):
            if self.get_status() != DFU_STATE["DOWNLOAD_BUSY"]:
                break
            else:
                time.sleep(1)

        if i == tries:
            raise Exception("set_address() failed")

        # Check command state
        if self.get_status() != DFU_STATE["DOWNLOAD_IDLE"]:
            raise Exception("set_address() failed")


    def write_memory(self, addr, buf, progress=None, progress_addr=0, progress_size=0):
        xfer_count = 0
        xfer_bytes = 0
        xfer_total = len(buf)
        xfer_base = addr

        while xfer_bytes < xfer_total:
            if xfer_count % 512 == 0:
                print ("Addr 0x%x %dKBs/%dKBs..." % (xfer_base + xfer_bytes,
                                                     xfer_bytes // 1024,
                                                     xfer_total // 1024))
            if progress and xfer_count % 256 == 0:
                progress(progress_addr, xfer_base + xfer_bytes - progress_addr, progress_size)

            # Set mem write address
            self.set_address(xfer_base+xfer_bytes)

            # Send DNLOAD with fw data
            chunk = min(64, xfer_total-xfer_bytes)
            self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                                DFU_CMDS["DNLOAD"],
                                2,
                                self.intf,
                                buf[xfer_bytes:xfer_bytes + chunk],
                                USB_TIMEOUT)

            # wait for the command to complete
            for i in range(MAX_TRIES):
                if self.get_status() != DFU_STATE["DOWNLOAD_BUSY"]:
                    break
                else:
                    time.sleep(1)

            if i == tries:
                raise Exception("write_memory() failed")

            # Check command state
            if self.get_status() != DFU_STATE["DOWNLOAD_IDLE"]:
                raise Exception("write_memory() failed")

            xfer_count += 1
            xfer_bytes += chunk


    def write_page(buf, xfer_offset, xfer_base = LDR_ADDRESS):
        # Set mem write address
        set_address(xfer_base+xfer_offset)

        # Send DNLOAD with fw data
        self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                                DFU_CMDS["DNLOAD"],
                                2,
                                self.intf,
                                buf,
                                USB_TIMEOUT)


        # wait for the command to complete
        for i in range(MAX_TRIES):
            if self.get_status() != DFU_STATE["DOWNLOAD_BUSY"]:
                break
            else:
                time.sleep(1)

        if i == tries:
            raise Exception("write_page() failed")

        # Check command state
        if self.get_status() != DFU_STATE["DOWNLOAD_IDLE"]:
            raise Exception("write_page() failed")

        print ("Wrote: 0x%x " % (xfer_base + xfer_offset))


    def exit_dfu(self):
        # set jump address
        set_address(LDR_ADDRESS)

        # Send DNLOAD with 0 length to exit DFU
        self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
                                DFU_CMDS["DNLOAD"],
                                2,
                                self.intf,
                                buf,
                                USB_TIMEOUT)

        try:
            # Execute last command
            if get_status() != DFU_STATE["DFU_MANIFEST"]:
                print("Failed to reset device")

            # Release device
            usb.util.dispose_resources(self.dev)
        except:
            pass


class FilterDFU(object):
    def __call__(self, dev):
        for cfg in dev:
            for intf in cfg:
                iface_class = intf.bInterfaceClass
                iface_subclass = intf.bInterfaceSubClass
                return (iface_class == 0xfe and iface_subclass == 1)


def get_dfu_devices(*args, **kwargs):
    # convert to list for compatibility with newer PyUSB
    return list(usb.core.find(*args,find_all=True,custom_match=FilterDFU(),**kwargs))


def list_dfu_devices(*args, **kwargs):
    devs = get_dfu_devices(*args, **kwargs)
    if len(devs) <= 0:
        print("No DFU capable devices found :-(")
        return
    for d in devs:
        print("Bus {} Device {:03d}: ID {:04x}:{:04x}"
            .format(d.bus, d.address, d.idVendor, d.idProduct))
    return devs

def print_usage():
    print("\nUsage :\t./wookey_dfu.py [-u|-U] output_file\t", \
	  "Save device firmware in output_file\n", \
    	  "\t./wookey_dfu.py [-d|-D] input_file\t", \
	  "Send firmware input_file to device\n")

def main():
    # Usage
    if(len(argv) == 1 or ( len(argv) == 2 and (argv[1] == "-h" or argv[1] == "--help"))):
	print_usage()
	quit()

    # Launch
    dev = list_dfu_devices(idVendor=VID, idProduct=PID)
    if dev:
    	dfu_dev = dfu_device(dev[0])
	if(len(argv) > 2):
	    if(argv[1] == "-U" or argv[1] == "-u"):
	   	dfu_dev.upload()
	    elif(argv[1] == "-D" or argv[1] == "-d"):
		dfu_dev.dnload()
	    else:
		print("\n{0}: Input arguments error\n".format(argv[0]))
		print_usage()
		quit()
	else:
	    print("No device found...\n")
	quit()


if __name__ == "__main__":
    main()


