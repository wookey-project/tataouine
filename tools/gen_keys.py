# Generate all the keys for the platform and for the
# Javacard tokens.

from common_utils import *
from crypto_utils import *

def PrintUsage():
    executable = os.path.basename(__file__)
    print("Usage: "+sys.argv[0]+" private_path ec_utils_path curve_name use_external_sig_token platform_profile")
    sys.exit(-1)

# TODO/FIXME: replace the UNIX sys_cmd commands (touch, rm -f, ...) with
# OS agnostic Python functions so that we can run the script anywhere!

if __name__ == '__main__':
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handler)
    # Current script path
    FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
    SCRIPT_PATH = os.path.dirname(os.path.abspath(FILENAME)) + "/"

    # Get the current interpreter
    INTERPRETER  = sys.executable

    # The tools paths
    KEY2JAVA = INTERPRETER + " " + SCRIPT_PATH+"/key2java.py"
    ENCRYPT_PLATFORM_DATA_HEADER = INTERPRETER + " " + SCRIPT_PATH+"/encrypt_platform_data.py"
    PROJECT_PATH = SCRIPT_PATH+"../"

    # Get the curve name, signature algorithm and hash algorithm

    CURVE_NAME = None
    if len(sys.argv) < 6:
        PrintUsage()
    # The generated files path
    KEYS_DIR = sys.argv[1]
    EC_UTILS = sys.argv[2]
    if sys.argv[3] == "FRP256V1":
        CURVE_NAME = "FRP256V1"
    elif sys.argv[3] == "BRAINPOOLP256R1":
        CURVE_NAME = "BRAINPOOLP256R1"
    elif sys.argv[3] == "SECP256R1":
        CURVE_NAME = "SECP256R1"
    else:
        print("Error: asked curve "+sys.argv[3]+" is not allowed.")
        print("\tPossible values: FRP256V1, BRAINPOOLP256R1 or SECP256R1")
        sys.exit(-1)

    # Check if we want to use an external token for the signature or not
    USE_SIG_TOKEN = None
    if sys.argv[4] == "USE_SIG_TOKEN":
        USE_SIG_TOKEN = True
    elif sys.argv[4] == "NO_SIG_TOKEN":
        USE_SIG_TOKEN = False
    else:
        print("Error: arg4 "+sys.argv[4]+" is not allowed.")
        print("\tPossible values: USE_SIG_TOKEN or NO_SIG_TOKEN")
        sys.exit(-1)
    # Get the platform profile
    PLATFORM_PROFILE = sys.argv[5]

    # Signature algorithm and hash function are fixed (mainly because the
    # external Javacard tokens only support these ...
    SIG_ALG_NAME = "ECDSA"
    HASH_ALG_NAME = "SHA_256"

    # Create the directory if it does not exist
    sys_cmd("mkdir -p "+KEYS_DIR)
    # Clean all the files
    sys_cmd("rm -rf "+KEYS_DIR+"/*")

    # Generate binaries and C/Javacard headers for the platform and the token
    # ========================================================================
    cmd_gen_keys_base = EC_UTILS+" gen_keys "+CURVE_NAME+" "+SIG_ALG_NAME+" "

    # Generate the AUTH, DFU and SIG paths
    AUTH_TOKEN_PATH = KEYS_DIR+"/AUTH"
    DFU_TOKEN_PATH = KEYS_DIR+"/DFU"
    SIG_TOKEN_PATH = KEYS_DIR+"/SIG"

    sys_cmd("mkdir -p "+AUTH_TOKEN_PATH)
    sys_cmd("mkdir -p "+DFU_TOKEN_PATH)
    sys_cmd("mkdir -p "+SIG_TOKEN_PATH)

    #=================
    # Asymmetric keys
    ## AUTH token
    sys_cmd(cmd_gen_keys_base+AUTH_TOKEN_PATH+"/platform_auth")
    sys_cmd(cmd_gen_keys_base+AUTH_TOKEN_PATH+"/token_auth")
    ## DFU token
    sys_cmd(cmd_gen_keys_base+DFU_TOKEN_PATH+"/platform_dfu")
    sys_cmd(cmd_gen_keys_base+DFU_TOKEN_PATH+"/token_dfu")
    ## SIG token
    # NOTE: We generate these keys even when we do not use a signature
    # token but local signature. These files won't be used in this last
    # case!
    sys_cmd(cmd_gen_keys_base+SIG_TOKEN_PATH+"/platform_sig")
    sys_cmd(cmd_gen_keys_base+SIG_TOKEN_PATH+"/token_sig")

    ## Firmware signature keys
    sys_cmd(cmd_gen_keys_base+SIG_TOKEN_PATH+"/token_sig_firmware")

    ## Cleanup the unneccessary header files
    sys_rm_file(AUTH_TOKEN_PATH+"/*.h")
    sys_rm_file(DFU_TOKEN_PATH+"/*.h")
    sys_rm_file(SIG_TOKEN_PATH+"/*.h")

    #=================
    # Max bumber of tries for PINs and secure channel mount fails
    ## AUTH
    DEFAULT_AUTH_MAX_PIN_TRIES = 3
    DEFAULT_AUTH_MAX_SC_TRIES  = 10
    auth_max_pin_tries = get_user_input("Please provide the maximum AUTH pin tries before locking the token:\n")
    auth_max_sc_tries = get_user_input("Please provide the maximum AUTH secure channel tries before locking the token:\n")
    if auth_max_pin_tries == "":
        auth_max_pin_tries = DEFAULT_AUTH_MAX_PIN_TRIES
    if auth_max_sc_tries == "":
        auth_max_sc_tries = DEFAULT_AUTH_MAX_SC_TRIES
    ## DFU
    DEFAULT_DFU_MAX_PIN_TRIES = 3
    DEFAULT_DFU_MAX_SC_TRIES  = 10
    dfu_max_pin_tries = get_user_input("Please provide the maximum DFU pin tries before locking the token:\n")
    dfu_max_sc_tries = get_user_input("Please provide the maximum DFU secure channel tries before locking the token:\n")
    if dfu_max_pin_tries == "":
        dfu_max_pin_tries = DEFAULT_DFU_MAX_PIN_TRIES
    if dfu_max_sc_tries == "":
        dfu_max_sc_tries = DEFAULT_DFU_MAX_SC_TRIES
    ## SIG
    if USE_SIG_TOKEN == True:
        DEFAULT_SIG_MAX_PIN_TRIES = 3
        DEFAULT_SIG_MAX_SC_TRIES  = 10
        sig_max_pin_tries = get_user_input("Please provide the maximum SIG pin tries before locking the token:\n")
        sig_max_sc_tries = get_user_input("Please provide the maximum SIG secure channel tries before locking the token:\n")
        if sig_max_pin_tries == "":
            sig_max_pin_tries = DEFAULT_SIG_MAX_PIN_TRIES
        if sig_max_sc_tries == "":
            sig_max_sc_tries = DEFAULT_SIG_MAX_SC_TRIES

    #=================
    # PET pin, PET name
    ## AUTH
    DEFAULT_AUTH_PET_PIN = "1234"
    DEFAULT_AUTH_PET_NAME = "My dog name is Bob!"
    auth_pet_pin = get_user_input("Please provide your AUTH PET pin:\n")
    auth_pet_name = get_user_input("Please provide your AUTH PET secret name:\n")
    if auth_pet_pin == "":
        auth_pet_pin = DEFAULT_AUTH_PET_PIN
    if auth_pet_name == "":
        auth_pet_name = DEFAULT_AUTH_PET_NAME
    # TODO: check pin and secret name entropy ...
    if check_string_security_policy(auth_pet_pin, strtype='PIN') == False:
        print("Error: bad entropy for AUTH Pet PIN")
        sys.exit(-1)
    if check_string_security_policy(auth_pet_name, strtype='NAME') == False:
        print("Error: bad entropy for AUTH Pet Name")
        sys.exit(-1)
    save_in_file(auth_pet_pin, AUTH_TOKEN_PATH+"/shared_auth_petpin.bin")
    save_in_file(auth_pet_name, AUTH_TOKEN_PATH+"/shared_auth_petname.bin")
    ## DFU
    DEFAULT_DFU_PET_PIN = "1234"
    DEFAULT_DFU_PET_NAME = "My cat name is Alice!"
    dfu_pet_pin = get_user_input("Please provide your DFU PET pin:\n")
    dfu_pet_name = get_user_input("Please provide your DFU PET secret name:\n")
    if dfu_pet_pin == "":
        dfu_pet_pin = DEFAULT_DFU_PET_PIN
    if dfu_pet_name == "":
        dfu_pet_name = DEFAULT_DFU_PET_NAME
    # TODO: check pin and secret name entropy ...
    if check_string_security_policy(dfu_pet_pin, strtype='PIN') == False:
        print("Error: bad entropy for DFU Pet PIN")
        sys.exit(-1)
    if check_string_security_policy(dfu_pet_name, strtype='NAME') == False:
        print("Error: bad entropy for DFU Pet Name")
        sys.exit(-1)
    save_in_file(dfu_pet_pin, DFU_TOKEN_PATH+"/shared_dfu_petpin.bin")
    save_in_file(dfu_pet_name, DFU_TOKEN_PATH+"/shared_dfu_petname.bin")
    ## SIG
    if USE_SIG_TOKEN == True:
        DEFAULT_SIG_PET_PIN = "1234"
        DEFAULT_SIG_PET_NAME = "My fish name is Eve!"
        sig_pet_pin = get_user_input("Please provide your SIG PET pin:\n")
        sig_pet_name = get_user_input("Please provide your SIG PET secret name:\n")
        if sig_pet_pin == "":
            sig_pet_pin = DEFAULT_SIG_PET_PIN
        if sig_pet_name == "":
            sig_pet_name = DEFAULT_SIG_PET_NAME
        # TODO: check pin and secret name entropy ...
        if check_string_security_policy(sig_pet_pin, strtype='PIN') == False:
            print("Error: bad entropy for SIG Pet PIN")
            sys.exit(-1)
        if check_string_security_policy(sig_pet_name, strtype='NAME') == False:
            print("Error: bad entropy for SIG Pet Name")
            sys.exit(-1)
        save_in_file(sig_pet_pin, SIG_TOKEN_PATH+"/shared_sig_petpin.bin")
        save_in_file(sig_pet_name, SIG_TOKEN_PATH+"/shared_sig_petname.bin")
    else:
        # If we do not want to use a signature token, we have to use local
        # password storage with a strong entropy
        DEFAULT_LOCAL_STORAGE_PASSWORD = "mylocalpassword"
        local_storage_password = get_user_input("Please provide your local storage password for the SIG keys (used to sign and encrypt the firmware):\n")
        if local_storage_password == "":
            local_storage_password = DEFAULT_LOCAL_STORAGE_PASSWORD
        # TODO: check local storage password entropy. This is critical since
        # this password handles very sensitive private keys
        if check_string_security_policy(local_storage_password, strtype='PASSWORD') == False:
            print("Error: bad entropy for AUTH Pet PIN")
            sys.exit(-1)
        save_in_file(local_storage_password, SIG_TOKEN_PATH+"/local_storage_password.bin")

    #=================
    # User PIN
    ## AUTH
    DEFAULT_AUTH_USER_PIN = "1234"
    auth_user_pin = get_user_input("Please provide your AUTH USER pin:\n")
    if auth_user_pin == "":
        auth_user_pin = DEFAULT_AUTH_USER_PIN
    # TODO: check pin entropy ...
    if check_string_security_policy(auth_user_pin, strtype='PIN') == False:
        print("Error: bad entropy for AUTH User PIN")
        sys.exit(-1)
    save_in_file(auth_user_pin, AUTH_TOKEN_PATH+"/shared_auth_userpin.bin")
    ## DFU
    DEFAULT_DFU_USER_PIN = "1234"
    dfu_user_pin = get_user_input("Please provide your DFU USER pin:\n")
    if dfu_user_pin == "":
        dfu_user_pin = DEFAULT_DFU_USER_PIN
    # TODO: check pin entropy ...
    if check_string_security_policy(dfu_user_pin, strtype='PIN') == False:
        print("Error: bad entropy for DFU User PIN")
        sys.exit(-1)
    save_in_file(dfu_user_pin, DFU_TOKEN_PATH+"/shared_dfu_userpin.bin")
    ## SIG
    if USE_SIG_TOKEN == True:
        DEFAULT_SIG_USER_PIN = "1234"
        sig_user_pin = get_user_input("Please provide your SIG USER pin:\n")
        if sig_user_pin == "":
            sig_user_pin = DEFAULT_SIG_USER_PIN
        # TODO: check pin entropy ...
        if check_string_security_policy(sig_user_pin, strtype='PIN') == False:
            print("Error: bad entropy for SIG User PIN")
            sys.exit(-1)
        save_in_file(sig_user_pin, SIG_TOKEN_PATH+"/shared_sig_userpin.bin")

    # In case of FIDO profile, we also generate the attestation certificate as
    # well as the ECDSA attestation key
    if PLATFORM_PROFILE == "u2f2":
        print("==> U2F2 profile: generating attestation certificate")
        # Use our external tool to generate the attestation certificate and the key
        CERTIFICATE_GEN = SCRIPT_PATH+"/fido_gen_certificate.sh"
        sys_cmd("mkdir -p "+AUTH_TOKEN_PATH+"/FIDO/")
        sys_cmd("sh "+CERTIFICATE_GEN+" "+AUTH_TOKEN_PATH+"/FIDO/")
        # Now generate the C header files
        KEY2C = INTERPRETER + " " + SCRIPT_PATH+"/key2c.py"
        sys_cmd(KEY2C+" "+AUTH_TOKEN_PATH+"/FIDO/attestation.der"+" "+AUTH_TOKEN_PATH+"/FIDO/attestation_key.der")

    #=================
    # Master symmetric keys
    ## Master encryption key in the AUTH token
    # NOTE: we generate a 64 bytes buffer here for various usages
    save_in_file(gen_rand_string(64), AUTH_TOKEN_PATH+"/master_symmetric_auth_key.bin")
    # SDCard Passwd in the AUTH token
    save_in_file(gen_rand_string(16), AUTH_TOKEN_PATH+"/sd_pwd_auth.bin")
    ## Master firmware encryption key shared between the DFU and SIG tokens
    shared_master_dfu_sig = gen_rand_string(64)
    save_in_file(shared_master_dfu_sig, DFU_TOKEN_PATH+"/master_symmetric_dfu_key.bin")
    save_in_file(shared_master_dfu_sig, SIG_TOKEN_PATH+"/master_symmetric_sig_key.bin")
    ##
    # In case of DFU and SIG, we also have an over-encryption key
    shared_overencrypt_dfu_sig = gen_rand_string(32)
    save_in_file(shared_overencrypt_dfu_sig, DFU_TOKEN_PATH+"/symmetric_overencrypt_dfu_key_iv.bin")
    save_in_file(shared_overencrypt_dfu_sig, SIG_TOKEN_PATH+"/symmetric_overencrypt_sig_key_iv.bin")
    # Generate the associated C headers
    # DFU case
    text  = "/* NOTE: here lies an overencryption firmware key allowing secret seperation (with the application handling the token) */\n\n"
    text += "/* Handle backup SRAM usage for the overencryption key and IV content */\n"
    text += "#ifdef CONFIG_APP_DFUFLASH_USE_BKUP_SRAM\n"
    text += "  #define KEYBAG_SECTION "+"__attribute__((section(\".noupgrade.dfu_flash_key_iv\")))\n"
    text += "#else\n"
    text += "  #define KEYBAG_SECTION\n"
    text += "#endif /* CONFIG_APP_DFUFLASH_USE_BKUP_SRAM */\n\n\n"
    text += "KEYBAG_SECTION const unsigned char symmetric_overencrypt_dfu_key_iv[]    = { "
    for byte in read_in_file(DFU_TOKEN_PATH+"/symmetric_overencrypt_dfu_key_iv.bin"):
        text += "0x%02x, " % stringtoint(byte)
    text += "};"
    save_in_file(text, DFU_TOKEN_PATH+"/symmetric_overencrypt_dfu_key_iv.h")
    # SIG case
    text  = "/* NOTE: here lies an overencryption firmware key allowing secret seperation (with the application handling the token) */\n\n"
    text += "/* Handle backup SRAM usage for the overencryption key and IV content */\n"
    text += "#ifdef SIG_USE_BKUP_SRAM\n"
    text += "  #define KEYBAG_SECTION "+"__attribute__((section(\".noupgrade.sig_flash_key_iv\")))\n"
    text += "#else\n"
    text += "  #define KEYBAG_SECTION\n"
    text += "#endif /* SIG_USE_BKUP_SRAM */\n\n\n"
    text += "KEYBAG_SECTION const unsigned char symmetric_overencrypt_sig_key_iv[]    = { "
    for byte in read_in_file(SIG_TOKEN_PATH+"/symmetric_overencrypt_sig_key_iv.bin"):
        text += "0x%02x, " % stringtoint(byte)
    text += "};"
    save_in_file(text, SIG_TOKEN_PATH+"/symmetric_overencrypt_sig_key_iv.h")
    ##
    # Save salts
    salt_auth = gen_rand_string(16)
    save_in_file(salt_auth, AUTH_TOKEN_PATH+"/salt_auth.bin")
    salt_dfu = gen_rand_string(16)
    save_in_file(salt_dfu, DFU_TOKEN_PATH+"/salt_dfu.bin")
    salt_sig = gen_rand_string(16)
    save_in_file(salt_sig, SIG_TOKEN_PATH+"/salt_sig.bin")
    # Generate random keys (for encryption and HMAC)
    # NOTE: we generate 64 bytes of key + 16 bytes of secret IV
    master_symmetric_auth_local_pet_key = gen_rand_string(64+16)
    master_symmetric_dfu_local_pet_key  = gen_rand_string(64+16)
    master_symmetric_sig_local_pet_key  = gen_rand_string(64+16)
    save_in_file(master_symmetric_auth_local_pet_key, AUTH_TOKEN_PATH+"/master_symmetric_auth_local_pet_key.bin")
    save_in_file(master_symmetric_dfu_local_pet_key, DFU_TOKEN_PATH+"/master_symmetric_dfu_local_pet_key.bin")
    save_in_file(master_symmetric_sig_local_pet_key, SIG_TOKEN_PATH+"/master_symmetric_sig_local_pet_key.bin")
    # Encrypt the local keys
    pbkdf2_iterations = 4096
    enc_master_symmetric_auth_local_pet_key = enc_local_pet_key(read_in_file(AUTH_TOKEN_PATH+"/shared_auth_petpin.bin"), read_in_file(AUTH_TOKEN_PATH+"/salt_auth.bin"), pbkdf2_iterations, master_symmetric_auth_local_pet_key)
    enc_master_symmetric_dfu_local_pet_key = enc_local_pet_key(read_in_file(DFU_TOKEN_PATH+"/shared_dfu_petpin.bin"), read_in_file(DFU_TOKEN_PATH+"/salt_dfu.bin"), pbkdf2_iterations, master_symmetric_dfu_local_pet_key)
    if USE_SIG_TOKEN == True:
        enc_master_symmetric_sig_local_pet_key = enc_local_pet_key(read_in_file(SIG_TOKEN_PATH+"/shared_sig_petpin.bin"), read_in_file(SIG_TOKEN_PATH+"/salt_sig.bin"), pbkdf2_iterations, master_symmetric_sig_local_pet_key)
    else:
        enc_master_symmetric_sig_local_pet_key = enc_local_pet_key(read_in_file(SIG_TOKEN_PATH+"/local_storage_password.bin"), read_in_file(SIG_TOKEN_PATH+"/salt_sig.bin"), pbkdf2_iterations, master_symmetric_sig_local_pet_key)
    # Save the derived keys
    save_in_file(enc_master_symmetric_auth_local_pet_key, AUTH_TOKEN_PATH+"/enc_master_symmetric_auth_local_pet_key.bin")
    save_in_file(enc_master_symmetric_dfu_local_pet_key, DFU_TOKEN_PATH+"/enc_master_symmetric_dfu_local_pet_key.bin")
    save_in_file(enc_master_symmetric_sig_local_pet_key, SIG_TOKEN_PATH+"/enc_master_symmetric_sig_local_pet_key.bin")

    #=================
    # Formatting the keys for Javacard
    ## AUTH
    sys_cmd(KEY2JAVA+" "+AUTH_TOKEN_PATH+"/token_auth_private_key.bin "+AUTH_TOKEN_PATH+"/token_auth_public_key.bin "+AUTH_TOKEN_PATH+"/platform_auth_public_key.bin "+AUTH_TOKEN_PATH+"/shared_auth_petpin.bin "+AUTH_TOKEN_PATH+"/shared_auth_petname.bin "+AUTH_TOKEN_PATH+"/shared_auth_userpin.bin "+AUTH_TOKEN_PATH+"/master_symmetric_auth_key.bin "+AUTH_TOKEN_PATH+"/enc_master_symmetric_auth_local_pet_key.bin "+" "+str(auth_max_pin_tries)+" "+" "+str(auth_max_sc_tries)+" "+AUTH_TOKEN_PATH+"/sd_pwd_auth.bin"+" "+AUTH_TOKEN_PATH+"/AUTHKeys.java auth "+PLATFORM_PROFILE)
    # In case of FIDO profile, also save the HMAC of the platform keys
    if PLATFORM_PROFILE == "u2f2":
        print("==> U2F2 profile: generating platform keys hash HMAC")
        # HMAC of SHA-256(decrypted_token_pub_key || decrypted_platform_priv_key || decrypted_platform_pub_key)
        to_hmac =  read_in_file(AUTH_TOKEN_PATH+"/token_auth_public_key.bin")
        to_hmac += read_in_file(AUTH_TOKEN_PATH+"/platform_auth_private_key.bin")
        to_hmac += read_in_file(AUTH_TOKEN_PATH+"/platform_auth_public_key.bin")
        (to_hmac, _, _) = local_sha256(to_hmac)
        # HMAC with the token FIDO secret key
        token_fido_secret_key = read_in_file(AUTH_TOKEN_PATH+"/master_symmetric_auth_key.bin")[32:]
        hm = local_hmac.new(token_fido_secret_key, digestmod=hashlib.sha256)
        hm.update(to_hmac)
        out_hmac = hm.digest()
        save_in_file(out_hmac, AUTH_TOKEN_PATH+"/FIDO/fido_hmac.bin")
        # Now generate the C header files
        KEY2C = INTERPRETER + " " + SCRIPT_PATH+"/key2c.py"
        sys_cmd(KEY2C+" "+AUTH_TOKEN_PATH+"/FIDO/fido_hmac.bin")

    # Cleanup
    sys_rm_file(AUTH_TOKEN_PATH+"/master_symmetric_auth_key.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/shared_auth_petname.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/shared_auth_userpin.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/enc_master_symmetric_auth_local_pet_key.bin")

    ## DFU
    sys_cmd(KEY2JAVA+" "+DFU_TOKEN_PATH+"/token_dfu_private_key.bin "+DFU_TOKEN_PATH+"/token_dfu_public_key.bin "+DFU_TOKEN_PATH+"/platform_dfu_public_key.bin "+DFU_TOKEN_PATH+"/shared_dfu_petpin.bin "+DFU_TOKEN_PATH+"/shared_dfu_petname.bin "+DFU_TOKEN_PATH+"/shared_dfu_userpin.bin "+DFU_TOKEN_PATH+"/master_symmetric_dfu_key.bin "+DFU_TOKEN_PATH+"/enc_master_symmetric_dfu_local_pet_key.bin "+" "+str(dfu_max_pin_tries)+" "+" "+str(dfu_max_sc_tries)+" "+"void.bin"+" "+DFU_TOKEN_PATH+"/DFUKeys.java dfu "+PLATFORM_PROFILE)
    # Cleanup
    sys_rm_file(DFU_TOKEN_PATH+"/master_symmetric_dfu_key.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/shared_dfu_petname.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/shared_dfu_userpin.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/enc_master_symmetric_dfu_local_pet_key.bin")

    ## SIG
    if USE_SIG_TOKEN == True:
        sys_cmd(KEY2JAVA+" "+SIG_TOKEN_PATH+"/token_sig_private_key.bin "+SIG_TOKEN_PATH+"/token_sig_public_key.bin "+SIG_TOKEN_PATH+"/platform_sig_public_key.bin "+SIG_TOKEN_PATH+"/shared_sig_petpin.bin "+SIG_TOKEN_PATH+"/shared_sig_petname.bin "+SIG_TOKEN_PATH+"/shared_sig_userpin.bin "+SIG_TOKEN_PATH+"/master_symmetric_sig_key.bin "+SIG_TOKEN_PATH+"/enc_master_symmetric_sig_local_pet_key.bin "+" "+str(sig_max_pin_tries)+" "+" "+str(sig_max_sc_tries)+" "+"void.bin"+" "+SIG_TOKEN_PATH+"/SIGKeys.java sig "+PLATFORM_PROFILE+" "+SIG_TOKEN_PATH+"/token_sig_firmware_private_key.bin "+SIG_TOKEN_PATH+"/token_sig_firmware_public_key.bin")
        # Cleanup
        sys_rm_file(SIG_TOKEN_PATH+"/master_symmetric_sig_key.bin")
        sys_rm_file(SIG_TOKEN_PATH+"/shared_sig_petname.bin")
        sys_rm_file(SIG_TOKEN_PATH+"/shared_sig_userpin.bin")

    #=================
    # Generate the headers
    # Data to be encrypted on the platform flash. The data is encrypted using a secret key (encrypted with PBKDF2 of
    # the PET PIN).
    # => Private and public platform keypair, public token key
    # AUTH + cleanup
    sys_cmd(ENCRYPT_PLATFORM_DATA_HEADER+" "+AUTH_TOKEN_PATH+"/shared_auth_petpin.bin "+AUTH_TOKEN_PATH+"/platform_auth_public_key.bin "+AUTH_TOKEN_PATH+"/platform_auth_private_key.bin "+AUTH_TOKEN_PATH+"/token_auth_public_key.bin "+AUTH_TOKEN_PATH+"/master_symmetric_auth_local_pet_key.bin "+AUTH_TOKEN_PATH+"/salt_auth.bin "+AUTH_TOKEN_PATH+"/encrypted_platform_auth_keys "+CURVE_NAME+" "+str(pbkdf2_iterations)+" "+" auth")
    sys_rm_file(AUTH_TOKEN_PATH+"/shared_auth_petpin.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/platform_auth_public_key.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/platform_auth_private_key.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/token_auth_public_key.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/master_symmetric_auth_local_pet_key.bin")
    sys_rm_file(AUTH_TOKEN_PATH+"/salt_auth.bin")
    # DFU + cleanup
    sys_cmd(ENCRYPT_PLATFORM_DATA_HEADER+" "+DFU_TOKEN_PATH+"/shared_dfu_petpin.bin "+DFU_TOKEN_PATH+"/platform_dfu_public_key.bin "+DFU_TOKEN_PATH+"/platform_dfu_private_key.bin "+DFU_TOKEN_PATH+"/token_dfu_public_key.bin "+DFU_TOKEN_PATH+"/master_symmetric_dfu_local_pet_key.bin "+DFU_TOKEN_PATH+"/salt_dfu.bin "+DFU_TOKEN_PATH+"/encrypted_platform_dfu_keys "+CURVE_NAME+" "+str(pbkdf2_iterations)+" "+" dfu "+SIG_TOKEN_PATH+"/token_sig_firmware_public_key.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/shared_dfu_petpin.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/platform_dfu_public_key.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/platform_dfu_private_key.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/token_dfu_public_key.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/master_symmetric_dfu_local_pet_key.bin")
    sys_rm_file(DFU_TOKEN_PATH+"/salt_dfu.bin")
    # SIG + cleanup
    if USE_SIG_TOKEN == True:
       sys_cmd(ENCRYPT_PLATFORM_DATA_HEADER+" "+SIG_TOKEN_PATH+"/shared_sig_petpin.bin "+SIG_TOKEN_PATH+"/platform_sig_public_key.bin "+SIG_TOKEN_PATH+"/platform_sig_private_key.bin "+SIG_TOKEN_PATH+"/token_sig_public_key.bin "+SIG_TOKEN_PATH+"/master_symmetric_sig_local_pet_key.bin "+SIG_TOKEN_PATH+"/salt_sig.bin "+SIG_TOKEN_PATH+"/encrypted_platform_sig_keys "+CURVE_NAME+" "+str(pbkdf2_iterations)+" "+" sig "+SIG_TOKEN_PATH+"/token_sig_firmware_public_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/shared_sig_petpin.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/platform_sig_public_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/platform_sig_private_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/token_sig_public_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/token_sig_firmware_private_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/master_symmetric_sig_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/master_symmetric_sig_local_pet_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/salt_sig.bin")
    else:
       sys_cmd(ENCRYPT_PLATFORM_DATA_HEADER+" "+SIG_TOKEN_PATH+"/local_storage_password.bin "+SIG_TOKEN_PATH+"/platform_sig_public_key.bin "+SIG_TOKEN_PATH+"/platform_sig_private_key.bin "+SIG_TOKEN_PATH+"/token_sig_public_key.bin "+SIG_TOKEN_PATH+"/master_symmetric_sig_local_pet_key.bin "+SIG_TOKEN_PATH+"/salt_sig.bin "+SIG_TOKEN_PATH+"/encrypted_platform_sig_keys "+CURVE_NAME+" "+str(pbkdf2_iterations)+" "+" sig "+SIG_TOKEN_PATH+"/token_sig_firmware_public_key.bin "+SIG_TOKEN_PATH+"/token_sig_firmware_private_key.bin "+SIG_TOKEN_PATH+"/master_symmetric_sig_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/local_storage_password.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/platform_sig_public_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/platform_sig_private_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/token_sig_public_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/token_sig_firmware_private_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/master_symmetric_sig_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/master_symmetric_sig_local_pet_key.bin")
       sys_rm_file(SIG_TOKEN_PATH+"/salt_sig.bin")
