#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Encrypt a firmware and sign it using interactions with
# the SIG token

# Import our local utils
from common_utils import *
from crypto_utils import *
from firmware_utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print("Error when executing %s\n\tUsage:\t%s keys_path firmware_to_sign firmware_magic firmware_partition_type firmware_version firmware_chunk_size usb_vid usb_pid" % (executable, executable))
    sys.exit(-1)

# DFU CRC32 function (for the DFU suffix)
dfu_crc32_table = [
    0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f,
    0xe963a535, 0x9e6495a3, 0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
    0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91, 0x1db71064, 0x6ab020f2,
    0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
    0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9,
    0xfa0f3d63, 0x8d080df5, 0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172,
    0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b, 0x35b5a8fa, 0x42b2986c,
    0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
    0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423,
    0xcfba9599, 0xb8bda50f, 0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924,
    0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d, 0x76dc4190, 0x01db7106,
    0x98d220bc, 0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
    0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d,
    0x91646c97, 0xe6635c01, 0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e,
    0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457, 0x65b0d9c6, 0x12b7e950,
    0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
    0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7,
    0xa4d1c46d, 0xd3d6f4fb, 0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0,
    0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9, 0x5005713c, 0x270241aa,
    0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
    0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81,
    0xb7bd5c3b, 0xc0ba6cad, 0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a,
    0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683, 0xe3630b12, 0x94643b84,
    0x0d6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
    0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb,
    0x196c3671, 0x6e6b06e7, 0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc,
    0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5, 0xd6d6a3e8, 0xa1d1937e,
    0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
    0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55,
    0x316e8eef, 0x4669be79, 0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236,
    0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f, 0xc5ba3bbe, 0xb2bd0b28,
    0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
    0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 0x9c0906a9, 0xeb0e363f,
    0x72076785, 0x05005713, 0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38,
    0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21, 0x86d3d2d4, 0xf1d4e242,
    0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
    0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69,
    0x616bffd3, 0x166ccf45, 0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2,
    0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db, 0xaed16a4a, 0xd9d65adc,
    0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
    0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693,
    0x54de5729, 0x23d967bf, 0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94,
    0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d ]

def dfu_crc32_update(buf, crc):
    for k in buf:
        crc = (crc >> 8) ^ dfu_crc32_table[(crc & 0xff) ^ ord(k)]
    return crc

if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    # Get the arguments
    if len(sys.argv) <= 7:
        PrintUsage()
    keys_path = sys.argv[1]
    firmware_to_sign_file = sys.argv[2]
    firmware_magic = int(sys.argv[3])
    firmware_partition_type = sys.argv[4]
    firmware_version = int(sys.argv[5])
    firmware_chunk_size = int(sys.argv[6])
    # Default values for the DFU suffix
    usb_vid = usb_pid = 0xffff
    if len(sys.argv) > 7:
        usb_vid = int(sys.argv[7], 16)
    if len(sys.argv) > 8:
        usb_pid = int(sys.argv[8], 16)
  
    if usb_vid > 0xffff:
        print("Error: provided USB Vendor ID %d is invalid (> 0xffff)" % (usb_vid))
        sys.exit(-1)
    if usb_pid > 0xffff:
        print("Error: provided USB Product ID %d is invalid (> 0xffff)" % (usb_pid))
        sys.exit(-1)  

    if not os.path.isfile(firmware_to_sign_file):
        print("Error: provided firmware file %s does not exist!" % (firmware_to_sign_file))
        sys.exit(-1)
    firmware_partition_type = partitions_types[firmware_partition_type]
    if (firmware_chunk_size < 0) or (firmware_version < 0) or (firmware_chunk_size < 0):
        print("Error: negative values are not allowed as arguments ...")
        sys.exit(-1)
    # Sanity checks
    if firmware_magic > (0x1 << 32):
        print("Error: provided firmware_magic %d exceeds maximum size of 4 bytes ..." % (firmware_magic))
        sys.exit(-1)
    if firmware_version > (0x1 << 32):
        print("Error: provided firmware_version %d exceeds maximum size of 4 bytes ..." % (firmware_version))
        sys.exit(-1) 
    # Check that we have a reasonable chunk size to be sure to call the token
    # a reasonable number of times
    if firmware_chunk_size > 65536:
        print("Error: provided firmware_chunk_size %d exceeds maximum allowed size of 65536 ..." % (firmware_chunk_size))
        sys.exit(-1)
    # Convert magic, version and chunk_size to strings in big endian
    firmware_magic = expand(inttostring(firmware_magic), 32, "LEFT")
    firmware_version = expand(inttostring(firmware_version), 32, "LEFT")
    firmware_chunk_size_str = expand(inttostring(firmware_chunk_size), 32, "LEFT")
    # Read the firmware file in a buffer
    firmware_to_sign = read_in_file(firmware_to_sign_file)
 
    # Current script path
    SCRIPT_PATH = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
    # Variable used when the SIG token is used
    card = None
    scp_sig = None
    # Variables used when the SIG token is NOT used and all the key
    # are locally encrypted
    dec_token_pub_key_data = None
    dec_platform_priv_key_data = None
    dec_platform_pub_key_data = None
    dec_firmware_sig_pub_key_data = None 
    dec_firmware_sig_priv_key_data = None
    dec_firmware_sig_sym_key_data = None

    # Check if we want to use an external token for the signature or not
    USE_SIG_TOKEN = is_sig_token_used(keys_path+"/SIG/encrypted_platform_sig_keys.bin")
 
    if USE_SIG_TOKEN == True:
        from token_utils import *
        card = connect_to_token("SIG")
        scp_sig = token_full_unlock(card, "sig", keys_path+"/SIG/encrypted_platform_sig_keys.bin") # pet_pin="1234", user_pin="1234", force_pet_name_accept = True)
    else:
        local_storage_password = get_user_input("Please provide the local storage password for SIG (firmware signature):\n")
        # Decrypt the local keys
        dec_token_pub_key_data, dec_platform_priv_key_data, dec_platform_pub_key_data, dec_firmware_sig_pub_key_data, dec_firmware_sig_priv_key_data, dec_firmware_sig_sym_key_data, _, _ = decrypt_platform_data(keys_path+"/SIG/encrypted_platform_sig_keys.bin", local_storage_password, "sig")

    # ======================
    # Structure of a signed image is:
    # Header + MAX_CHUNK_SIZE(4 bytes) + IV + HMAC(previous) + SIG + ENC(firmware)
    # The signature covers Header + MAX_CHUNK_SIZE + firmware

    # ======================
    # We forge the basic header = magic on 4 bytes || partition type on 4 bytes || version on 4 bytes || len of data after the header on 4 bytes || siglen on 4 bytes
    sigtype = None
    if USE_SIG_TOKEN == True:
        sigtype, sw1, sw2 = scp_sig.token_sig_get_sig_type()
        if (sw1 != 0x90) or (sw2 != 0x00):
            print("Error:  SIG token APDU error ...")
            sys.exit(-1)
    else:
        sigtype = expand(inttostring(get_sig_len(dec_firmware_sig_priv_key_data)), 32, "LEFT") + dec_firmware_sig_priv_key_data[:2]
    siglen = sigtype[:4]
    libeccparams = sigtype[-2:]
    # Sanity check on the ECDSA signature algorithm
    the_sig = stringtoint(libeccparams[0])
    if ((len(sigtype) != 6) or (the_sig != 0x01)):
        print("Error: signature type %d sent by the card is not conforming to ECDSA ..." % (the_sig))
        sys.exit(-1)

    data_len_encapsulated = expand(inttostring(len(firmware_to_sign)), 32, "LEFT")
    header = firmware_magic + expand(inttostring(firmware_partition_type), 32, "LEFT") + firmware_version + data_len_encapsulated + siglen

    # ======================
    # The signature on the header + chunk_size + the CLEAR text firmware
    # NOTE1: since we want to check the firmware once it is written on flash, we
    # have to sign its clear text form (and not the encrypted one).
    # NOTE2: because of ECDSA limitations of the current javacard API, we cannot
    # compute ECDSA on raw data since the card performs the hash function. Hence, we are
    # deemed to compute ECDSA with double SHA-256:
    # firmware_sig = ECDSA_SIG(SHA-256(header || firmware))
    (to_sign, _, _) = sha256(header + firmware_chunk_size_str + firmware_to_sign)
    sig = None
    if USE_SIG_TOKEN == True:
        sig, sw1, sw2  = scp_sig.token_sig_sign_firmware(to_sign)
        if (sw1 != 0x90) or (sw2 != 0x00):
            print("Error:  SIG token APDU error ...")
            sys.exit(-1)
        signed_data = to_sign + sig
        resp, sw1, sw2 = scp_sig.token_sig_verify_firmware(signed_data) 
        if (sw1 != 0x90) or (sw2 != 0x00):
            print("Error:  SIG token APDU error ...")
            sys.exit(-1)
    else:
        # Software ECDSA signature
        ret_alg, ret_curve, prime, a, b, gx, gy, order, cofactor = get_curve_from_key(dec_firmware_sig_pub_key_data)
        c = Curve(a, b, prime, order, cofactor, gx, gy, cofactor * order, ret_alg, None)
        ecdsa_privkey = PrivKey(c, stringtoint(dec_firmware_sig_priv_key_data[3:3+32]))
        ecdsa_keypair = KeyPair(None, ecdsa_privkey)
        (sig, _) = ecdsa_sign(sha256, ecdsa_keypair, to_sign)


    sig_session_iv = None
    # We first begin a signing session to get the iv and the header HMAC
    if USE_SIG_TOKEN == True:
        sig_session_iv, sw1, sw2 = scp_sig.token_sig_begin_sign_session(header + firmware_chunk_size_str + sig)
        if (sw1 != 0x90) or (sw2 != 0x00):
            print("Error:  SIG token APDU error ...")
            sys.exit(-1)
    else:
        # Generate random
        sig_session_iv = gen_rand_string(16)
        # Compute the HMAC, and concatenate them
        hm = local_hmac.new(dec_firmware_sig_sym_key_data, digestmod=hashlib.sha256)
        hm.update(header + firmware_chunk_size_str + sig_session_iv + sig)
        sig_session_iv += hm.digest()

    # ======================
    # The encryption of the firmware chunks of 
    # Each chunk is encrypted using AES-CTR and the current session key and an IV of zero
   
    # Split the firmware in chunks
    n_chunks = int(len(firmware_to_sign) // firmware_chunk_size)
    if len(firmware_to_sign) % firmware_chunk_size != 0:
        n_chunks += 1
    
    encrypted_firmware = ""
    
    if USE_SIG_TOKEN == True:
        # The SIG token will derive keys for us
        local_key_to_derive = None
    else:
        # We use software crypto to derive keys
        local_key_to_derive = sig_session_iv[:16]
    for i in range(0, n_chunks):
        print("\tXXXXXXXXXXXXXXXXX ENCRYPTING CHUNK %04x XXXXXXXXXXXXXXXXX" % (i))
        chunk_key = None
        if USE_SIG_TOKEN == True:
            chunk_key, sw1, sw2 = scp_sig.token_sig_derive_key()
            if (sw1 != 0x90) or (sw2 != 0x00):
                print("Error:  SIG token APDU error ...")
                sys.exit(-1)
        else:
            aes_cbc_ctx = local_AES.new(dec_firmware_sig_sym_key_data[:16], AES.MODE_CBC, iv=dec_firmware_sig_sym_key_data[16:])
            chunk_key = aes_cbc_ctx.encrypt(local_key_to_derive)
 
            # Increment the session iv
            local_key_to_derive = expand(inttostring((stringtoint(local_key_to_derive)+1)), 128, "LEFT")
        # Initialize AES-CTR IV to 0
        chunk_iv = inttostring(0)
        if i != n_chunks-1:
            chunk = firmware_to_sign[(i*firmware_chunk_size) : ((i+1)*firmware_chunk_size)]
        else:
            chunk = firmware_to_sign[(i*firmware_chunk_size):]
        aes = local_AES.new(chunk_key, AES.MODE_CTR, iv=chunk_iv)
        encrypted_firmware += aes.encrypt(chunk)
        print("\tXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    # Compute the DFU suffix on 16 bytes
    dfu_suffix = inttostring(0xffff) + expand(inttostring(usb_pid), 16, "LEFT")[::-1] + expand(inttostring(usb_vid), 16, "LEFT")[::-1] + "\x00\x01\x55\x46\x44\x10"
    to_save = header + firmware_chunk_size_str + sig_session_iv + sig + encrypted_firmware + dfu_suffix
    dfu_suffix_crc32 = expand(inttostring(dfu_crc32_update(to_save, 0xffffffff)), 32, "LEFT")[::-1]
    # Save the header and signed/encrypted firmware in a file
    save_in_file(to_save + dfu_suffix_crc32, firmware_to_sign_file+".signed")
