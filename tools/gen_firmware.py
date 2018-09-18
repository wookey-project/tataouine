#!/usr/bin/python
## gen_firmware.py ##

from sys import argv
import bincopy

DEBUG = 0

# Assert arguments
if(len(argv) < 3):
    if(DEBUG):
        print "\n{0}: Input arguments error (need 2 at least)\n".format(argv[0])
    quit()
else:
    if(DEBUG):
        print "{0}: Parsing {1} arguments".format(argv[0],len(argv)-1)

# Create new buffer for hex files
if(DEBUG):
    print "{0}: Creating buffer binary file".format(argv[0])
wookey = bincopy.BinFile()

# Table for hex files
f = []

# Open and merge hex files
for i in range(1, len(argv)-2):
    if(DEBUG):
        print "{0}: Reading argument {1} to add to hex file".format(argv[0], i)
    f = open(argv[i])
    wookey.add_ihex(f.read(), True)

if(DEBUG):
    print wookey.info()

if(DEBUG):
    print "{0}: Merging done".format(argv[0])

# If last argument is 0, build .hex file
if(not int(argv[len(argv)-1])):
    if(DEBUG):
        print "Building {0} file".format(argv[len(argv)-2])
    output_hex = open(argv[len(argv)-2], 'w')
    print >> output_hex, wookey.as_ihex()
    output_hex.close()
# Else, build .bin file
else:
    if(DEBUG):
        print "Building {0} file".format(argv[len(argv)-2])
    output_bin = open(argv[len(argv)-2], 'w')
    print >> output_bin, wookey.as_binary()
    output_bin.close()
