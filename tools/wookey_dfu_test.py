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

#VID = 0xffff
#PID = 0x0004
VID = 0x1d50
PID = 0x6002

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

def get_first_value(myArray):
    return myArray.tolist()[0]

def print_status(status):
    return str(get_key_by_value(DFU_STATUS, get_first_value(status)))

def print_state(state):
    return str(get_key_by_value(DFU_STATE, get_first_value(state)))

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
                    self.intf = intf.bInterfaceNumber
                    self.altsetting = intf.bAlternateSetting
                    self.cfg = cfg
                    break

        self.dev.set_configuration(self.cfg)
        usb.util.claim_interface(self.dev, self.intf)
        self.std_get_dev_desc()
	myStatus = self.get_status()
	if(myStatus.tolist()[0] == DFU_STATUS["OK"]):	
	    pass
	else:
	    self.clr_status()
	    myStatus = self.get_status()
	    if(myStatus.tolist()[0] == DFU_STATUS["OK"]):	
		pass
	    else:
		print("*** Something went wrong, please reset the board ***")
		quit()

    def std_get_dev_desc(self):
	myDescriptor =  self.dev.ctrl_transfer(
				bmRequestType	= 0x80,
				bRequest	= 0x06,
				wValue		= (1<<8),
				wIndex		= 0,
				data_or_wLength	= 18,
				timeout		= USB_TIMEOUT)

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

    def restart_state_machine(self):
	myStatus = self.get_status()
	if(myStatus.tolist()[0] != DFU_STATUS["OK"]):	
	    self.clr_status()
	    myStatus = self.get_status()
	    if(myStatus.tolist()[0] == DFU_STATUS["OK"]):	
		return
	    else:
	    	print("\n*** GLOBAL TEST ERROR ***")
		quit()

    def upload(self):
        i = 0
	uploadInProgress = True
	myFirmware = []
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
		quit()
	    if(size < 0):
		uploadInProgress = False

	    elif(size == DFU_TSFR_SIZE):
		myFirmware = myFirmware + myFirmwarePacket
	    	i+=1

	    elif(size < DFU_TSFR_SIZE):
		myFirmware = myFirmware + myFirmwarePacket
		if (size):
			i+=1
		uploadInProgress = False
	    else:
		uploadInProgress = False
	
	# Format because unhexlify accepts only even-legnth number,
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
	#print("[*] Getting Status...")
	#print(" |- Upload complete \t\t:  \t{}".format(print_status(self.get_status())))
        return len(myFirmware)

    def packet_dnload(self, packet):
	    self.dev.ctrl_transfer( DFU_REQUEST_TYPE["DNLOAD"],
			    DFU_CMDS["DNLOAD"],
			    0,
			    self.intf,
			    packet,
			    USB_TIMEOUT)

    # Get status
    # Return [1,2]
    # 1 : True: OK, False: FAILED
    # 2 : Status
    def dnload_status(self, i):
	# Get device status
	myStatus = self.get_status()
	if(myStatus.tolist()[0] == DFU_STATUS["OK"]):
	   return [True, 0] 
	else:
	    return [False, get_first_value(myStatus)] 

    # input_file is firmware image to send
    # test_choice is test number [0..10]
    # test_curve is used curve [0..8]
    def dnload(self, input_file, test_choice, test_curve):
	# Control value
	ret = [True,0]
	# Open bin file
	f = open(input_file, "rb")
	# Retrieving siglen from file
	f.seek(16, 0)
	fwx_siglen = ord(f.read(1))
	f.seek(0, 0)
	# Computing size and packets number
	size = path.getsize(input_file)
	pkt_nb = (size-20-fwx_siglen)/64
	if(size%64 > 0):
		pkt_nb = pkt_nb + 1
	# Computing fwx and sig size
	fwx_size = size - METADATA_SIZE - fwx_siglen
	sig_pkt_nb = fwx_siglen/64
	if(fwx_siglen%64 > 0):
		sig_pkt_nb = sig_pkt_nb + 1
	# Sending routine
	fwx = []

	# Metadata (5 * uint32_t)
	for k in range(20):
	   fwx.append(ord(f.read(1)))
	# Append test infos
	fwx.append(test_choice)
	fwx.append(test_curve)
	#print(fwx)
   	# Corrupt header
	if(test_choice ==  9):
	    fwx[18] = (fwx[18] + 135) % 0xff	
	# Send packet
	#print(fwx)
	#print("Sending metadata...")
	self.packet_dnload(fwx)
	ret = self.dnload_status(0)
	# Get error
	if(test_choice ==  9 and ret[0] == True):
	    print("\t\t\tFAILED (Didn't detect wrong header)")
	    quit()
	elif(test_choice ==  9 and ret[0] == False):
	    print("\t\t\tOK")
	    return
	# Signature
	# Set offset
	f.seek(fwx_size+20, 0)
	# Send signature
	#print("Sending sig...")
	for i in range(sig_pkt_nb):
	    del fwx[:]
	    if(i == sig_pkt_nb-1 and fwx_siglen%64 != 0): # Last packet < 64B
	    	for k in range(fwx_siglen % 64):
		    fwx.append(ord(f.read(1)))
	    else:
	    	for k in range(64):
	    	    fwx.append(ord(f.read(1)))
	    # Corrupt signature
	    if(test_choice == 10):
	    	fwx[0] = (fwx[0] + 0x45) % 0xff
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
	    print("\t\t\tOK")
	elif(test_choice == 10 and myStatus.tolist()[0] == DFU_STATUS["SIGNATURE"]):
	    print("\t\t\tOK")
	else:
	    myState = self.get_state()
	    print("\t\t\tFAILED ({}: {})".format(print_state(myState), print_status(myStatus)))

    # Test function
    def test_dfu(self):
	# Test each curves
	print("*** Testing DFU mode ***")
	print("Test #1")
        self.dnload("images/fwx_fr256.bin", 0, 0)
	self.restart_state_machine()
	print("Test #2")
        self.dnload("images/fwx_sp256.bin", 1, 1)
	self.restart_state_machine()
	print("Test #3")
        self.dnload("images/fwx_sp384.bin", 2, 2)
	self.restart_state_machine()
	print("Test #4")
        self.dnload("images/fwx_sp521.bin", 3, 3)
	self.restart_state_machine()
	print("Test #5")
        self.dnload("images/fwx_bp256.bin", 4, 4)
	self.restart_state_machine()
	print("Test #6")
        self.dnload("images/fwx_bp384.bin", 5, 5)
	self.restart_state_machine()
	print("Test #7")
        self.dnload("images/fwx_bp512.bin", 6, 6)
	self.restart_state_machine()
	print("Test #8")
        self.dnload("images/fwx_gt256.bin", 7, 7)
	self.restart_state_machine()
	print("Test #9")
        self.dnload("images/fwx_gt512.bin", 8, 8)
	self.restart_state_machine()
	# Test with a wrong header
	print("Test #10")
        self.dnload("images/fwx_fr256.bin", 9, 0)
	self.restart_state_machine()
	# Test with a wrong signature
	self.restart_state_machine()
	print("Test #11")
        self.dnload("images/fwx_fr256.bin", 10, 0)
	self.restart_state_machine()

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

def main():
    # Launch
    dev = list_dfu_devices(idVendor=VID, idProduct=PID)
    if dev:
    	dfu_dev = dfu_device(dev[0])
	dfu_dev.test_dfu()
    else:
        print("No device found...\n")
	quit()

if __name__ == "__main__":
    main()


