from common_utils import *

# The partition types
partitions_types = {
    'FW1'      : 0,
    'FW2'      : 1,
    'DFU1'     : 2,
    'DFU2'     : 3,
    'SHR'      : 4,
}

# The firmware header layout
firmware_header_layout = {
    'MAGIC_OFFSET'      : 0,
    'MAGIC_SIZE'        : 4,
    #
    'TYPE_OFFSET'       : 4,
    'TYPE_SIZE'         : 4,
    #
    'VERSION_OFFSET'    : 8,
    'VERSION_SIZE'      : 4,
    #
    'LEN_OFFSET'        : 12,
    'LEN_SIZE'          : 4,
    #
    'SIGLEN_OFFSET'     : 16,
    'SIGLEN_SIZE'       : 4,
    #
    'CHUNKSIZE_OFFSET'  : 20,
    'CHUNKSIZE_SIZE'    : 4,
    #
    'IV_OFFSET'         : 24,
    'IV_SIZE'           : 16,
    #
    'HMAC_OFFSET'       : 40,
    'HMAC_SIZE'         : 32,
    #
    'SIG_OFFSET'        : 72,
}

# Infer from the size of the local key bag if we use a SIG token or not
# [RB] FIXME: this is a bit hardcoded, we should use a more flexible way of dealing
# with this.
def is_sig_token_used(encrypted_platform_bin_file):
    data = read_in_file(encrypted_platform_bin_file)
    if(len(data) > 400):
        return False
    else:
        return True

