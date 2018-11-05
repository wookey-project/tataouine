#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, array
import hashlib, hmac
import binascii
from Crypto.Cipher import AES

from utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print(u'\nencrypt_platform_data\n\n\tUsage:\t{} shared_petpin.bin platform_public_key.bin platform_private_key.bin token_public_key.bin local_pet_key.bin salt.bin outfile_base curve_name pbkdf2_iterations applet_type <firmware_sig_pub_key> <firmware_sig_priv_key> <firmware_sig_sym_key>\n'.format(executable))
    sys.exit(-1)

def encrypt_platform_data(argv):
    if not os.path.isfile(argv[1]):
        print(u'\nFile "{}" does not exist'.format(argv[1]))
        PrintUsage()
    if not os.path.isfile(argv[2]):
        print(u'\nFile "{}" does not exist'.format(argv[2]))
        PrintUsage()
    if not os.path.isfile(argv[3]):
        print(u'\nFile "{}" does not exist'.format(argv[3]))
        PrintUsage()
    if not os.path.isfile(argv[4]):
        print(u'\nFile "{}" does not exist'.format(argv[4]))
        PrintUsage()
    if not os.path.isfile(argv[5]):
        print(u'\nFile "{}" does not exist'.format(argv[5]))
        PrintUsage()
    if not os.path.isfile(argv[6]):
        print(u'\nFile "{}" does not exist'.format(argv[6]))
        PrintUsage()

    shared_petpin     = argv[1]
    platform_pub_key  = argv[2]
    platform_priv_key = argv[3]
    token_pub_key     = argv[4]
    local_pet_key     = argv[5]
    salt              = argv[6]
    firmware_sig_pub_key = None
    outfile_base      = argv[7]
    curve_name        = argv[8]
    pbkdf2_iterations = int(argv[9])
    applet_type       = argv[10]
    firmware_sig_priv_key  = None
    firmware_sig_sym_key   = None
    if (applet_type != "auth") and (applet_type != "dfu") and (applet_type != "sig"):
        print("Error: applet type must be auth, dfu, sig! %s has been provided ..." % (applet_type))
        sys.exit(-1)
    if (applet_type == "dfu") or (applet_type == "sig"):
        firmware_sig_pub_key = argv[11]
    if (applet_type == "sig") and (len(argv) == 14):
        # We are asked to locally store the firmware signature secrets: the user does not want
        # to use an external smartcard for this
        firmware_sig_priv_key = argv[12]
        firmware_sig_sym_key = argv[13]
            
    token_pub_key_data = read_in_file(token_pub_key)
    local_pet_key_data = read_in_file(local_pet_key)
    salt_data = read_in_file(salt)
    platform_pub_key_data = read_in_file(platform_pub_key)
    platform_priv_key_data = read_in_file(platform_priv_key)
    shared_petpin_data = read_in_file(shared_petpin)
    firmware_sig_pub_key_data = None
    if (applet_type == "dfu") or (applet_type == "sig"):
        firmware_sig_pub_key_data = read_in_file(firmware_sig_pub_key)
    firmware_sig_priv_key_data = None
    firmware_sig_sym_key_data = None
    if (applet_type == "sig") and (len(argv) == 14):
        # We are asked to locally store the firmware signature secrets: the user does not want
        # to use an external smartcard for this
        firmware_sig_priv_key_data = read_in_file(firmware_sig_priv_key)
        firmware_sig_sym_key_data = read_in_file(firmware_sig_sym_key)
 
    outfile = open(outfile_base+'.h', 'w')
    outfile_bin = open(outfile_base+'.bin', 'w')

    # The encryption and HMAC keys are from the local pet key file
    dk = local_pet_key_data 
    # Encrypt all our data with AES-128-CTR using the first 128 bits
    encrypt_platform_data.iv = gen_rand_string(16)
    initial_iv = encrypt_platform_data.iv
    # [RB] FIXME: move to AES-256 when the ANSSI masked AES implementation supports it
    enc_key = dk[:16]
    counter_inc = initial_iv
    cipher = local_AES.new(enc_key, AES.MODE_CTR, iv=counter_inc)
    token_pub_key_data = cipher.encrypt(token_pub_key_data)
    platform_priv_key_data = cipher.encrypt(platform_priv_key_data) 
    platform_pub_key_data = cipher.encrypt(platform_pub_key_data)
    if (applet_type == "dfu") or (applet_type == "sig"):
        firmware_sig_pub_key_data = cipher.encrypt(firmware_sig_pub_key_data)
    if (applet_type == "sig") and (len(argv) == 14):
        # We are asked to locally store the firmware signature secrets: the user does not want
        # to use an external smartcard for this
        firmware_sig_priv_key_data = cipher.encrypt(firmware_sig_priv_key_data)
        firmware_sig_sym_key_data = cipher.encrypt(firmware_sig_sym_key_data)
        # We also compute the encrypted local pet key to save it
        encrypted_local_pet_key_data = enc_local_pet_key(shared_petpin_data, salt_data, pbkdf2_iterations, local_pet_key_data)

    # Use HMAC-SHA256 with to compute the integrity tag
    hmac_key = dk[32:]
    # The integrity tag covers the salt, the iv and the encrypted data
    hm = local_hmac.new(hmac_key, digestmod=hashlib.sha256)
    hm.update(initial_iv+salt_data+token_pub_key_data+platform_priv_key_data+platform_pub_key_data)
    if (applet_type == "dfu") or (applet_type == "sig"):
        hm.update(firmware_sig_pub_key_data)
    if (applet_type == "sig") and (len(argv) == 14):
        hm.update(firmware_sig_priv_key_data+firmware_sig_sym_key_data)
    hmac_tag = hm.digest()
 
    # Curve name
    text  = "#ifndef USED_SIGNATURE_CURVE\n"
    text += "#define USED_SIGNATURE_CURVE "+curve_name+"\n"
    text += "#endif\n"
 
    # PBKDF2 iterations
    text += "#ifndef PLATFORM_PBKDF2_ITERATIONS\n"
    text += "#define PLATFORM_PBKDF2_ITERATIONS "+str(pbkdf2_iterations)+"\n"
    text += "#endif\n"
    text += "#define PLATFORM_IV_IDX_"+applet_type.upper()+" 0\n"
    text += "#define PLATFORM_SALT_IDX_"+applet_type.upper()+" 1\n"
    text += "#define PLATFORM_HMAC_TAG_IDX_"+applet_type.upper()+" 2\n"
    text += "#define TOKEN_PUB_KEY_IDX_"+applet_type.upper()+" 3\n"
    text += "#define PLATFORM_PRIV_KEY_IDX_"+applet_type.upper()+" 4\n"
    text += "#define PLATFORM_PUB_KEY_IDX_"+applet_type.upper()+" 5\n"
    if (applet_type == "dfu") or (applet_type == "sig"):
        text += "#define FIRMWARE_SIG_PUB_KEY_IDX_"+applet_type.upper()+" 6\n"
    if (applet_type == "sig") and (len(argv) == 14):
        text += "#define FIRMWARE_SIG_PRIV_KEY_IDX_"+applet_type.upper()+" 7\n"
        text += "#define FIRMWARE_SIG_SYM_KEY_IDX_"+applet_type.upper()+" 8\n"
        text += "#define ENCRYPTED_LOCAL_PET_KEY_IDX_"+applet_type.upper()+" 9\n"
    text += "\n\n"
    # IV
    text += "unsigned char platform_iv_"+applet_type+"[]    = { "
    for byte in initial_iv:
        text += "0x%02x, " % stringtoint(byte)
    # Salt
    text += " };\n\nunsigned char platform_salt_"+applet_type+"[]  = { "
    for byte in salt_data:
        text += "0x%02x, " % stringtoint(byte)
    # HMAC tag
    text += " };\n\nunsigned char platform_hmac_tag_"+applet_type+"[]  = { "
    for byte in hmac_tag:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted token_pub_key_data
    text += " };\n\nunsigned char token_pub_key_data_"+applet_type+"[]  = { "
    for byte in token_pub_key_data:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted platform_priv_key_data
    text += " };\n\nunsigned char platform_priv_key_data_"+applet_type+"[]  = { "
    for byte in platform_priv_key_data:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted platform_pub_key_data
    text += " };\n\nunsigned char platform_pub_key_data_"+applet_type+"[]  = { "
    for byte in platform_pub_key_data:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted firmware signature_pub_key_data only for DFU and SIG bag
    if (applet_type == "dfu") or (applet_type == "sig"):
        text += " };\n\nunsigned char firmware_sig_pub_key_data_"+applet_type+"[]  = { "
        for byte in firmware_sig_pub_key_data:
            text += "0x%02x, " % stringtoint(byte) 
    # Encrypted firmware private signature key and symmetric key only for SIG bag when explicitly asked for
    if (applet_type == "sig") and (len(argv) == 14):
        text += " };\n\nunsigned char firmware_sig_priv_key_data_"+applet_type+"[]  = { "
        for byte in firmware_sig_priv_key_data:
            text += "0x%02x, " % stringtoint(byte) 
        text += " };\n\nunsigned char firmware_sig_sym_key_data_"+applet_type+"[]  = { "
        for byte in firmware_sig_sym_key_data:
            text += "0x%02x, " % stringtoint(byte)
        text += " };\n\nunsigned char encrypted_local_pet_key_data_"+applet_type+"[]  = { "
        for byte in encrypted_local_pet_key_data:
            text += "0x%02x, " % stringtoint(byte)
      
    text += "};\n\n\n"

    # Now create the keybag structure
    text += "databag keybag_"+applet_type+"[] = {\n"

    name = "platform_iv_"+applet_type
    text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    name = "platform_salt_"+applet_type
    text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    name = "platform_hmac_tag_"+applet_type
    text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    name = "token_pub_key_data_"+applet_type
    text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    name = "platform_priv_key_data_"+applet_type
    text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    name = "platform_pub_key_data_"+applet_type
    text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    if (applet_type == "dfu") or (applet_type == "sig"):
        name = "firmware_sig_pub_key_data_"+applet_type
        text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    if (applet_type == "sig") and (len(argv) == 14):
        name = "firmware_sig_priv_key_data_"+applet_type
        text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
        name = "firmware_sig_sym_key_data_"+applet_type
        text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
        name = "encrypted_local_pet_key_data_"+applet_type
        text += "    { .data = "+name+", .size = sizeof("+name+") },\n"
    text += "};\n"

    outfile.write(text)
    outfile.close()

    outfile_bin.write(initial_iv+salt_data+hmac_tag+token_pub_key_data+platform_priv_key_data+platform_pub_key_data)
    if (applet_type == "dfu") or (applet_type == "sig"):
        outfile_bin.write(firmware_sig_pub_key_data)
    if (applet_type == "sig") and (len(argv) == 14):
        outfile_bin.write(firmware_sig_priv_key_data)
        outfile_bin.write(firmware_sig_sym_key_data)
        outfile_bin.write(encrypted_local_pet_key_data)
    outfile_bin.close()
    return 0


if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    if len(sys.argv) < 9:
        PrintUsage()
        sys.exit(1)
    encrypt_platform_data(sys.argv)
