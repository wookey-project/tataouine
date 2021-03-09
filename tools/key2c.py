import sys, os, array

# Import our local utils
from crypto_utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print(u'\nkey2c\n\n\tUsage:\t{} certificate.der keys.der\n'.format(executable))
    sys.exit(-1)

def Key2C(argv):
    if not os.path.isfile(argv[1]):
        print(u'\nFile "{}" does not exist'.format(argv[1]))
        PrintUsage()
    if not os.path.isfile(argv[2]):
        print(u'\nFile "{}" does not exist'.format(argv[2]))
        PrintUsage()

    # Certificate der
    cert  = read_in_file(argv[1])

    text = "static const unsigned char fido_attestation_cert["+str(len(cert))+"] = { \n\t"
    line = 1
    for byte in cert:
        text += "0x%02x, " % ord(byte)
        if line % 8 == 0:
            text += "\n\t"
        line += 1
    text += "\n};"
    save_in_file(text, argv[1]+".h")

    # Public and private key der
    keysder  = read_in_file(argv[2])
    # We have to extract the private and public keys
    # We have a SEQUENCE of OCTET STRING, OID, BITSTRING
    (check, size_seq, seq) = extract_DER_sequence(keysder)
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    # Get integer
    (check, size_ver, ver) = extract_DER_integer(seq)
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    # Get encapsulated OCTET string
    (check, privkey_size, privkey) = extract_DER_octetstring(seq[size_ver:])
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    # Get OID (encapsulated [0])
    (check, oidenc_size, oidenc) = extract_DER_object(seq[size_ver+privkey_size:], 0xa0)
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    (check, oid_size, oid) = extract_DER_oid(oidenc)
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    # Check OID
    # Does the OID correspond to a prime field?
    if(oid != "\x2A\x86\x48\xCE\x3D\x03\x01\x07"):
        print("Error when parsing ASN.1 %s: OID does not correspond to prime256v1" % argv[2])
        sys.exit(-1)
 
    # Extract pubkey
    # Encapsulated [1]
    (check, pubkeyenc_size, pubkeyenc) = extract_DER_object(seq[size_ver+privkey_size+oidenc_size:], 0xa1)
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    # BITSTRING
    (check, pubkey_size, pubkey) = extract_DER_bitstring(pubkeyenc)
    if check == False:
        print("Error when parsing ASN.1 %s" % argv[2])
        sys.exit(-1)
    # Extract the point
    # Check unused bits = 0 and uncompressed point
    if (pubkey[0] != '\x00') or (pubkey[1] != '\x04'):
        print("Error when parsing ASN.1 %s: expected uncompressed point, got other thing" % argv[2])
        sys.exit(-1)
    # Encapsulated coordinates
    pubkey = pubkey[1:]
    # Sanity check on the size
    if len(pubkey) != 65:
        print("Error when parsing ASN.1 %s: bad pubkey length" % argv[2])
        sys.exit(-1)
    # Sanity check on the curve
    X = stringtoint(pubkey[1:][:32])
    Y = stringtoint(pubkey[1:][32:])
    SECP256R1 = Curve(115792089210356248762697446949407573530086143415290314195533631308867097853948, 41058363725152142129326129780047268409114441015993725554835256314039467401291, 115792089210356248762697446949407573530086143415290314195533631308867097853951, 115792089210356248762697446949407573529996955224135760342422259061068512044369, 1, 48439561293906451759052585252797914202762949526041747995844080717082404635286, 36134250956749795798585127919587881956611106672985015071877198253568414405109, 115792089210356248762697446949407573529996955224135760342422259061068512044369, "SECP256R1", None)
    # Check public key
    G = Point(SECP256R1, SECP256R1.gx, SECP256R1.gy)
    P = Point(SECP256R1, X, Y)    
    P_frompriv = stringtoint(privkey) * G
    if P != P_frompriv:
        print("Error when parsing ASN.1: private and public keys do not correspond!" % argv[2])
        sys.exit(-1)
    # Everything is OK: save our data
    text = "static const unsigned char fido_attestation_privkey["+str(len(privkey))+"] = { \n\t"
    line = 1
    for byte in privkey:
        text += "0x%02x, " % ord(byte)
        if line % 8 == 0:
            text += "\n\t"
        line += 1
    text += "\n};"
    text += "\n\nstatic const unsigned char fido_attestation_pubkey["+str(len(pubkey))+"] = { \n\t"
    line = 1
    for byte in pubkey:
        text += "0x%02x, " % ord(byte)
        if line % 8 == 0:
            text += "\n\t"
        line += 1
    text += "\n};"
    # Save in file
    save_in_file(text, argv[2]+".h")

    return 0

if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    if len(sys.argv) < 3:
        PrintUsage()
        sys.exit(1)
    Key2C(sys.argv)
