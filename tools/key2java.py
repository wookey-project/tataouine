#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, array

def PrintUsage():
    executable = os.path.basename(__file__)
    print u'\nkey2java\n\n\tUsage:\t{} token_priv_key.bin token_pub_key.bin platform_pub_key.bin outfile\n'.format(executable)
    sys.exit(1)

def Key2Java(argv):
    if not os.path.isfile(argv[1]):
        print u'\nFile "{}" does not exist'.format(argv[1])
        PrintUsage()
    if not os.path.isfile(argv[2]):
        print u'\nFile "{}" does not exist'.format(argv[2])
        PrintUsage()
    if not os.path.isfile(argv[3]):
        print u'\nFile "{}" does not exist'.format(argv[3])
        PrintUsage()

    token_priv_key   = argv[1]
    token_pub_key    = argv[2]
    platform_pub_key = argv[3]
    outfile = argv[4]


    token_priv_key_data = array.array('B', open(token_priv_key, 'rb').read())
    token_pub_key_data = array.array('B', open(token_pub_key, 'rb').read())
    platform_pub_key_data = array.array('B', open(platform_pub_key, 'rb').read())
    outfile = open(outfile, 'w')
    
    token_priv_key_data    = token_priv_key_data[3:]
    token_pub_key_data     = token_pub_key_data[3:(2*(len(token_pub_key_data)) / 3)+1]
    platform_pub_key_data  = platform_pub_key_data[3:(2*(len(platform_pub_key_data)) / 3)+1]

    text = "package goodusb;\n\npublic class Keys {\n\tbyte[] OurPrivKeyBuf    = { "
    for byte in token_priv_key_data:
        text += "(byte)0x%02x, " % byte
    # For public keys, add the '04' uncompressed point 
    text += " };\n\n\tbyte[] OurPubKeyBuf     = { (byte)0x04, "
    for byte in token_pub_key_data:
        text += "(byte)0x%02x, " % byte
    text += " };\n\n\tbyte[] GoodUSBPubKeyBuf   = { (byte)0x04, "
    for byte in platform_pub_key_data:
        text += "(byte)0x%02x, " % byte
    text += "};\n\n}"

    outfile.write(text)
    outfile.close()
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 5:
        PrintUsage()
        sys.exit(1)

    Key2Java(sys.argv)
