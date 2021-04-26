# Import our local utils
import sys, os, inspect
FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
SCRIPT_PATH = os.path.dirname(os.path.abspath(FILENAME)) + "/"
sys.path.append(SCRIPT_PATH+'../')
sys.path.append(SCRIPT_PATH+'images/')

from common_utils import *
from crypto_utils import *
from firmware_utils import *
from token_utils import *
from copy import deepcopy

from ctypes import *
from struct import *
from rle_utils import *

class StructHelper(object):
    def __get_value_str(self, name, fmt='{}'):
        val = getattr(self, name)
        if isinstance(val, Array):
            val = list(val)
        return fmt.format(val)

    def __str__(self):
        result = '{}:\n'.format(self.__class__.__name__)
        maxname = max(len(name) for name, type_ in self._fields_)
        for name, type_ in self._fields_:
            value = getattr(self, name)
            result += ' {name:<{width}}: {value}\n'.format(
                    name = name,
                    width = maxname,
                    value = self.__get_value_str(name),
                    )
        return result

    def __repr__(self):
        return '{name}({fields})'.format(
                name = self.__class__.__name__,
                fields = ', '.join(
                    '{}={}'.format(name, self.__get_value_str(name, '{!r}')) for name, _ in self._fields_)
                )

    @classmethod
    def _typeof(cls, field):
        """Get the type of a field
        Example: A._typeof(A.fld)
        Inspired by stackoverflow.com/a/6061483
        """
        for name, type_ in cls._fields_:
            if getattr(cls, name) is field:
                return type_
        raise KeyError

    @classmethod
    def read_from(cls, buff):
        if len(buff) != sizeof(cls):
            print("Error: trying to import buffer of size %d in structure of size %d" % (len(buff), sizeof(cls)))
            raise EOFError
        result = cls.from_buffer_copy(buff)
        return result

    def serialize(self, field_name):
        if field_name == '':
            return bytearray(self)
        for name, type_ in self._fields_:
            if name == field_name: 
                val = getattr(self, name)
                if isinstance(val, Array):
                    return bytearray(val)
                elif type_ == c_uint8:
                    return pack("<B", val) 
                elif type_ == c_uint16:  
                    return pack("<H", val) 
                elif type_ == c_uint32:
                    return pack("<I", val)
                elif type_ == c_uint64:
                    return pack("<Q", val)
                else:
                    # Constructed type: call serialize again
                    return val.serialize('')
        print("Error: %s field not found!" % field_name)
        raise KeyError

    def deserialize(self, field_name, buff):
        if field_name == '':
            a = type(self).read_from(buff)
            for name, type_ in self._fields_:
                f = copy.deepcopy(getattr(a, name))
                setattr(self, name, f)
            return
        for name, type_ in self._fields_:
            if name == field_name:
                setattr(self, name, type_.from_buffer_copy(buff))
                return
        print("Error: %s field not found!" % field_name)
        raise KeyError


################################################################################

def log_print(in_str, verbose=False):
    if verbose == True:
        print(in_str)
    return

# Connect to token and get back credentials
def FIDO_token_get_assets(token_type, keys_path, pet_pin, user_pin, user_feed_back = None):
    card = connect_to_token(token_type)
    token_type_min = token_type.lower()
    token_type_maj = token_type.upper()
  
    # Establish secure channel
    if user_feed_back == None:
        scp = token_full_unlock(card, token_type_min, keys_path+"/"+token_type_maj+"/encrypted_platform_"+token_type_min+"_keys.bin", pet_pin, user_pin, force_pet_name_accept = True)
    else:
        scp, pet_name = token_full_unlock(card, token_type_min, keys_path+"/"+token_type_maj+"/encrypted_platform_"+token_type_min+"_keys.bin", pet_pin, user_pin, force_pet_name_accept = False, only_get_petname = True)
        check = user_feed_back(pet_name)
        if check == False:
            print("Error: user refused Pet Name")
            return None, None, None
        scp = token_full_unlock(card, token_type_min, keys_path+"/"+token_type_maj+"/encrypted_platform_"+token_type_min+"_keys.bin", pet_pin, user_pin, force_pet_name_accept = True)        

    key, sw1, sw2 = scp.token_auth_get_key(user_pin)
    if sw1 != 0x90 or sw2 != 0x00:
        print("Error: error in FIDO_token_get_assets for key")
        return None, None, None
    sdpwd, sw1, sw2 = scp.token_auth_get_sdpwd(user_pin)
    if sw1 != 0x90 or sw2 != 0x00:
        print("Error: error in FIDO_token_get_assets for sdpwd")
        return None, None, None
    return key, sdpwd, scp
    

# Open a FIDO session
def FIDO_token_open_session(scp, token_type, keys_path):
    token_type_min = token_type.lower()
    token_type_maj = token_type.upper()
    # Open FIDO session
    hprivkey, sw1, sw2 = scp.token_auth_fido_send_pkey(user_pin, local_fido_hmac_file=keys_path+"/"+token_type_maj+"/FIDO/fido_hmac.bin")
    if sw1 != 0x90 or sw2 != 0x00:
        print("Error: error in FIDO_token_open_session")
        return None
    return hprivkey

# Register
def FIDO_token_register(scp, keys_path, app_param):
    # Ask for key handle and public key
    r, sw1, sw2 = scp.token_auth_fido_register(app_param)
    if sw1 != 0x90 or sw2 != 0x00:
        print("Error: error in FIDO_token_open_session")
        return None, None
    kh = r[:64]
    ecdsa_pub_key = r[64:]
    return kh, ecdsa_pub_key

# Authenticate
def FIDO_token_authenticate(scp, keys_path, app_param, kh, check_only=False):
    if check_only == True:
        r, sw1, sw2 = scp.token_auth_fido_authenticate_check_only(app_param, kh)
        if sw1 != 0x90 or sw2 != 0x00:
            print("Error: error in FIDO_token_authenticate")
            return False, None
        if r[0] == '\x01':
            return True, None
        else:
            return False, None
    else:
        r, sw1, sw2 = scp.token_auth_fido_authenticate(app_param, kh)
        if sw1 != 0x90 or sw2 != 0x00:
            print("Error: error in FIDO_token_authenticate")
            return False, None    
        if len(r) == 1:
            return False, None    
        else:
            return True, r


#   How it works:
#  
#        SDCard (encrypted)
#   | bitmap of active sectors   | (len 1024 (two sectors))
#   |----------------------------| 
#   | hmac of slotting table+ctr | (len 512 + 2560)
#   |----------------------------|               \
#   | appid1|slotid1|hmac        | (len 512)     |
#   |----------------------------|               |
#   | appid2|slotid2|hmac        | (len 512)     = global slotting table
#   |----------------------------|               |
#   | appid3|slotid3|hmac        | (len 512)     |
#   |----------------------------|               /
#   | ... (upto 4M len max)      |
#   |                            |
#   |xxxxxxxxx (padding) xxxxxxxx|
#   |----------------------------|
#   |                            | <---- at slotid1 sector @
#   |appid|ctr|icon-type|icon_len|
#   |icon.........               |
#   |              xxx(padding)xx|
#   |----------------------------|
#   |                            | <---- at slotid2 sector @
#   |appid|ctr|icon-type|icon_len|
#   |icon.........               |
#   |----------------------------|
#  

SECTOR_SIZE = 512
# Maximum number of slots
SLOTS_NUM   = 8192
# Fixed (maximum) size of a SLOT = 4k bytes
SLOT_SIZE = 4096

class sd_slot_header_entry(Structure, StructHelper):
    _pack_ = 1
    _fields_ = [
        ('appid', c_uint8 * 32),
        ('slotid', c_uint32),
        ('hmac', c_uint8 * 32),
        ('padding', c_uint8 * (SECTOR_SIZE - 68)), 
        ]
    # Zero initialize
    def __init__(self):
        self.deserialize('', b'\x00'*sizeof(self))

# Bitmap of active sectors and hmac
class sd_header(Structure, StructHelper):
    _pack_ = 1
    _fields_ = [
        ('bitmap', c_uint8 * (SLOTS_NUM // 8)),
        # Usage counter for anti-replay
        ('ctr_replay', c_uint64),
        #
        ('hmac', c_uint8 * 32),
        ('padding', c_uint8 * ((SECTOR_SIZE * 6) - 32 - 8)),
        #
        ('slots', sd_slot_header_entry * SLOTS_NUM),
        ]
    # Zero initialize
    def __init__(self):
        self.deserialize('', b'\x00'*sizeof(self))
    def is_slot_active(self, slot_num):
        # Get the representative bit
        if (slot_num // 8) >= len(self.bitmap):
            print("Error: offset %d >= %d in SD bitmap ..." % ((slot_num // 8), len(self.bitmap)))
            sys.exit(-1)
        if self.bitmap[slot_num // 8] & (0x1 << (slot_num % 8)) != 0:
            return True
        else:
            return False
    def set_slot_active(self, slot_num):
        # Set the representative bit
        if (slot_num // 8) >= len(self.bitmap):
            print("Error: offset %d >= %d in SD bitmap ..." % ((slot_num // 8), len(self.bitmap)))
            sys.exit(-1)
        self.bitmap[slot_num // 8] |= (0x1 << (slot_num % 8))
        return
    def set_slot_inactive(self, slot_num):
        # Set the representative bit
        if (slot_num // 8) >= len(self.bitmap):
            print("Error: offset %d >= %d in SD bitmap ..." % ((slot_num // 8), len(self.bitmap)))
            sys.exit(-1)
        if self.bitmap[slot_num // 8] & (0x1 << (slot_num % 8)) != 0:
            self.bitmap[slot_num // 8] ^= (0x1 << (slot_num % 8))
        # Erase the elements in our slot
        self.slots[slot_num].deserialize('', b'\x00'*sizeof(sd_slot_header_entry))
        return
    def update_hmac(self, key):
        # Compute HMAC only on active slots
        hm = local_hmac.new(key, digestmod=hashlib.sha256)
        to_hmac = self.serialize('bitmap') + self.serialize('ctr_replay')
        for i in range(0, SLOTS_NUM):
            if self.is_slot_active(i) == True:
                to_hmac += self.slots[i].serialize('appid') + self.slots[i].serialize('slotid') + self.slots[i].serialize('hmac')
        hm.update(str_decode(to_hmac))
        self.deserialize('hmac', str_encode(hm.digest()))
        return
    def check_hmac(self, key):
        # Compute HMAC
        hm = local_hmac.new(key, digestmod=hashlib.sha256)
        to_hmac = self.serialize('bitmap') + self.serialize('ctr_replay')
        for i in range(0, SLOTS_NUM):
            if self.is_slot_active(i) == True:
                to_hmac += self.slots[i].serialize('appid') + self.slots[i].serialize('slotid') + self.slots[i].serialize('hmac')
        hm.update(str_decode(to_hmac))
        hmac = str_encode(hm.digest())
        if hmac != self.serialize('hmac'):
            return False
        else:
            return True 

icon_types = {
    'NONE'    : 0,
    'RGB'     : 1,
    'RLE'     : 2,
}
def inverse_mapping(f):
    return f.__class__(map(reversed, f.items()))

class sd_icon_rgb_fixed(Structure, StructHelper):
    _pack_ = 1
    _fields_ = [
        ('rgb_color', c_uint8 * 3),
        ('padding', c_uint8 * (SLOT_SIZE - 104 - 3)),
        ]
    # Zero initialize
    def __init__(self):
        self.deserialize('', b'\x00'*sizeof(self))

class sd_icon_data(Union, StructHelper):
    _pack_ = 1
    _fields_ = [
        ('rgb_color', sd_icon_rgb_fixed),
        ('icon_data', c_uint8 * (SLOT_SIZE - 104)),
        ]
    # Zero initialize
    def __init__(self):
        self.deserialize('', b'\x00'*sizeof(self))

class sd_slot_entry(Structure, StructHelper):
    _pack_ = 1
    _fields_ = [
        ('appid', c_uint8 * 32),
        ('flags', c_uint32),
        ('name', c_uint8 * 60),
        ('ctr', c_uint32),
        ('icon_len', c_uint16),
        ('icon_type', c_uint16),
        ('icon', sd_icon_data),
        ]
    # Zero initialize
    def __init__(self):
        self.deserialize('', b'\x00'*sizeof(self))
    def hmac(self, key):
        # Compute HMAC
        hm = local_hmac.new(key, digestmod=hashlib.sha256)
        to_hmac = self.serialize('appid')+self.serialize('flags')+self.serialize('name')+self.serialize('ctr')+self.serialize('icon_len')+self.serialize('icon_type')
        if self.icon_len != 0:
            to_hmac += self.serialize('icon')[:self.icon_len]
        hm.update(str_decode(to_hmac))
        return str_encode(hm.digest())

##############
# Global variable to tell if we use SD surface encryption
USE_SD_ENCRYPTION = True
AES_CBC_ESSIV_SECTOR_SIZE = SLOT_SIZE

def read_SD_sectors(sd_device, sector_num, number = 1, key = None):    
    try:
        sd_device.seek((sector_num * SECTOR_SIZE), 0)
    except:
        print("Error: cannot seek sector %d in SD dev file ..." % sector_num)
        sys.exit(-1) 
    try:
        sectors = sd_device.read(number * SECTOR_SIZE)
    except:
        print("Error: cannot read sector %d in SD dev file ..." % sector_num)
        sys.exit(-1)
    if (key != None) and (USE_SD_ENCRYPTION == True):
        deciphered_sectors = ""
        (iv_key, _, _) = local_sha256(key)
        num_aes_sectors = (number * SECTOR_SIZE) // AES_CBC_ESSIV_SECTOR_SIZE
        if (number * SECTOR_SIZE) % AES_CBC_ESSIV_SECTOR_SIZE != 0:
            num_aes_sectors += 1
        base = (sector_num * SECTOR_SIZE) // AES_CBC_ESSIV_SECTOR_SIZE
        for s in range(0, num_aes_sectors):
            # AES CBC-ESSIV
            iv = derive_essiv_iv(iv_key, base + s, "AES")
            crypto = local_AES.new(key, AES.MODE_CBC, iv=iv)
            b = (s*AES_CBC_ESSIV_SECTOR_SIZE)
            e = ((s+1)*AES_CBC_ESSIV_SECTOR_SIZE)
            if e > (number * SECTOR_SIZE):
                e = (number * SECTOR_SIZE)
            sect = sectors[b:e].decode('latin-1')
            deciphered_sectors += crypto.decrypt(sect)
        return deciphered_sectors.encode('latin-1')
    else:
        return sectors

def write_SD_sectors(sd_device, sector_num, sectors, key = None):
    if (len(sectors) < SECTOR_SIZE) or (len(sectors) % SECTOR_SIZE != 0):
        print("Error: sector length %d illegal" % len(sectors))
        sys.exit(-1) 
    try:
        sd_device.seek((sector_num * SECTOR_SIZE), 0)
    except:
        print("Error: cannot seek sector %d in SD dev file ..." % sector_num)
        sys.exit(-1)
    if (key != None) and (USE_SD_ENCRYPTION == True):
        ciphered_sectors = ""
        (iv_key, _, _) = local_sha256(key)
        num_aes_sectors = len(sectors) // AES_CBC_ESSIV_SECTOR_SIZE
        if len(sectors) % AES_CBC_ESSIV_SECTOR_SIZE != 0:
            num_aes_sectors += 1
        base = (sector_num * SECTOR_SIZE) // AES_CBC_ESSIV_SECTOR_SIZE
        for s in range(0, num_aes_sectors):
            # AES CBC-ESSIV
            iv = derive_essiv_iv(iv_key, base + s, "AES")
            crypto = local_AES.new(key, AES.MODE_CBC, iv=iv)
            b = (s*AES_CBC_ESSIV_SECTOR_SIZE)
            e = ((s+1)*AES_CBC_ESSIV_SECTOR_SIZE)
            if e > len(sectors):
                e = len(sectors)
            sect = sectors[b:e].decode('latin-1')
            ciphered_sectors += crypto.encrypt(sect)
        ciphered_sectors = ciphered_sectors.encode('latin-1')
    else:
        ciphered_sectors = sectors
    try:
        sd_device.write(ciphered_sectors)
    except:
        print("Error: cannot write sector %d in SD dev file ..." % sector_num)
        sys.exit(-1) 
    return
   
#####
def open_SD(device):
    # Try to open our SD card
    sd_device = None
    if not os.path.isfile(device):
        print("Error: SD dev file %s does not exist!" % device)
        sys.exit(-1)
    try:
        sd_device = open(device, 'rb+')
    except:
        print("Error: cannot open SD dev file %s. Please check your right ..." % device)
        sys.exit(-1)
    return sd_device

def close_SD(sd_device):
    sd_device.close()
    return

def init_SD(key, device):
    sd_device = open_SD(device)
    # Derive our keys from the master key
    (AES_key, _, _)  = local_sha256("ENCRYPTION"+ key)
    (HMAC_key, _, _) = local_sha256("INTEGRITY" + key)    
    # Initialize our slotting table
    init_header = sd_header()
    init_header.update_hmac(HMAC_key)
    to_write = init_header.serialize('')
    write_SD_sectors(sd_device, 0, to_write, AES_key)
    close_SD(sd_device)
    return

# Check the intergity of our SD header and get slot appid if asked, or by slot number
def get_SD_appid_slot(key, device, slot_num=None, appid=None, check_hmac=True):
    # Derive our keys from the master key
    (AES_key, _, _)  = local_sha256("ENCRYPTION"+ key)
    (HMAC_key, _, _) = local_sha256("INTEGRITY" + key)    
    sd_device = open_SD(device)
    # First, read the header with the mapping
    header = None
    header = read_SD_sectors(sd_device, 0, sizeof(sd_header) // SECTOR_SIZE, AES_key)
    #
    sd_h = sd_header()
    sd_h.deserialize('', header)
    # Now check the HMAC
    if (sd_h.check_hmac(HMAC_key) == False) and (check_hmac == True):
        print("get_SD_appid_slot: header HMAC not OK!")
        close_SD(sd_device)
        return False, None, None
    if (appid == None) and (slot_num == None):
        close_SD(sd_device)
        return True, None, None
    # slot number explicitly provided
    if slot_num != None:
        if slot_num >= SLOTS_NUM:
            print("get_SD_appid_slot: slot number overflow %d >= %d" % (slot_num, SLOTS_NUM))
            close_SD(sd_device)
            return False, None, None
        slotid = sd_h.slots[slot_num].slotid
        # Read it
        appid_slot_raw = read_SD_sectors(sd_device, slotid, sizeof(sd_slot_entry) // SECTOR_SIZE, AES_key)
        appid_slot = sd_slot_entry()
        appid_slot.deserialize('', appid_slot_raw)
        if check_hmac == True:
            hmac = appid_slot.hmac(HMAC_key)
            if hmac != sd_h.slots[slot_num].serialize('hmac'):
                print("get_SD_appid_slot: slot %d HMAC not OK!" % i)
                close_SD(sd_device)
                return False, appid_slot, slot_num
        if (appid != None) and (appid_slot.serialize('appid') != appid):
            close_SD(sd_device)
            return False, appid_slot, slot_num
        close_SD(sd_device)
        return True, appid_slot, slot_num 
    # Find the appid slot bye searching by appid
    for i in range(0, SLOTS_NUM):
        # Get active slot data
        if (sd_h.slots[i].serialize('appid') == appid) and (sd_h.is_slot_active(i) == True):
            # Appid found, get the sector
            slotid = sd_h.slots[i].slotid
            # Read it
            appid_slot_raw = read_SD_sectors(sd_device, slotid, sizeof(sd_slot_entry) // SECTOR_SIZE, AES_key)
            appid_slot = sd_slot_entry()
            appid_slot.deserialize('', appid_slot_raw)
            if check_hmac == True:
                hmac = appid_slot.hmac(HMAC_key)
                if hmac != sd_h.slots[i].serialize('hmac'):
                    print("get_SD_appid_slot: slot %d HMAC not OK!" % i)
                    close_SD(sd_device)
                    return False, appid_slot, i 
            close_SD(sd_device)
            return True, appid_slot, i
    return True, None, None

# Remove an appid
def remove_appid(key, device, appid=None, slot_num=None, check_hmac=True):
    if (appid == None) and (slot_num == None):
        print("remove_appid: appid or slot_num must be not None!")
        return False
    # Derive our keys from the master key
    (AES_key, _, _)  = local_sha256("ENCRYPTION"+ key)
    (HMAC_key, _, _) = local_sha256("INTEGRITY" + key)
    sd_device = open_SD(device)
    # First, read the header with the mapping
    header = read_SD_sectors(sd_device, 0, sizeof(sd_header) // SECTOR_SIZE, AES_key)
    #
    sd_h = sd_header()
    sd_h.deserialize('', header)
    # Now check the HMAC
    if (sd_h.check_hmac(HMAC_key) == False) and (check_hmac == True):
        print("remove_appid: header HMAC not OK!")
        close_SD(sd_device)
        return False
    # If the slot number is provided, use it
    if (slot_num != None):
       if slot_num >= SLOTS_NUM:
           print("remove_appid: asked slot overflow %d >= %d" % (slot_num, SLOTS_NUM))
       if (appid != None) and (sd_h.slots[slot_num].serialize('appid') != appid):
           print("remove_appid: appid differ in slot %d from provided one" % slot_num)
           close_SD(sd_device)
           return False       
    # Find and remove our appid
    for i in range(0, SLOTS_NUM):
        # Get active slot data
        if (sd_h.slots[i].serialize('appid') == appid) and (sd_h.is_slot_active(i) == True):
            slot_num = i
    # Now remove
    if slot_num != None:
        print("remove_appid: removing slot %d" % slot_num)
        # Zeroize the slot content
        sd_appid_slot = sd_slot_entry() # zero by default
        to_write = sd_appid_slot.serialize('')
        if len(to_write) != sizeof(sd_slot_entry):
            # Sanity check
            print("create_new_appid: error when serializing!")
            return False
        if write_SD_sectors(sd_device, sd_h.slots[slot_num].slotid, to_write, AES_key) == False:
            # Write failure
            print("create_new_appid: SD write failure!")
            return False 
        sd_h.set_slot_inactive(slot_num)
        # Update our HMAC
        sd_h.update_hmac(HMAC_key)
        # Save our header
        to_write = sd_h.serialize('')
        if len(to_write) != sizeof(sd_header):
            # Sanity check
            print("remove_appid: error when serializing!")
            return False
        # Write the header
        if write_SD_sectors(sd_device, 0, to_write, AES_key) == False:
            # Write failure
            print("remove_appid: SD write failure!")
            return False
        return True 
    # Nothing found
    print("remove_appid: asked appid not found!")
    return False


# Update or create new appid and add a new slot
def update_appid(key, device, appid, slot_num=None, name=None, ctr=0, icon=None, flags=0, check_hmac=True):
    # Derive our keys from the master key
    (AES_key, _, _)  = local_sha256("ENCRYPTION"+ key)
    (HMAC_key, _, _) = local_sha256("INTEGRITY" + key)    
    sd_device = open_SD(device)
    # First, read the header with the mapping
    header = read_SD_sectors(sd_device, 0, sizeof(sd_header) // SECTOR_SIZE, AES_key)
    #
    sd_h = sd_header()
    sd_h.deserialize('', header)
    # Now check the HMAC
    if (sd_h.check_hmac(HMAC_key) == False) and (check_hmac == True):
        print("update_appid: header HMAC not OK!")
        close_SD(sd_device)
        return False, None, None, None
    if slot_num != None:       
        # Slot number provided, force it
        if slot_num >= SLOTS_NUM:
            print("update_appid: asked slot %d overflow max %d" % (slot_num, SLOTS_NUM))
            close_SD(sd_device)
            return False, None, None, None
        num_slot = slot_num
        sd_appid_slot = sd_slot_entry()
        sd_appid_slot.deserialize('appid', appid)
    else:
        # Slot number not provided, find it
        _, sd_appid_slot, num_slot = get_SD_appid_slot(key, device, appid=appid)
    found = False
    if sd_appid_slot == None:
        # Find a free slot
        found = False
        for i in range(0, SLOTS_NUM):
            if sd_h.is_slot_active(i) == False:
                found = True
                num_slot = i
                break
        if found == False:
            print("create_new_appid: slot overflow!")
            close_SD(sd_device)
            return False, None, None, None
        # Now create our new slot
        print("create_new_appid: creating new slot %d" % num_slot)
        sd_appid_slot = sd_slot_entry()
        sd_appid_slot.deserialize('appid', appid)
    else:
        print("create_new_appid: updating slot %d" % num_slot)
    # Fill our slot
    sd_appid_slot.flags = flags
    sd_appid_slot.ctr = ctr
    if name != None:
        if len(name) > 60:
            print("update_appid: name %s too long!" % name)
            return False, None, None, None
        sd_appid_slot.deserialize('name', name+(b'\x00'*(60-len(name))))
    # Put our icon data inside it
    sd_appid_slot.icon_len = 0
    sd_appid_slot.icon_type = icon_types['NONE']
    if icon != None:
        if len(icon) == 0:
            # None type icon
            sd_appid_slot.icon_type = icon_types['NONE']
        elif len(icon) == 3:
            # RGB type icon
            sd_appid_slot.icon_type = icon_types['RGB']
        elif len(icon) > 3:
            # RLE type icon
            sd_appid_slot.icon_type = icon_types['RLE']
        else:
            print("update_appid: bad icon len %d!" % len(icon))
            return False, None, None, None
        sd_appid_slot.icon_len = len(icon)
        sd_appid_slot.deserialize('icon', icon+(b'\x00'*(sizeof(sd_icon_data) - len(icon))))
    # We use a fixed address
    sd_h.slots[num_slot].slotid = (sizeof(sd_header) + (num_slot * SLOT_SIZE)) // SECTOR_SIZE
    sd_h.slots[num_slot].deserialize('appid', appid)
    # Now update the hmacs and save the slot
    hmac = sd_appid_slot.hmac(HMAC_key)
    sd_h.slots[num_slot].deserialize('hmac', hmac)
    # Write the slot at its address
    to_write = sd_appid_slot.serialize('')
    if len(to_write) != sizeof(sd_slot_entry):
        # Sanity check
        print("create_new_appid: error when serializing!")
        return False, None, None, None
    if write_SD_sectors(sd_device, sd_h.slots[num_slot].slotid, to_write, AES_key) == False:
        # Write failure
        print("create_new_appid: SD write failure!")
        return False, None, None, None
    # Set the slot active and update the header HMAC
    sd_h.set_slot_active(num_slot)
    sd_h.update_hmac(HMAC_key)
    to_write = sd_h.serialize('')
    if len(to_write) != sizeof(sd_header):
        # Sanity check
        print("create_new_appid: error when serializing!")
        return False, None, None, None
    # Write the header
    if write_SD_sectors(sd_device, 0, to_write, AES_key) == False:
        # Write failure
        print("create_new_appid: SD write failure!")
        return False, None, None, None
    return True, num_slot, sd_h.slots[num_slot], sd_appid_slot

# Pretty printing of our state
def get_num_active_slots(key, device):
    (AES_key, _, _)  = local_sha256("ENCRYPTION"+ key)
    (HMAC_key, _, _) = local_sha256("INTEGRITY" + key)
    sd_device = open_SD(device)
    # First, read the header with the mapping
    header = read_SD_sectors(sd_device, 0, sizeof(sd_header) // SECTOR_SIZE, AES_key)
    #
    sd_h = sd_header()
    sd_h.deserialize('', header)
    num_active_slots = 0
    for i in range(0, SLOTS_NUM):
        # Get active slot data
        if (sd_h.is_slot_active(i) == True):
            num_active_slots += 1
    return num_active_slots

def dump_slots(key, device, check_hmac=True, slot_num=None, verbose=False, curr_slot_progress = None):
    # Derive our keys from the master key
    (AES_key, _, _)  = local_sha256("ENCRYPTION"+ key)
    (HMAC_key, _, _) = local_sha256("INTEGRITY" + key)
    sd_device = open_SD(device)
    # First, read the header with the mapping
    header = read_SD_sectors(sd_device, 0, sizeof(sd_header) // SECTOR_SIZE, AES_key)
    #
    sd_h = sd_header()
    sd_h.deserialize('', header)
    # Now check the HMAC
    if (sd_h.check_hmac(HMAC_key) == False) and (check_hmac == True):
        print("dump_slots: header HMAC not OK!")
        close_SD(sd_device)
        return None
    # Traverse all our active slots:
    active_slots = []
    for i in range(0, SLOTS_NUM):
        if curr_slot_progress != None:
            early_exit = curr_slot_progress(i, SLOTS_NUM)
            if early_exit == True:
                # Early exit asked
                return None
        if (slot_num != None) and not(i in slot_num):
            continue
        # Get active slot data
        if (sd_h.is_slot_active(i) == True):
            log_print("===========", verbose)
            log_print("dump_slots: slot %d is active!" % i, verbose)
            # Print information of the slot
            log_print(" |- appid : %s" % (binascii.hexlify(sd_h.slots[i].serialize('appid'))), verbose)
            log_print(" |- slotid: 0x%08x (sector @0x%08x)" % (sd_h.slots[i].slotid, sd_h.slots[i].slotid * SECTOR_SIZE), verbose)
            log_print(" |- hmac  : %s" % (binascii.hexlify(sd_h.slots[i].serialize('hmac'))), verbose)
            close_SD(sd_device)
            # Now dump the slot content by index
            _, appid_slot, _ =  get_SD_appid_slot(key, device, appid=None, slot_num=i, check_hmac=check_hmac)
            # Check hmac
            hmac = appid_slot.hmac(HMAC_key)
            if hmac != sd_h.slots[i].serialize('hmac'):
                log_print("dump_slots: slot %d HMAC not OK!" % i, verbose)
                return None          
            log_print("  Content:", verbose)
            log_print("    |- appid     : %s" % (binascii.hexlify(appid_slot.serialize('appid'))), verbose)
            log_print("    |- flags     : 0x%08x" % (appid_slot.flags), verbose)
            log_print("    |- name      : %s" % (appid_slot.serialize('name').decode("latin-1")), verbose)
            log_print("    |- ctr       : 0x%08x" % (appid_slot.ctr), verbose)
            log_print("    |- icon_len  : 0x%04x" % (appid_slot.icon_len), verbose)
            log_print("    |- icon_type : 0x%04x (%s)" % (appid_slot.icon_type, inverse_mapping(icon_types)[appid_slot.icon_type]), verbose)
            if appid_slot.icon_len != 0:
                log_print("    |- icon      : %s" % binascii.hexlify(appid_slot.serialize('icon')[:min(32, appid_slot.icon_len)]), verbose)
            active_slots += [(i, sd_h.slots[i].serialize('appid'), sd_h.slots[i].slotid, sd_h.slots[i].slotid * SECTOR_SIZE, appid_slot)]
    return active_slots

#####
def PrintUsage():
    executable = os.path.basename(__file__)
    print("Error when executing %s\n\tUsage:\t%s keys_path PetPIN UserPIN" % (executable, executable))
    sys.exit(-1)

def FIDO_test(scp):
    hprivkey = FIDO_token_open_session(scp, "auth", keys_path)
    #
    kh, ecdsa_pub_key = FIDO_token_register(scp, keys_path, "\x00"*32)
    #
    check, ecdsa_priv_key = FIDO_token_authenticate(scp, keys_path, "\x00"*32, kh)
    #
    check, ecdsa_priv_key = FIDO_token_authenticate(scp, keys_path, "\x00"*32, kh, check_only=True)
    #
    check, ecdsa_priv_key = FIDO_token_authenticate(scp, keys_path, "\x01"*32, kh, check_only=True)
    return

def get_key_from_token(keys_path, pet_pin, user_pin):
    key, sdpwd, scp = FIDO_token_get_assets("auth", keys_path, pet_pin, user_pin)
    return key, sdpwd

#################################
# Get our arguments
if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    # Get the arguments
    if len(sys.argv) <= 3:
        PrintUsage()
    keys_path = sys.argv[1]
    pet_pin = sys.argv[2]
    user_pin = sys.argv[3]
    #key, sdpwd, scp = FIDO_token_get_assets("auth", keys_path, pet_pin, user_pin)
    #key = key[:32]
    key = "\xaa"*32
    sdpwd = "\xbb"*16
    print(local_hexlify(key))
    print(local_hexlify(sdpwd))    
    #
    init_SD(key, "/tmp/sd.dump")
    check, appid, num_slot = get_SD_appid_slot(key, "/tmp/sd.dump", appid=b"\xaa"*32)
    check =  update_appid(key, "/tmp/sd.dump", b"\xcd"*32, ctr=0x11223344, icon=None, check_hmac=True)
    check, appid, num_slot = get_SD_appid_slot(key, "/tmp/sd.dump", appid=b"\xcd"*32)
    check =  update_appid(key, "/tmp/sd.dump", b"\xab"*32, ctr=0x55667788, icon=None, check_hmac=True)
    check, appid, num_slot = get_SD_appid_slot(key, "/tmp/sd.dump", appid=b"\xab"*32)
    dump_slots(key, "/tmp/sd.dump", verbose=True)
    check = remove_appid(key, "/tmp/sd.dump", b"\xab"*32)
    check, appid, num_slot = get_SD_appid_slot(key, "/tmp/sd.dump", appid=b"\xab"*32)
    dump_slots(key, "/tmp/sd.dump", verbose=True)
    check =  update_appid(key, "/tmp/sd.dump", b"\xaa"*32, ctr=0x1, icon=b"\xaa\xbb\xcc", check_hmac=True)
    check =  update_appid(key, "/tmp/sd.dump", b"\xbb"*32, ctr=0x2, icon=None, check_hmac=True)
    with open("/tmp/amazon.png", "rb") as f:        
        check =  update_appid(key, "/tmp/sd.dump", b"\xcc"*32, ctr=0x3, name=b"Amazon", icon=RLE_compress_buffer(f.read(), target_dim=(45,45), colors=6)[0], check_hmac=True)
        for i in range(0, 200):
            f.seek(0)
            check =  update_appid(key, "/tmp/sd.dump", ("\xcc"*31+chr(i)).encode("latin-1"), ctr=i, name=("Amazon %d" % i).encode("latin-1"), icon=RLE_compress_buffer(f.read(), target_dim=(45,45), colors=6)[0], check_hmac=True)
   
    dump_slots(key, "/tmp/sd.dump", verbose=True)
