import sys, os, array

# Import our local utils
from crypto_utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print(u'\nkey2java\n\n\tUsage:\t{} token_priv_key.bin token_pub_key.bin platform_pub_key.bin shared_petpin.bin  shared_petname.bin shared_userpin.bin master_secret_key.bin enc_local_pet_key.bin max_pin_tries max_secure_channel_tries sdcard_passwd.bin outfile applet_type profile\n'.format(executable))
    sys.exit(-1)

def Key2Java(argv):
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
    if not os.path.isfile(argv[7]):
        print(u'\nFile "{}" does not exist'.format(argv[7]))
        PrintUsage()
    if not os.path.isfile(argv[8]):
        print(u'\nFile "{}" does not exist'.format(argv[8]))
        PrintUsage()

    # Keys for the secure channel
    token_priv_key    = argv[1]
    token_pub_key     = argv[2]
    platform_pub_key  = argv[3]
    shared_petpin     = argv[4]
    shared_petname    = argv[5]
    shared_userpin    = argv[6]
    master_secret_key = argv[7]
    enc_local_pet_key = argv[8]
    max_pin_tries     = int(argv[9], 0)
    max_secure_channel_tries = int(argv[10], 0)
    sdcard_passwd     = argv[11]
    outfile           = argv[12]
    applet_type       = argv[13]
    # Platform profile
    profile           = argv[14]
    sig_priv_key = None
    sig_pub_key = None
    if applet_type == "sig":
        sig_priv_key = argv[15]
        sig_pub_key = argv[16]

    token_priv_key_data = read_in_file(token_priv_key)
    token_pub_key_data = read_in_file(token_pub_key)
    platform_pub_key_data = read_in_file(platform_pub_key)
    shared_petpin_data = read_in_file(shared_petpin)
    shared_petname_data = read_in_file(shared_petname)
    shared_userpin_data = read_in_file(shared_userpin)
    master_secret_key_data = read_in_file(master_secret_key)
    enc_local_pet_key_data = read_in_file(enc_local_pet_key)
    if applet_type == "sig":
        sig_priv_key_data = read_in_file(sig_priv_key)
        sig_pub_key_data = read_in_file(sig_pub_key)
    # SD card password, only useful for AUTH applet
    if applet_type == "auth":
        if not os.path.isfile(sdcard_passwd):
            print(u'\nFile "{}" does not exist'.format(sdcard_passwd))
            PrintUsage()
        sdcard_passwd_data   = read_in_file(sdcard_passwd)

    libeccparams = token_priv_key_data[1:3]
    token_priv_key_data    = token_priv_key_data[3:]
    token_pub_key_data     = token_pub_key_data[3:int((2*(len(token_pub_key_data)) / 3)+1)]
    platform_pub_key_data  = platform_pub_key_data[3:int((2*(len(platform_pub_key_data)) / 3)+1)]
    if applet_type == "sig":
        sig_priv_key_data = sig_priv_key_data[3:]
        sig_pub_key_data = sig_pub_key_data[3:int((2*(len(sig_pub_key_data)) / 3)+1)]

    text = "package wookey_"+applet_type+";\n\nclass Keys {\n\tstatic byte[] OurPrivKeyBuf    = { "
    for byte in token_priv_key_data:
        text += "(byte)0x%02x, " % ord(byte)
    # For public keys, add the '04' uncompressed point
    text += " };\n\n\tstatic byte[] OurPubKeyBuf     = { (byte)0x04, "
    for byte in token_pub_key_data:
        text += "(byte)0x%02x, " % ord(byte)
    text += " };\n\n\tstatic byte[] WooKeyPubKeyBuf   = { (byte)0x04, "
    for byte in platform_pub_key_data:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the curve and signing algorithm information
    text += " };\n\n\tstatic final byte[] LibECCparams  = { "
    for byte in libeccparams:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the PET PIN
    text += " };\n\n\tstatic byte[] PetPin  = { "
    for byte in shared_petpin_data:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the PET NAME
    orig_shared_petname_data_len = len(shared_petname_data)
    shared_petname_data = shared_petname_data + (64-orig_shared_petname_data_len)*'\x00'
    text += " };\n\n\tstatic short PetNameLength = "+str(orig_shared_petname_data_len)+";\n\n\tstatic byte[] PetName  = { "
    for byte in shared_petname_data:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the User PIN
    text += " };\n\n\tstatic byte[] UserPin  = { "
    for byte in shared_userpin_data:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the master secret key
    text += " };\n\n\tstatic byte[] MasterSecretKey  = { "
    for byte in master_secret_key_data:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the encrypted local pet key
    text += " };\n\n\tstatic byte[] EncLocalPetSecretKey  = { "
    for byte in enc_local_pet_key_data[:64]:
        text += "(byte)0x%02x, " % ord(byte)
    # Add the encrypted local pet key
    text += " };\n\n\tstatic byte[] EncLocalPetSecretKeyIV  = { "
    for byte in enc_local_pet_key_data[64:]:
        text += "(byte)0x%02x, " % ord(byte)
    if applet_type == "sig":
        # Add the signature public key
        text += " };\n\n\tstatic byte[] FirmwareSigPubKeyBuf     = { (byte)0x04, "
        for byte in sig_pub_key_data:
            text += "(byte)0x%02x, " % ord(byte)
        text += " };\n\n\tstatic byte[] FirmwareSigPrivKeyBuf = { "
        for byte in sig_priv_key_data:
            text += "(byte)0x%02x, " % ord(byte)
    if applet_type == "auth":
        text += " };\n\n\tstatic byte[] SDPassword  = { "
        for byte in sdcard_passwd_data:
            text += "(byte)0x%02x, " % ord(byte)
    #
    text += "};\n"

    # Add the maximum PIN tries
    text += "\n\n\tstatic final byte max_pin_tries = (byte)"+str(max_pin_tries)+";"
    # Add the maximum secure channel mounting tries tries
    text += "\n\n\tstatic final short max_secure_channel_tries = "+str(max_secure_channel_tries)+";"
    # Add the platform profile
    text += "\n\n\t /* Platform profiles is: \""+profile+"\"*/"
    text += "\n\tstatic final byte[] Profile =  { "
    for byte in profile:
            text += "(byte)0x%02x, " % ord(byte)
    text += "};\n"

    # In case of FIDO profile, we also save second half of the private key
    if applet_type == "auth" and profile == "u2f2":
        fido_privkey_file = os.path.dirname(os.path.abspath(sdcard_passwd))+"/FIDO/attestation_key.der.privkey.bin"
        if not os.path.isfile(fido_privkey_file):
            print(u'\nFile %s does not exist' % fido_privkey_file)
            sys.exit(-1)
        fido_privkey = read_in_file(fido_privkey_file)
        # Save the second half key n the applet
        text += "\n\tstatic final byte[] FidoHalfPrivKey =  { "
        for byte in fido_privkey[16:]:
            text += "(byte)0x%02x, " % ord(byte)
        text += "};\n"

    #
    text += "\n}"

    save_in_file(text, outfile)
    return 0


if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    if len(sys.argv) < 13:
        PrintUsage()
        sys.exit(1)
    Key2Java(sys.argv)
