from common_utils import *
from crypto_utils import *

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
    pbkdf2_iterations = int(argv[9], 0)
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

    # The encryption and HMAC keys are from the local pet key file
    # We only take first 64 bytes (last bytes are the IV)
    dk = local_pet_key_data[:64]
    # The key we use is the SHA-256 of the two 32 bytes in two halves (for one-wayness)
    (dk1, _, _) = local_sha256(dk[:32])
    (dk2, _, _) = local_sha256(dk[32:])
    dk = dk1 + dk2
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
    # [RB] NOTE: we use the platform data hash (SHA-256) as the HMAC Key because of possible SCA attacks
    # on HMAC (see https://www.cryptoexperts.com/sbelaid/articleHMAC.pdf). Although this
    # usage seems a bit counter-intuitive, this prevents extracting the encrypted data
    # through side-channels (consumption, EM, etc.).
    platform_data_to_hash = initial_iv+salt_data+token_pub_key_data+platform_priv_key_data+platform_pub_key_data
    if (applet_type == "dfu") or (applet_type == "sig"):
        platform_data_to_hash += firmware_sig_pub_key_data
    if (applet_type == "sig") and (len(argv) == 14):
        platform_data_to_hash += firmware_sig_priv_key_data+firmware_sig_sym_key_data
    (hmac_key, _, _) = local_sha256(platform_data_to_hash)
    # The integrity tag covers the salt, the iv and the encrypted data
    hm = local_hmac.new(hmac_key, digestmod=hashlib.sha256)
    hm.update(dk[32:])
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

    ###############
    # Case where we use the Backup SRAM as a keybag placeholder
    ###############
    if applet_type == "auth":
        bkup_sram_cfg = "CONFIG_APP_SMART_USE_BKUP_SRAM"
    elif applet_type == "dfu":
        bkup_sram_cfg = "CONFIG_APP_DFUSMART_USE_BKUP_SRAM"
    else:
        bkup_sram_cfg = "SIG_USE_BKUP_SRAM"

    text += "/* Handle backup SRAM usage for the keybag content */\n"
    text += "#ifdef "+bkup_sram_cfg+"\n"
    text += "  #define KEYBAG_SECTION "+"__attribute__((section(\".noupgrade."+applet_type+")))\n"
    text += "#else\n"
    text += "  #define KEYBAG_SECTION\n"
    text += "#endif /* "+bkup_sram_cfg+" */\n\n\n"
    
    ###############
    # Handle the keybags
    ###############
    # IV
    text += "KEYBAG_SECTION const unsigned char platform_iv_"+applet_type+"[]    = { "
    for byte in initial_iv:
        text += "0x%02x, " % stringtoint(byte)
    # Salt
    text += " };\n\nKEYBAG_SECTION const unsigned char platform_salt_"+applet_type+"[]  = { "
    for byte in salt_data:
        text += "0x%02x, " % stringtoint(byte)
    # HMAC tag
    text += " };\n\nKEYBAG_SECTION const unsigned char platform_hmac_tag_"+applet_type+"[]  = { "
    for byte in hmac_tag:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted token_pub_key_data
    text += " };\n\nKEYBAG_SECTION const unsigned char token_pub_key_data_"+applet_type+"[]  = { "
    for byte in token_pub_key_data:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted platform_priv_key_data
    text += " };\n\nKEYBAG_SECTION const unsigned char platform_priv_key_data_"+applet_type+"[]  = { "
    for byte in platform_priv_key_data:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted platform_pub_key_data
    text += " };\n\nKEYBAG_SECTION const unsigned char platform_pub_key_data_"+applet_type+"[]  = { "
    for byte in platform_pub_key_data:
        text += "0x%02x, " % stringtoint(byte)
    # Encrypted firmware signature_pub_key_data only for DFU and SIG bag
    if (applet_type == "dfu") or (applet_type == "sig"):
        text += " };\n\nKEYBAG_SECTION const unsigned char firmware_sig_pub_key_data_"+applet_type+"[]  = { "
        for byte in firmware_sig_pub_key_data:
            text += "0x%02x, " % stringtoint(byte)
    # Encrypted firmware private signature key and symmetric key only for SIG bag when explicitly asked for
    if (applet_type == "sig") and (len(argv) == 14):
        text += " };\n\nKEYBAG_SECTION const unsigned char firmware_sig_priv_key_data_"+applet_type+"[]  = { "
        for byte in firmware_sig_priv_key_data:
            text += "0x%02x, " % stringtoint(byte)
        #
        text += " };\n\nKEYBAG_SECTION const unsigned char firmware_sig_sym_key_data_"+applet_type+"[]  = { "
        for byte in firmware_sig_sym_key_data:
            text += "0x%02x, " % stringtoint(byte)
        #
        text += " };\n\nKEYBAG_SECTION const unsigned char encrypted_local_pet_key_data_"+applet_type+"[]  = { "
        for byte in encrypted_local_pet_key_data:
            text += "0x%02x, " % stringtoint(byte)

    text += "};\n\n\n"

    # Now create the keybag structure
    text += "databag keybag_"+applet_type+"[] = {\n"
    name = "platform_iv_"+applet_type
    text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    name = "platform_salt_"+applet_type
    text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    name = "platform_hmac_tag_"+applet_type
    text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    name = "token_pub_key_data_"+applet_type
    text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    name = "platform_priv_key_data_"+applet_type
    text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    name = "platform_pub_key_data_"+applet_type
    text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    if (applet_type == "dfu") or (applet_type == "sig"):
        name = "firmware_sig_pub_key_data_"+applet_type
        text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    if (applet_type == "sig") and (len(argv) == 14):
        name = "firmware_sig_priv_key_data_"+applet_type
        text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
        name = "firmware_sig_sym_key_data_"+applet_type
        text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
        name = "encrypted_local_pet_key_data_"+applet_type
        text += "    { .data = (unsigned char*)"+name+", .size = sizeof("+name+") },\n"
    text += "};\n"

    # Save in header file
    save_in_file(text, outfile_base+'.h')

    # Save in bin file
    encrypted_data_bin = initial_iv + salt_data + hmac_tag+token_pub_key_data + platform_priv_key_data + platform_pub_key_data
    if (applet_type == "dfu") or (applet_type == "sig"):
        encrypted_data_bin += firmware_sig_pub_key_data
    if (applet_type == "sig") and (len(argv) == 14):
        encrypted_data_bin += (firmware_sig_priv_key_data + firmware_sig_sym_key_data + encrypted_local_pet_key_data)
    save_in_file(encrypted_data_bin, outfile_base+'.bin')
    return 0


if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    if len(sys.argv) < 9:
        PrintUsage()
        sys.exit(1)
    encrypt_platform_data(sys.argv)
