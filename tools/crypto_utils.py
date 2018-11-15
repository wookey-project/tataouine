# Crypto related utils

import math
from Crypto.Cipher import AES
import hashlib, hmac

from common_utils import *

# Import our ECC python primitives
sys.path.append(os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + "../externals/libecc/scripts/")
from expand_libecc import *

# Get the curve and signature algorithm from a structured key
# [RB] FIXME: the algorithm and curve 'enum' values are hardcoded
# and supposed fixed in libecc. This is a bit tedious and error prone:
# we should ideally extract this information from the libecc headers.
def get_curve_from_key(structured_key_buffer):
    algo  = ord(structured_key_buffer[1])
    curve = ord(structured_key_buffer[2])
    prime = None
    a = None
    b = None
    gx = None
    gy = None
    order = None
    cofactor = None
    if algo == 1:
        # We only support ECDSA
        ret_alg = "ECDSA"
    else:
        ret_alg = None
    if curve == 1:
        ret_curve = "FRP256V1"
        prime = 0xF1FD178C0B3AD58F10126DE8CE42435B3961ADBCABC8CA6DE8FCF353D86E9C03
        a = 0xF1FD178C0B3AD58F10126DE8CE42435B3961ADBCABC8CA6DE8FCF353D86E9C00
        b = 0xEE353FCA5428A9300D4ABA754A44C00FDFEC0C9AE4B1A1803075ED967B7BB73F
        gx = 0xB6B3D4C356C139EB31183D4749D423958C27D2DCAF98B70164C97A2DD98F5CFF
        gy = 0x6142E0F7C8B204911F9271F0F3ECEF8C2701C307E8E4C9E183115A1554062CFB
        order = 0xF1FD178C0B3AD58F10126DE8CE42435B53DC67E140D2BF941FFDD459C6D655E1
        cofactor = 1
    elif curve == 8:
        ret_curve = "BRAINPOOLP256R1"
        prime = 76884956397045344220809746629001649093037950200943055203735601445031516197751
        a = 0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9
        b = 0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6
        gx = 0x8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262
        gy = 0x547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997
        order = 0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7
        cofactor = 1
    elif curve == 4:
        ret_curve = "SECP256R1"
        prime = 115792089210356248762697446949407573530086143415290314195533631308867097853951
        a = 115792089210356248762697446949407573530086143415290314195533631308867097853948
        b = 41058363725152142129326129780047268409114441015993725554835256314039467401291
        gx = 48439561293906451759052585252797914202762949526041747995844080717082404635286
        gy = 36134250956749795798585127919587881956611106672985015071877198253568414405109
        order = 115792089210356248762697446949407573529996955224135760342422259061068512044369
        cofactor = 1
    else:
        ret_curve = None
    return (ret_alg, ret_curve, prime, a, b, gx, gy, order, cofactor)
        
def get_sig_len(structured_key_buffer):
    # We only support 64 bytes (r, s) as the signature length for now ...
    # [RB] FIXME: use a more flexible way to compute this from the key
    return 64

# Python 2/3 abstraction layer for hash function
def local_sha256(arg_in):
    (a, b, c) = sha256(arg_in)
    return (a, b, c)

# Python 2/3 abstraction layer for HMAC
class local_hmac:
    hm = None
    def __init__(self, key, digestmod=hashlib.sha256):
        if is_python_2() == False: 
            key = key.encode('latin-1')
        self.hm = hmac.new(key, digestmod=digestmod)
        return
    def update(self, in_str):
        if is_python_2() == False: 
            in_str = in_str.encode('latin-1')
        if self.hm == None:
            return
        else:
            self.hm.update(in_str)
            return
    def digest(self):
        if self.hm == None:
            return None
        else:
            d = self.hm.digest()
            if is_python_2() == False:
                return d.decode('latin-1')
            else:
                return d
    @staticmethod
    def new(key, digestmod=hashlib.sha256):
        return local_hmac(key, digestmod=digestmod)

# Python 2/3 abstraction layer for AES
class local_AES:
    aes = None
    iv = None
    def  __init__(self, key, mode, iv=None, counter=None):
        if is_python_2() == False: 
            key = key.encode('latin-1')
        if iv != None:
            self.iv = iv
            if is_python_2() == False: 
                iv = iv.encode('latin-1')
            if mode == AES.MODE_CTR:
                if counter == None:
                    self.aes = AES.new(key, mode, counter=self.counter_inc)
                else:
                    self.aes = AES.new(key, mode, counter=counter)
            else:
                self.aes = AES.new(key, mode, iv)
            return
        else:
            if mode == AES.MODE_CTR:
                if counter == None:
                    self.iv = expand(inttostring(0), 128, "LEFT")
                    self.aes = AES.new(key, mode, counter=self.counter_inc)
                else:
                    self.aes = AES.new(key, mode, counter=counter)
            else:
                self.aes = AES.new(key, mode)
            return
    def counter_inc(self):
        curr_iv = expand(inttostring((stringtoint(self.iv))), 128, "LEFT")
        self.iv = expand(inttostring((stringtoint(self.iv)+1)), 128, "LEFT")
        if is_python_2() == False:
            curr_iv = curr_iv.encode('latin-1')
        return curr_iv
    def encrypt(self, data):
        if is_python_2() == False:
            data = data.encode('latin-1')
        ret = self.aes.encrypt(data)
        if is_python_2() == False:
            ret = ret.decode('latin-1')
        return ret
    def decrypt(self, data):
        if is_python_2() == False:
            data = data.encode('latin-1')
        ret = self.aes.decrypt(data)
        if is_python_2() == False:
            ret = ret.decode('latin-1')
        return ret
    @staticmethod
    def new(key, mode, iv=None, counter=None):
        return local_AES(key, mode, iv=iv, counter=counter)

# Python 2/3 abstraction layer for PBKDF2
def local_pbkdf2_hmac(hash_func, pin, salt, pbkdf2_iterations):
    if is_python_2() == False:
        pin = pin.encode('latin-1')
        salt = salt.encode('latin-1')
    dk = hashlib.pbkdf2_hmac(hash_func, pin, salt, pbkdf2_iterations)
    if is_python_2() == False:
        return dk.decode('latin-1')
    else:
        return dk
