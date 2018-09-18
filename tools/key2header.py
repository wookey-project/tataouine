#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, array

def PrintUsage():
    executable = os.path.basename(__file__)
    print u'\nkey2header\n\n\tUsage:\t{} infile outfile\n'.format(executable)
    sys.exit(1)

def Key2Header(argv):
    if not os.path.isfile(argv[1]):
        print u'\nFile "{}" does not exist'.format(argv[1])
        PrintUsage()

    path = argv[1]
    outfile = argv[2]

    hname_upper = os.path.basename(outfile).replace(".","_").upper()

    data = array.array('B', open(path, 'rb').read())
    outfile = open(outfile, 'w')

    text = "#ifndef {}\n\t#define {}\n\n".format(hname_upper,hname_upper)
    text +="\t#define DFU_SIGLEN {}\n\n".format(len(data))
    text +="\t#define DFU_SIG { \\\n"

    current = 0
    data_length = len(data)
    for byte in data:
        if (current % 12) == 0:
            text += '\t\t'
        text += '0x%02x' % byte

        if (current + 1) < data_length:
            text += ', '
        if (current % 12) == 11:
            text += '\\\n'

        current += 1

    text += ' \\\n\t}\n\n#endif\n'
    outfile.write(text)
    outfile.close()
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        PrintUsage()
        sys.exit(1)

    Key2Header(sys.argv)
