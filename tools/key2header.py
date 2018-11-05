#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, array

def PrintUsage():
    executable = os.path.basename(__file__)
    print u'\nkey2header\n\n\tUsage:\t{} directory prefix\n'.format(executable)
    sys.exit(1)

def Key2Header(argv):
    prefix = argv[2]
    binfile = argv[1]+'/'+prefix+'.bin'
    outfile = argv[1]+'/'+prefix+'.h'

    if not os.path.isfile(binfile):
        print u'\nFile "{}" does not exist'.format(binfile)
        PrintUsage()

    data = array.array('B', open(binfile, 'rb').read())
    outfile = open(outfile, 'w')

    text = "const unsigned char "+prefix+"[] = {"

    current = 0
    data_length = len(data)
    for byte in data:
        text += '0x%02x' % byte
        if (current + 1) < data_length:
            text += ', '
        current += 1

    text += '};\n'
    outfile.write(text)
    outfile.close()
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        PrintUsage()
        sys.exit(1)

    Key2Header(sys.argv)
