## gen_firmware.py ##

from sys import argv
import os
from intelhex import *

DEBUG = 0

# Assert arguments
if(len(argv) < 3):
    if(DEBUG):
        print("\n{0}: Input arguments error (need 2 at least)\n".format(argv[0]))
    quit()
else:
    if(DEBUG):
        print("{0}: Parsing {1} arguments".format(argv[0],len(argv)-1))

# Create new buffer for hex files
if(DEBUG):
    print("{0}: Creating buffer binary file".format(argv[0]))
wookey = IntelHex()

# Table for hex files
f = []

# Open and merge hex files
for i in range(1, len(argv)-2):
    if(DEBUG):
        print("{0}: Reading argument {1} to add to hex file".format(argv[0], i))
    new_hex = IntelHex(argv[i])
    wookey.merge(new_hex, overlap='ignore')

if(DEBUG):
    print("{0}: Merging done".format(argv[0]))

# Infer the main binary name from extension
base = os.path.splitext(argv[len(argv)-2])[0]
# Build both bin and hex files
# Build .hex file
if(DEBUG):
    print("Building {0} file".format(argv[len(argv)-2]))
wookey.tofile(base+".hex", format='hex')
# Build .bin file
if(DEBUG):
    print("Building {0} file".format(argv[len(argv)-2]))
wookey.tofile(base+".bin", format='bin')
