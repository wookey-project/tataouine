#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Decrypt a firmware and check its signature using
# the DFU token

# Import our local utils
from common_utils import *
from crypto_utils import *
from firmware_utils import *
from token_utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print("Error when executing %s\n\tUsage:\t%s keys_path firmware_to_decrypt <only_info>" % (executable, executable))
    sys.exit(-1)

if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    # Get the arguments
    if len(sys.argv) < 3:
        PrintUsage()
    if len(sys.argv) > 4:
        PrintUsage()
    keys_path = sys.argv[1]
    firmware_to_decrypt_file = sys.argv[2]
    if not os.path.isfile(firmware_to_decrypt_file):
        print("Error: provided firmware file %s does not exist!" % (firmware_to_decrypt_file))
        sys.exit(-1)
    # Read the buffer from the file
    firmware_to_decrypt = read_in_file(firmware_to_decrypt_file)
    # Remove the DFU suffix if present
    if len(firmware_to_decrypt) >= 16:
        if firmware_to_decrypt[-8:-5] == "UFD" and firmware_to_decrypt[-4:] == expand(inttostring(dfu_crc32_update(firmware_to_decrypt[:-4], 0xffffffff)), 32, "LEFT")[::-1]:
            firmware_to_decrypt = firmware_to_decrypt[:-16]

    # Check if we only want to print the information
    ONLY_INFO = False
    if len(sys.argv) == 4:
        ONLY_INFO = True
    # Parse the header
    # Header = magic on 4 bytes || partition type on 4 bytes || version on 4 bytes || len of data after the header on 4 bytes || siglen on 4 bytes
    header = firmware_to_decrypt[:firmware_header_layout['CHUNKSIZE_OFFSET']]
    magic =  header[firmware_header_layout['MAGIC_OFFSET'] : firmware_header_layout['MAGIC_OFFSET'] + firmware_header_layout['MAGIC_SIZE']]
    partition_type =  header[firmware_header_layout['TYPE_OFFSET'] : firmware_header_layout['TYPE_OFFSET'] + firmware_header_layout['TYPE_SIZE']]
    version = header[firmware_header_layout['VERSION_OFFSET'] : firmware_header_layout['VERSION_OFFSET'] + firmware_header_layout['VERSION_SIZE']]
    data_len = header[firmware_header_layout['LEN_OFFSET'] : firmware_header_layout['LEN_OFFSET'] + firmware_header_layout['LEN_SIZE']]
    siglen = header[firmware_header_layout['SIGLEN_OFFSET'] : firmware_header_layout['SIGLEN_OFFSET'] + firmware_header_layout['SIGLEN_SIZE']]

    def inverse_mapping(f):
        return f.__class__(map(reversed, f.items()))

    print("Magic         : 0x" + local_hexlify(magic))
    print("Partition type: '"  + inverse_mapping(partitions_types)[stringtoint(partition_type)]+"'")
    print("Version       : 0x" + local_hexlify(version))
    print("Data length   : 0x" + local_hexlify(data_len))
    print("Sig length    : 0x" + local_hexlify(siglen))

    # Now extract the signature and parse the content
    data_len = stringtoint(data_len)
    siglen = stringtoint(siglen)
    firmware_chunk_size_str = firmware_to_decrypt[firmware_header_layout['CHUNKSIZE_OFFSET'] : firmware_header_layout['CHUNKSIZE_OFFSET'] + firmware_header_layout['CHUNKSIZE_SIZE']]
    firmware_chunk_size = stringtoint(firmware_chunk_size_str)
    # Extract the chunk size, the IV and the HMAC
    iv = firmware_to_decrypt[firmware_header_layout['IV_OFFSET'] : firmware_header_layout['IV_OFFSET'] + firmware_header_layout['IV_SIZE']:]
    hmac = firmware_to_decrypt[firmware_header_layout['HMAC_OFFSET'] : firmware_header_layout['HMAC_OFFSET'] + firmware_header_layout['HMAC_SIZE']]
    # Extract the signature
    signature = firmware_to_decrypt[firmware_header_layout['SIG_OFFSET'] : firmware_header_layout['SIG_OFFSET'] + siglen]
    # Extract the remaining data
    encrypted_content = encapsulated_content = firmware_to_decrypt[firmware_header_layout['SIG_OFFSET'] + siglen:]

    if len(encapsulated_content) != data_len:
        print("Error: encapsulated firmware length %d does not match the one in the header %d!" % (len(encapsulated_content), data_len))
        sys.exit(-1)
    # Now extract the signature information from the public key
    SCRIPT_PATH = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
    firmware_sig_pub_key_data = read_in_file(keys_path+"/SIG/token_sig_firmware_public_key.bin") 
    ret_alg, ret_curve, prime, a, b, gx, gy, order, cofactor = get_curve_from_key(firmware_sig_pub_key_data)
    # Sanity check: the algorithm should be ECDSA 
    if ret_alg != "ECDSA":
        print("Error: asked signature algorithm is not supported (not ECDSA)")
        sys.exit(-1)

    print("IV            : 0x" + local_hexlify(iv))
    print("HMAC          : 0x" + local_hexlify(hmac))
    print("Chunk size    : %d" % (firmware_chunk_size))
    print("Signature     : 0x" + local_hexlify(signature))
    
    # If we only wanted information, we can quit here
    if ONLY_INFO == True:
        sys.exit(0)

    # Ask the DFU token to begin a session
    card = connect_to_token("DFU")
    scp_dfu = token_full_unlock(card, "dfu", keys_path+"/DFU/encrypted_platform_dfu_keys.bin") # pet_pin="1234", user_pin="1234", force_pet_name_accept = True)
    resp, sw1, sw2 = scp_dfu.token_dfu_begin_decrypt_session(header + firmware_chunk_size_str + iv + hmac + signature)
    if (sw1 != 0x90) or (sw2 != 0x00):
        print("Error:  DFU token APDU error ...")
        sys.exit(-1)

    # Now decrypt the firmware
    # Split the firmware in chunks
    n_chunks = int(len(encrypted_content) // firmware_chunk_size)
    if len(encrypted_content) % firmware_chunk_size != 0:
        n_chunks += 1

    decrypted_firmware = ""
    for i in range(0, n_chunks):
        print("\tXXXXXXXXXXXXXXXXX DECRYPTING CHUNK %04x XXXXXXXXXXXXXXXXX" % (i))
        chunk_key, sw1, sw2 = scp_dfu.token_dfu_derive_key()
        if (sw1 != 0x90) or (sw2 != 0x00):
            print("Error:  DFU token APDU error ...")
            sys.exit(-1)

        # Initialize IV to 0
        chunk_iv = inttostring(0)
        if i != n_chunks-1:
            chunk = encrypted_content[(i*firmware_chunk_size) : ((i+1)*firmware_chunk_size)]
        else:
            chunk = encrypted_content[(i*firmware_chunk_size):]
        aes = local_AES.new(chunk_key, AES.MODE_CTR, iv=chunk_iv)
        decrypted_firmware += aes.decrypt(chunk)
        print("\tXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    # Now check the signature on the decrypted firmware with the header
    # NOTE1: since we want to check the firmware once it is written on flash, we
    # have to verify its clear text form (and not the encrypted one).
    (to_verify, _, _) = sha256(header + firmware_chunk_size_str + decrypted_firmware)

    # Verify ECDSA_VERIF(SHA-256(to_verify))
    c = Curve(a, b, prime, order, cofactor, gx, gy, cofactor * order, ret_alg, None)
    ecdsa_pubkey = PubKey(c, Point(c, stringtoint(firmware_sig_pub_key_data[3:3+32]), stringtoint(firmware_sig_pub_key_data[3+32:3+64])))
    ecdsa_keypair = KeyPair(ecdsa_pubkey, None)
    if ecdsa_verify(sha256, ecdsa_keypair, to_verify, signature) == False:
        print(("\033[1;41m "+"[Error: bad signature for %s]"+"\033[1;m") % (firmware_to_decrypt_file))
        sys.exit(-1) 
    else: 
        print(("\033[1;42m"+"[Signature for %s is OK!]  "+"\033[1;m") % (firmware_to_decrypt_file))

    # Save the file
    save_in_file(decrypted_firmware, firmware_to_decrypt_file+".decrypted")
