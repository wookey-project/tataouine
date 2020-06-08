# Import our local utils
import sys, os, inspect
FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
SCRIPT_PATH = os.path.dirname(os.path.abspath(FILENAME)) + "/"
sys.path.append(SCRIPT_PATH+'../')

from common_utils import *
from crypto_utils import *
from firmware_utils import *
from token_utils import *


# Check a token
# TODO: these are basic tests that should be augmented to test all
# the tokens automatons and corner cases!
def check_token(token_type, keys_path, pet_pin, user_pin):
    card = connect_to_token(token_type)
    token_type_min = token_type.lower()
    token_type_maj = token_type.upper()
    # Establish secure channel
    scp = token_full_unlock(card, token_type_min, keys_path+"/"+token_type_maj+"/encrypted_platform_"+token_type_min+"_keys.bin", pet_pin, user_pin, force_pet_name_accept = True)
    old_pet_name, sw1, sw2 = scp.token_get_pet_name()
    # Modify the Pet Name
    new_pet_name = "This is a test pet Name"
    resp, sw1, sw2 = scp.token_set_pet_name(new_pet_name)
    # Get the new Pet Name
    resp, sw1, sw2 = scp.token_get_pet_name()
    if resp != new_pet_name:
        print("Error: error in %s self tests in token_set_pet_name/token_get_pet_name: got %s instead of %s" % (token_type, resp, new_pet_name))
        sys.exit(-1)
    # Try to set very big Pet Name, should failt
    resp, sw1, sw2 = scp.token_set_pet_name('A'*220)
    if sw1 != 0x63 and sw2 != 0x02:
        print("Error in token_set_pet_name")
        sys.exit(-1)
    resp, sw1, sw2 = scp.token_get_pet_name()
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_get_pet_name")
        sys.exit(-1)
    if resp != new_pet_name:
        print("Error: error in %s self tests in token_set_pet_name/token_get_pet_name: got %s instead of %s" % (token_type, resp, new_pet_name))
        sys.exit(-1)
    # Put back the old Pet Name
    resp, sw1, sw2 = scp.token_set_pet_name(old_pet_name)
    if sw1 != 0x90 and sw2 != 0x00:
        print("Error in token_set_pet_name")
        sys.exit(-1)
    resp, sw1, sw2 = scp.token_get_pet_name()
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_get_pet_name")
        sys.exit(-1)
    if resp != old_pet_name:
        print("Error: error in %s self tests in token_set_pet_name/token_get_pet_name: got %s instead of %s" % (token_type, resp, new_pet_name))
        sys.exit(-1)
    # Set the PetPIN
    resp, sw1, sw2 = scp.token_set_pet_pin("1111")
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_set_pet_pin")
        sys.exit(-1)
    # Set the UserPIN
    resp, sw1, sw2 = scp.token_set_user_pin("2222")
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_set_user_pin")
        sys.exit(-1)
    # Lock the token
    resp, sw1, sw2 = scp.token_full_lock()
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_full_lock")
        sys.exit(-1)
    # Now unlock again with new pins
    scp = token_full_unlock(card, token_type_min, keys_path+"/"+token_type_maj+"/encrypted_platform_"+token_type_min+"_keys.bin", "1111", "2222", force_pet_name_accept = True)
    # Put back the old PINs
    resp, sw1, sw2 = scp.token_set_pet_pin(pet_pin)
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_set_pet_pin")
        sys.exit(-1)
    resp, sw1, sw2 = scp.token_set_user_pin(user_pin)
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_set_user_pin")
        sys.exit(-1)
    # Only lock the UserPIN
    resp, sw1, sw2 = scp.token_user_pin_lock()
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_user_pin_lock")
        sys.exit(-1)
    # Get random: the first call should fail
    resp, sw1, sw2 = scp.token_get_random(100)
    if sw1 != 0x63 and sw2 != 0x02:
        print("Error in token_get_random")
        sys.exit(-1)
    # The second call shuld be OK after User pin unlock
    resp, sw1, sw2 = scp.token_unlock_user_pin(user_pin)
    if sw1 != 0x90 and sw2 != 0x90:
        print("Error in token_unlock_user_pin")
        sys.exit(-1)
    resp, sw1, sw2 = scp.token_get_random(100)
    if sw1 != 0x90 and sw2 != 0x00:
        print("Error in token_get_random")
        sys.exit(-1) 
    return

def PrintUsage():
    executable = os.path.basename(__file__)
    print("Error when executing %s\n\tUsage:\t%s token_type keys_path PetPIN UserPIN" % (executable, executable))
    sys.exit(-1)

# Get our arguments
if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    # Get the arguments
    if len(sys.argv) <= 4:
        PrintUsage()
    token_type = sys.argv[1]
    keys_path = sys.argv[2]
    pet_pin = sys.argv[3]
    user_pin = sys.argv[4]
    check_token(token_type, keys_path, pet_pin, user_pin)
